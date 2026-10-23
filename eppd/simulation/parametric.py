"""Parametric study runner with database integration.

This module provides simple functions for executing parametric
studies with automatic database tracking of results.

For creating parameter grids (Cartesian products), use the crosspar()
function from eppd.utils.
"""

import sqlite3
import shutil
from pathlib import Path
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import numpy as np
from tqdm import tqdm

from ..core import read_idf, Idfpd
from ..postprocess import read_xml
from ..logger import get_logger
from .runner import _setup_simulation_dir, _run_energyplus, _validate_energyplus_location

logger = get_logger(__name__)


def setup_param_db(
    database_path: str | Path,
    params: pd.DataFrame,
) -> None:
    """Create or recreate database with parameter combinations.

    This function sets up a SQLite database for parametric studies.
    The table is replaced each time this function is called.

    Args:
        database_path: Path to SQLite database file (will be created/replaced)
        params: DataFrame with parameter combinations

    Required columns in params DataFrame:
        - idffile: Path to baseline IDF file
        - weather: Path to weather file (.epw)
        - Additional parameter columns and output columns as needed

    Optional columns:
        - runid: Unique identifier for each run (int, str, UUID, etc.)
                 If not provided, will be auto-generated from DataFrame index (starting at 1)

    Note:
        The 'run' column is automatically added (0 = pending, 1 = completed, -1 = failed).
        Any output columns should be pre-defined in the params DataFrame.

    Example:
        >>> import pandas as pd
        >>> from eppd.utils import crosspar
        >>> import numpy as np
        >>>
        >>> # Create parameter combinations using crosspar
        >>> lpd_values = pd.DataFrame({'lpd': [10, 12, 14, 16]})
        >>> wall_r = pd.DataFrame({'wall_r': [15, 20, 25]})
        >>> params = crosspar([lpd_values, wall_r])
        >>>
        >>> # Add required columns
        >>> params['idffile'] = 'baseline.idf'
        >>> params['weather'] = 'Chicago.epw'
        >>>
        >>> # Add output columns you expect (set to np.nan)
        >>> for col in ['Heating_Electricity', 'Cooling_Electricity', 'EUI']:
        ...     params[col] = np.nan
        >>>
        >>> # runid will be auto-generated from index (1, 2, 3, ...)
        >>> setup_param_db('study.db', params)

    Note:
        To restart interrupted simulations, just call run_parametric() again.
        Only use setup_param_db() again if you need to modify the parameters or
        reset the database.
    """
    database_path = Path(database_path)

    # Check if database already exists - skip if it does
    if database_path.exists():
        print(f"ℹ Database already exists: {database_path} (skipping setup)")
        return

    # Make a copy to avoid modifying the original
    params = params.copy()

    print(f"Setting up database: {database_path}")

    # Generate runid from index if not provided
    if "runid" not in params.columns:
        params["runid"] = list(params.index + 1)

    # Validate required columns explicitly
    if "idffile" not in params.columns:
        raise ValueError(
            "Idf file column missing, specify Idf file for run in a column named 'idffile'\n"
        )

    if "weather" not in params.columns:
        raise ValueError(
            "Weather file column missing, specify weather file for run in a column named 'weather'\n"
        )

    # Add 'run' column (0 = pending, 1 = completed, -1 = failed)
    params["run"] = 0

    # Create database and write parameters
    conn = sqlite3.connect(database_path)
    params.to_sql("pr", conn, if_exists="replace", index=False)
    conn.close()

    pending_count = (params["run"] == 0).sum()
    completed_count = (params["run"] == 1).sum()

    print(
        f"Database created: {len(params)} total cases ({pending_count} pending, {completed_count} completed)"
    )


def run_parametric(
    database_path: str | Path,
    param_mapping: dict,
    max_runs: int = 5,
    batch_size: int = 20,
    output_parser: str | Callable | list[str | Callable] | None = None,
) -> None:
    """Run parametric simulations from database.

    This function processes pending cases from the database, applies parameter
    values to the baseline IDF model, runs simulations, and stores results.
    Can be called multiple times on the same database to restart/continue.

    After all simulations complete, use runs_to_parquet() to export results:
        >>> import pandas as pd
        >>> from eppd.utils import runs_to_parquet
        >>> runs_to_parquet('study.db')
        >>> results = pd.read_parquet('study.parquet')

    Args:
        database_path: Path to SQLite database file (created by setup_database)
        param_mapping: Dictionary mapping database columns to IDF model indices.
                      Keys are column names from the database. Values are IDF indices.
                      Only database columns present as keys will be applied; other
                      columns are ignored (useful for output columns).
        max_runs: Maximum parallel simulations (default: 5)
        batch_size: Cases per batch before persisting (default: 100)
        output_parser: Method(s) to extract outputs from Xmlpd. Can be:
                      - String: method name like 'get_standard_results' (default)
                      - Callable: function that takes Xmlpd and returns pd.Series
                      - List: multiple methods/callables to combine results
                      Must match the parser used in setup_param_db()

    Parameter mapping format:
        Dictionary where each key is a database column name and value is an IDF index.
        IDF index can be:
        - ('object_type', 'object_name', param_index)
        - ('object_type', slice(None), param_index)  # All objects of type

    Example:
        >>> # First setup the database
        >>> setup_param_db('study.db', params)
        >>>
        >>> # Define how database columns map to IDF parameters
        >>> param_mapping = {
        ...     'lpd': ('lights', slice(None), 5),  # All lights, param 5
        ...     'wall_r': ('material', 'wall_insul', 3),  # Specific material
        ...     'window_u': ('windowmaterial:simpleglazingsystem', slice(None), 1)
        ... }
        >>>
        >>> # Run all pending simulations (uses default parser)
        >>> run_parametric('study.db', param_mapping)
        >>>
        >>> # Use custom parser (must match what was used in setup_database)
        >>> run_parametric('study.db', param_mapping, output_parser='get_prm')
        >>>
        >>> # If interrupted, just call again - it continues where it left off
        >>> run_parametric('study.db', param_mapping)
    """
    database_path = Path(database_path)

    # Check database exists
    if not database_path.exists():
        raise FileNotFoundError(
            f"Database not found: {database_path}\n"
            f"Create it first using setup_param_db()"
        )

    # Fail fast on misconfigured EnergyPlus path before spawning threads
    _validate_energyplus_location()

    # Set default output parser if not specified
    if output_parser is None:
        output_parser = "get_standard_results"

    # Normalize output_parser to a list
    if not isinstance(output_parser, list):
        parsers = [output_parser]
    else:
        parsers = output_parser

    # Validate param_mapping against database columns
    # timeout=30 allows SQLite to retry if database is locked (e.g., after interrupt)
    conn = sqlite3.connect(database_path, timeout=30)

    # Get initial counts
    pending_count = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM pr WHERE run = 0", conn
    )["count"].iloc[0]

    completed_count = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM pr WHERE run = 1", conn
    )["count"].iloc[0]

    try:
        if pending_count == 0:
            print("No pending cases to run")
            return

        print(
            f"Starting parametric study with {max_runs} parallel runs: {pending_count} pending, {completed_count} completed"
        )

        runs_completed = completed_count

        # Create overall progress bar for all runs
        overall_pbar = tqdm(
            total=pending_count + completed_count,
            desc="Overall Progress",
            unit="run",
            bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} runs [{elapsed}<{remaining}]",
        )

        # Update progress bar to reflect already-completed runs
        overall_pbar.update(completed_count)


        while True:
            # Get next batch of pending runs grouped by idffile
            # This ensures all cases in a batch use the same IDF file
            query = (
                "SELECT * FROM pr "
                "WHERE (idffile, run) IN "
                "(SELECT idffile, run FROM pr WHERE run = 0 LIMIT 1) "
                "AND run = 0 "
                "LIMIT ?"
            )

            cases = pd.read_sql_query(query, conn, params=(batch_size,))

            if len(cases) == 0:
                break

            # Get the IDF file for this batch (all cases use the same file)
            baseline_idf = cases["idffile"].iloc[0]

            # Load baseline IDF
            try:
                baseline_model = read_idf(baseline_idf)
            except Exception as e:
                overall_pbar.close()
                raise SystemExit(
                    f"\nParametric run stopped: failed to load IDF file '{baseline_idf}'.\n"
                    f"Fix the issue and re-run — completed runs will be skipped automatically.\n"
                    f"Cause: {e}"
                )


            # Run batch with thread pool
            with ThreadPoolExecutor(max_workers=max_runs) as executor:
                futures = []

                for idx, row in cases.iterrows():
                    future = executor.submit(
                        _run_parametric_case,
                        baseline_model,
                        row,
                        param_mapping,
                        parsers,
                    )
                    futures.append((future, row["runid"]))

                # Collect results and update database
                for future, runid in futures:
                    try:
                        results = future.result()

                        # Column names come from results.index (internally controlled);
                        # values and runid are bound as parameters so any sqlite3-supported
                        # type works (int, str, UUID-as-str, etc.) and quoting is automatic.
                        result_cols = ",".join(results.index)
                        placeholders = ",".join(["?"] * len(results))
                        update_query = (
                            f"UPDATE pr SET ({result_cols}, run) = ({placeholders}, 1) "
                            f"WHERE runid = ?"
                        )

                        conn.execute(update_query, [*results.values, runid])
                        runs_completed += 1
                        overall_pbar.update(1)

                    except Exception as e:
                        overall_pbar.close()
                        executor.shutdown(wait=False, cancel_futures=True)
                        raise SystemExit(
                            f"\nParametric run stopped: run {runid} failed.\n"
                            f"Fix the issue and re-run — completed runs will be skipped automatically.\n"
                            f"Cause: {e}"
                        )

                conn.commit()

        overall_pbar.close()

        # Get final counts
        total_completed = completed_count + runs_completed
        total_cases = pd.read_sql_query("SELECT COUNT(*) as count FROM pr", conn)[
            "count"
        ].iloc[0]

        print(
            f"Parametric study complete: {runs_completed} new runs finished ({total_completed}/{total_cases} total completed)"
        )

    finally:
        # Always close connection, even if interrupted (Ctrl+C)
        conn.close()


def _run_parametric_case(
    baseline_model: Idfpd,
    params: pd.Series,
    param_mapping: dict,
    parsers: list[str | Callable],
) -> pd.Series | None:
    """Run single parametric case (internal helper function).

    Uses lower-level simulation functions for better performance:
    - Skips full run_simulation verification overhead
    - Creates temporary simulation directory
    - Runs EnergyPlus directly
    - Parses outputs and cleans up immediately

    Args:
        baseline_model: Baseline IDF model
        params: Parameter values for this case
        param_mapping: Dictionary mapping database columns to IDF indices.
                      Only keys present in param_mapping are applied.
        parsers: List of parser specifications (strings or callables)

    Returns:
        Series of results or None if failed
    """
    runid = params["runid"]
    weather = params["weather"]
    sim_dir = None
    keep_dir = False

    try:
        # Create modified model
        model = baseline_model.copy()

        # get columns with paramters that not empty and have a parameter mapping
        params_mapped = params.dropna().index.intersection(param_mapping)
#        params_mapped = params

        # assign parameters to idf model.
        for par in list(params_mapped):
            model[param_mapping[par]] = params[par]

        # Create temporary simulation directory
        sim_dir = Path(f".parametric_run_{runid}")
        sim_dir.mkdir(parents=True, exist_ok=True)

        # Write modified IDF to temp directory
        temp_idf = sim_dir / "model.idf"
        model.write_idf(temp_idf)

        # Setup simulation directory (copies IDD and weather file)
        _setup_simulation_dir(sim_dir, temp_idf, Path(weather))

        # Run EnergyPlus directly (no overhead)
        success = _run_energyplus(sim_dir, 3600)  # 1 hour timeout

        if not success:
            keep_dir = True
            raise RuntimeError(f"EnergyPlus simulation failed for '{sim_dir}' — check the .err file in that directory for details")

        # Check for XML output
        xml_path = sim_dir / "eplustbl.xml"
        if not xml_path.exists():
            keep_dir = True
            raise RuntimeError(f"EnergyPlus ran but produced no XML output — check the .err file in '{sim_dir}' for details")

        # Parse results using specified parser(s)
        xml_parser = read_xml(xml_path)

        # Collect outputs from all specified parsers
        combined_results = pd.Series(dtype=float)
        for parser_spec in parsers:
            if isinstance(parser_spec, str):
                # String method name - call method on Xmlpd
                parser_output = getattr(xml_parser, parser_spec)()
            elif callable(parser_spec):
                # Callable function - call with Xmlpd as argument
                parser_output = parser_spec(xml_parser)
            else:
                raise TypeError(
                    f"output_parser must be string or callable, got {type(parser_spec)}"
                )

                # Combine results
            combined_results = pd.concat([combined_results, parser_output])
        #        return combined_results
        required_columns = combined_results.index.intersection(params.index)
        return combined_results[required_columns]

    finally:
        # Keep simulation directory on failure so the user can inspect the .err file
        if sim_dir and sim_dir.exists() and not keep_dir:
            shutil.rmtree(sim_dir, ignore_errors=True)


def runs_to_parquet(
    database_path: str | Path,
    delete_db: bool = False,
) -> Path:
    """Export completed runs from parametric study database to parquet file.

    Converts completed runs from a SQLite database to parquet format.
    Only completed runs (run=1) are exported. If incomplete runs exist,
    deletion of the database is prevented.

    Args:
        database_path: Path to SQLite database file (created by setup_param_db)
        delete_db: If True, delete the original database file after export.
                   Deletion is prevented if incomplete runs exist (default: False)

    Returns:
        Path to the exported parquet file

    Raises:
        FileNotFoundError: If database file doesn't exist
        ModuleNotFoundError: If pyarrow is not installed

    Example:
        >>> from eppd import runs_to_parquet
        >>> import pandas as pd
        >>>
        >>> # Export completed runs to parquet
        >>> parquet_path = runs_to_parquet('study.db')
        >>>
        >>> # Load results (only completed runs)
        >>> results = pd.read_parquet(parquet_path)
        >>> print(results[['runid', 'EUI', 'Heating_Electricity']])
        >>>
        >>> # Export and clean up database (only if all runs completed)
        >>> parquet_path = runs_to_parquet('study.db', delete_db=True)
    """
    database_path = Path(database_path)

    if not database_path.exists():
        raise SystemExit(f"Database not found: {database_path}")

    conn = sqlite3.connect(database_path)

    completed_count = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM pr WHERE run = 1", conn
    )["count"].iloc[0]

    incomplete_count = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM pr WHERE run != 1", conn
    )["count"].iloc[0]

    if incomplete_count > 0:
        print(
            f"Warning: {incomplete_count} run(s) incomplete, "
            f"{completed_count} run(s) completed. "
            f"Database will not be deleted."
        )
        delete_db = False

    try:
        import pyarrow  # noqa: F401

        results_df = pd.read_sql_query("SELECT * FROM pr WHERE run = 1", conn)
        parquet_path = database_path.with_suffix(".parquet")
        results_df.to_parquet(parquet_path, index=False, engine="pyarrow")
        conn.close()

        if completed_count > 0:
            print(f"Exported {completed_count} completed run(s) to {parquet_path.name}")

    except ModuleNotFoundError:
        conn.close()
        raise SystemExit(
            "Cannot export to parquet: pyarrow not installed. "
            "Install with: pip install pyarrow"
        )
    except Exception as e:
        conn.close()
        raise SystemExit(f"Failed to export to parquet: {e}")

    if delete_db:
        try:
            database_path.unlink()
            print(f"Deleted database: {database_path.name}")
        except Exception as e:
            raise SystemExit(f"Failed to delete database: {e}")

    return parquet_path

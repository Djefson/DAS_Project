"""Batch simulation runner for multiple IDF files.

This module provides simple functions for executing multiple
EnergyPlus simulations in parallel.
"""

import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..logger import get_logger
from .runner import (
    _setup_simulation_dir,
    _run_energyplus,
    _collect_outputs,
    _cleanup,
    _validate_energyplus_location,
)

logger = get_logger(__name__)


def run_batch(
    runs: dict[str, tuple[str | Path, str | Path]],
    max_runs: int = 5,
    remove_temp_files: bool = True,
) -> None:
    """Run batch of EnergyPlus simulations in parallel.

    Executes multiple simulations using a thread pool with configurable
    parallelism and automatic error handling. Results are logged to console.

    Args:
        runs: Dict mapping run names to (idf_file, weather_file) tuples
              The run name will be used as the output directory name
        max_runs: Maximum parallel simulations (default: 5)
        remove_temp_files: Whether to delete temp directories after runs

    Example:
        >>> from eppd.simulation import run_batch
        >>>
        >>> # Define multiple simulations
        >>> runs = {
        ...     'baseline': ('baseline.idf', 'Chicago.epw'),
        ...     'improved': ('improved.idf', 'Chicago.epw'),
        ...     'optimal': ('optimal.idf', 'Chicago.epw'),
        ... }
        >>>
        >>> # Run all simulations in parallel
        >>> run_batch(runs, max_runs=4)
        >>> # Output files are copied to: baseline.eso, baseline_Table.xml, etc.
    """

    # Fail fast on misconfigured EnergyPlus path before spawning threads
    _validate_energyplus_location()

    logger.info(
        f"Starting batch of {len(runs)} simulations with {max_runs} parallel runs"
    )

    with ThreadPoolExecutor(max_workers=max_runs) as executor:
        # Submit all simulation jobs
        futures = {}

        for run_name, (idf_file, weather_file) in runs.items():
            future = executor.submit(
                _run_batch_case,
                idf_file=idf_file,
                weather_file=weather_file,
                output_dir=Path(run_name),
                remove_temp_files=remove_temp_files,
            )
            futures[future] = run_name

        # Wait for all to complete; raise immediately on first failure
        for future in as_completed(futures):
            run_name = futures[future]

            try:
                future.result()
            except Exception as e:
                executor.shutdown(wait=False, cancel_futures=True)
                raise SystemExit(
                    f"\nBatch run stopped: simulation '{run_name}' failed.\n"
                    f"Fix the issue and re-run.\n"
                    f"Cause: {e}"
                )

    logger.info(f"Batch complete: {len(runs)} simulations finished")


def _run_batch_case(
    idf_file: str | Path,
    weather_file: str | Path,
    output_dir: str | Path,
    remove_temp_files: bool = True,
    timeout: int = 3600,
) -> None:
    """Run a single EnergyPlus simulation (internal helper).

    Args:
        idf_file: Path to IDF file
        weather_file: Path to EPW weather file
        output_dir: Directory for simulation outputs
        remove_temp_files: Whether to delete temp files after run (default: True)
        timeout: Maximum simulation time in seconds (default: 3600 = 1 hour)
    """
    idf_file = Path(idf_file)
    weather_file = Path(weather_file)
    output_dir = Path(output_dir)

    # Validate input files
    if not idf_file.exists():
        raise FileNotFoundError(f"IDF file not found: {idf_file}")

    if not weather_file.exists():
        raise FileNotFoundError(f"Weather file not found: {weather_file}")




    logger.info(f"Starting simulation: {output_dir.name}")
    logger.debug(f"IDF: {idf_file}, Weather: {weather_file}")

    try:

        # Delete previous results
        pfiles = (idf_file.with_suffix(ea) for ea in ('.xml','.html','.eso','.err'))
#        [p.unlink() for p in pfiles if p.is_file()]
        for p in pfiles:
            if p.is_file(): p.unlink() 

        # Setup simulation directory (will fail if EnergyPlus not configured)
        _setup_simulation_dir(output_dir, idf_file, weather_file)

        # Run EnergyPlus
        success = _run_energyplus(output_dir, timeout)

        # Collect outputs
        _collect_outputs(output_dir)

        # Cleanup if requested
        if remove_temp_files and success:
            _cleanup(output_dir)

        if success:
            logger.info(f"Simulation completed: {output_dir.name}")
        else:
            raise RuntimeError(
                f"EnergyPlus simulation failed for '{output_dir.name}' — check the IDF and .err file for errors"
            )

    except subprocess.TimeoutExpired:
        error_msg = f"Simulation '{output_dir.name}' timed out after {timeout} seconds"
        logger.error(error_msg)
        raise TimeoutError(error_msg)

    except Exception as e:
        logger.error(f"Simulation failed: {output_dir.name} - {e}")
        raise RuntimeError(
            f"Simulation '{output_dir.name}' failed: {e}"
        ) from e

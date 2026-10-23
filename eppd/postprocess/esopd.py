"""ESO file reader for hourly EnergyPlus outputs.

This module parses EnergyPlus ESO (EnergyPlus Standard Output) files
containing hourly simulation results.

Example:
    Simple function-based API:
        >>> from eppd.postprocess import read_eso
        >>> eso = read_eso('eplusout.eso')
        >>> zone_temps = eso.data.loc[:, ('Core', 'Zone Mean Air Temperature')]

    Class-based API (for multiple operations):
        >>> from eppd.postprocess import Esopd
        >>> eso = Esopd('eplusout.eso')
        >>> hourly_data = eso.data
"""

import re
import io
from pathlib import Path
import pandas as pd
import numpy as np

from ..logger import get_logger

logger = get_logger(__name__)


class Esopd:
    """Reader for EnergyPlus ESO hourly output files.

    Parses ESO format and stores DataFrame with datetime index
    and multi-level columns (zone, variable).

    Example:
        >>> eso = Esopd('eplusout.eso')
        >>> zone_temps = eso.data.loc[:, ('Core', 'Zone Mean Air Temperature')]
    """

    def __init__(self, filepath: str | Path, year: int = 2012):
        """Initialize ESO reader and load data.

        Args:
            filepath: Path to eplusout.eso file
            year: Year to use for datetime index (default: 2012, a leap year)

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If parsing fails
        """
        self.filepath = Path(filepath)
        self.year = year

        if not self.filepath.exists():
            raise SystemExit(f"ESO file not found: {self.filepath}")

        logger.debug(f"Initialized ESO reader for: {self.filepath.name}")

        # Read data immediately
        self.data = self._read()

    def _read(self) -> pd.DataFrame:
        """Read and parse ESO file (internal method).

        Returns:
            DataFrame with datetime index and (zone, variable) multi-columns

        Raises:
            ValueError: If parsing fails
        """
        logger.debug(f"Reading ESO file: {self.filepath.name}")

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Split into header and data sections
            sections = content.split("End of")

            if len(sections) < 3:
                raise ValueError("ESO file format invalid - expected 'End of' markers")

            header_section = sections[0]
            data_section = sections[1]

            # Parse column definitions from header
            columns = self._parse_header(header_section)

            # Parse data section
            dataframe = self._parse_data(data_section, columns, self.year)

            logger.debug(
                f"Successfully read ESO: {len(dataframe)} timesteps, "
                f"{len(dataframe.columns)} variables"
            )

            return dataframe

        except Exception as e:
            raise ValueError(f"Failed to read ESO file {self.filepath}: {e}") from e

    def _parse_header(self, header: str) -> pd.DataFrame:
        """Parse ESO header section to get column definitions.

        Args:
            header: Header section string

        Returns:
            DataFrame with column number, zone name, and variable name
        """
        # Skip first few lines based on whether calendar year is present
        skip_rows = 6 + int("Calendar Year" in header)

        try:
            cols = pd.read_csv(
                io.StringIO(header),
                skiprows=skip_rows,
                header=None,
                names=["n", "zone", "value"],
            )

            # Extract variable name (before the units in brackets)
            cols["value"] = cols["value"].str.split(r" \[", expand=True)[0]

            logger.debug(f"Parsed {len(cols)} column definitions from header")

            return cols

        except Exception as e:
            raise ValueError(f"Failed to parse ESO header: {e}") from e

    def _parse_data(
        self, data_section: str, columns: pd.DataFrame, year: int = 2012
    ) -> pd.DataFrame:
        """Parse ESO data section.

        Args:
            data_section: Data section string
            columns: Column definitions from header
            year: Year to use for datetime index (default: 2012, a leap year that starts on Sunday)

        Returns:
            DataFrame with datetime index and parsed data
        """
        # Extract timestamp information from data lines (lines starting with '2,')
        # Format: 2, month, day, hour, minute, ...
        timestamp_pattern = (
            r"2,[ 0-9]*,([ 0-9]*),([ 0-9]*),"
            r"[ 0-1]*,([ 0-9]*),([ 0-9.]*),[ 0-9.]*,[A-Za-z]*"
        )

        try:
            timestamps = re.findall(timestamp_pattern, data_section)

            if not timestamps:
                raise ValueError("No timestamp data found in ESO file")

            # Convert to DataFrame
            ts_df = pd.DataFrame(timestamps, dtype=np.float64).astype(int)

            # Create datetime index
            # Use specified year (default 2012, a leap year) to handle full 8760 hours
            ts_df.columns = ["month", "day", "hour", "minute"]
            ts_df["year"] = year
            datetimes = pd.to_datetime(
                ts_df[["year", "month", "day", "hour", "minute"]]
            )

            # Read actual data values
            # Remove timestamp lines, skip initial header rows
            data_clean = re.sub(r"^2,.*\n", "", data_section, flags=re.MULTILINE)

            eso_data = pd.read_csv(
                io.StringIO(data_clean),
                skiprows=2,
                header=None,
                dtype=np.float64,
                low_memory=False,
            )

            # Add hour counter for unstacking
            eso_data["hrs"] = eso_data.groupby(0).cumcount()

            # Reshape to wide format
            eso_wide = eso_data.set_index(["hrs", 0]).unstack()

            # Set datetime index
            eso_wide.index = datetimes

            # Set proper column names from header
            col_numbers = eso_wide.columns.get_level_values(0).astype(int)
            column_info = columns.loc[col_numbers, ["value", "zone"]].values.T

            eso_wide.columns = pd.MultiIndex.from_arrays(column_info)

            # Sort columns for easier access
            eso_wide = eso_wide.sort_index(axis=1)

            return eso_wide

        except Exception as e:
            raise ValueError(f"Failed to parse ESO data section: {e}") from e


def changepoint_fit(X: np.ndarray, Y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    r"""Fit a changepoint model to energy data for calibrated simulation.

    Fits a 5-parameter piecewise linear model with heating and cooling slopes:

        (xht_top,yht_top)                (xcl_top,ycl_top)
                        \              /
                         \            /
                          \__________/
          (xht_base,y_base)          (xcl_base,y_base)

    Inspired by: https://stackoverflow.com/a/70712007
    Retrieved 2026-02-08, License - CC BY-SA 4.0

    Args:
        X: Outdoor air drybulb temperatures (numpy array)
        Y: Energy usage values (numpy array)

    Returns:
        Tuple of (x_points, y_points) arrays defining the changepoint model:
            - x_points: [xht_top, xht_base, xcl_base, xcl_top]
            - y_points: [yht_top, y_base, y_base, ycl_top]

    Raises:
        ImportError: If scipy is not installed

    Example:
        >>> temps = np.array([0, 10, 20, 30, 40])
        >>> energy = np.array([100, 80, 50, 60, 90])
        >>> x_pts, y_pts = changepoint_fit(temps, energy)
        >>> # Use np.interp(temps, x_pts, y_pts) for predictions
    """
    # Lazy import - only required if using this function
    try:
        from scipy import optimize
    except ImportError as e:
        raise ImportError(
            "scipy is required for changepoint_fit. Install it with: pip install scipy"
        ) from e

    # Find initial guesses from extreme points
    xmin_ht_i = X.argmin()
    xmax_cl_i = X.argmax()

    xht_top = X[xmin_ht_i]
    yht_top = Y[xmin_ht_i]

    xcl_top = X[xmax_cl_i]
    ycl_top = Y[xmax_cl_i]

    # Initial guesses for base points (deadband region)
    xht_base, xcl_base = np.quantile([xht_top, xcl_top], [0.3, 0.6])
    y_base = np.quantile(Y, 0.5)

    def xyfunc(p):
        """Convert parameter vector to x,y point arrays."""
        xht_top, xht_base, xcl_base, xcl_top, y_base = p
        px = [xht_top, xht_base, xcl_base, xcl_top]
        py = [yht_top, y_base, y_base, ycl_top]
        return px, py

    def err(p):
        """Mean squared error between model and data."""
        px, py = xyfunc(p)
        Y2 = np.interp(X, px, py)
        return np.mean((Y - Y2) ** 2)

    # Optimize changepoint parameters
    r = optimize.minimize(
        err, x0=[xht_top, xht_base, xcl_base, xcl_top, y_base], method="Nelder-Mead"
    )

    return xyfunc(r.x)


def read_eso(filepath: str | Path, year: int = 2012) -> "Esopd":
    """Read and parse EnergyPlus ESO output file.
    Note: this will work only if all outputs have the same output interval
          and EnergyPlus is not run during sizingperiods.

    Args:
        filepath: Path to eplusout.eso file
        year: Year to use for datetime index (default: 2012, a leap year)

    Returns:
        Esopd: Reader instance with data already loaded in the .data attribute

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file cannot be parsed

    Example:
        >>> from eppd.postprocess import read_eso
        >>> eso = read_eso('eplusout.eso')
        >>> hourly_data = eso.data
        >>>
        >>> # Access specific zone temperature
        >>> core_temp = eso.data.loc[:, ('Core', 'Zone Mean Air Temperature')]
        >>>
        >>> # Access all zones for one variable
        >>> all_temps = eso.data.loc[:, (slice(None), 'Zone Mean Air Temperature')]
        >>>
        >>> # Daily averages
        >>> daily_avg = eso.data.resample('D').mean()
    """
    return Esopd(filepath, year)

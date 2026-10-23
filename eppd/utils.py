"""Generic utility functions for DataFrame manipulation.

This module provides helper functions for working with pandas DataFrames,
particularly useful for parametric studies and data cleaning.
"""

import re
import subprocess
from pathlib import Path

import pandas as pd
from types import SimpleNamespace
from .config import energyplus_config

from .postprocess import read_xml, read_eso


def joinpar(lst):
    """Join list of pandas DataFrames by concatenation.

    Concatenates DataFrames vertically (stacking rows).
    Useful for combining parameter lists from multiple sources.

    Args:
        lst: List of DataFrames to concatenate

    Returns:
        Single DataFrame with all rows from input DataFrames

    Example:
        >>> import pandas as pd
        >>> from eppd.utils import joinpar
        >>>
        >>> # Create parameter DataFrames
        >>> lpd_list = pd.DataFrame({'lpd': [0.8, 1.0, 1.2]})
        >>> fan_list = pd.DataFrame({'lpd': [1.5, 2.0]})
        >>>
        >>> # Join them
        >>> combined = joinpar([lpd_list, fan_list])
        >>> # Result has 5 rows (3 + 2)
        >>> print(combined)
        #    lpd
        # 0  0.8
        # 1  1.0
        # 2  1.2
        # 0  1.5
        # 1  2.0
    """
    return pd.concat(lst)


def crosspar(lst):
    """Join list of pandas DataFrames using cross merge (Cartesian product).

    Creates all combinations of rows from the input DataFrames.
    Useful for creating parametric study combinations.

    Args:
        lst: List of DataFrames to merge

    Returns:
        Single DataFrame with all combinations (Cartesian product)

    Example:
        >>> import pandas as pd
        >>> from eppd.utils import crosspar
        >>>
        >>> # Create parameter DataFrames
        >>> lpd_values = pd.DataFrame({'lpd': [0.8, 1.0, 1.2]})
        >>> fan_static = pd.DataFrame({'static': [2.5, 3.0, 3.5]})
        >>>
        >>> # Get all combinations
        >>> combinations = crosspar([lpd_values, fan_static])
        >>> # Result has 9 rows (3 × 3 combinations)
        >>> print(combinations)
        #    lpd  static
        # 0  0.8     2.5
        # 1  0.8     3.0
        # 2  0.8     3.5
        # 3  1.0     2.5
        # 4  1.0     3.0
        # 5  1.0     3.5
        # 6  1.2     2.5
        # 7  1.2     3.0
        # 8  1.2     3.5
    """
    f, *r = lst
    for ea in r:
        f = f.merge(ea, how="cross")
    return f


def trimrows(df):
    """Remove rows that are all NaN/False/0/empty.

    Args:
        df: DataFrame to trim

    Returns:
        DataFrame with empty rows removed

    Example:
        >>> import pandas as pd
        >>> from eppd.utils import trimrows
        >>>
        >>> df = pd.DataFrame({
        ...     'A': [1, 0, 3],
        ...     'B': [4, 0, 6]
        ... })
        >>> trimmed = trimrows(df)
        >>> # Row 1 (all zeros) is removed
    """
    return df.loc[df.any(axis=1), :]


def trimcols(df):
    """Remove columns that are all NaN/False/0/empty.

    Args:
        df: DataFrame to trim

    Returns:
        DataFrame with empty columns removed

    Example:
        >>> import pandas as pd
        >>> from eppd.utils import trimcols
        >>>
        >>> df = pd.DataFrame({
        ...     'A': [1, 2, 3],
        ...     'B': [0, 0, 0],
        ...     'C': [4, 5, 6]
        ... })
        >>> trimmed = trimcols(df)
        >>> # Column B (all zeros) is removed
    """
    return df.loc[:, df.any()]


def trimdf(df):
    """Remove both rows and columns that are all NaN/False/0/empty.

    Args:
        df: DataFrame to trim

    Returns:
        DataFrame with empty rows and columns removed

    Example:
        >>> import pandas as pd
        >>> from eppd.utils import trimdf
        >>>
        >>> df = pd.DataFrame({
        ...     'A': [1, 0, 3, 0],
        ...     'B': [0, 0, 0, 0],
        ...     'C': [4, 0, 6, 0]
        ... })
        >>> trimmed = trimdf(df)
        >>> # Row 1 and 3 (all zeros) and Column B (all zeros) are removed
    """
    return df.loc[df.any(axis=1), df.any()]


def pct_savings(df, col):
    """Calculate percentage savings relative to a baseline column.

    Computes percentage savings for each column in the DataFrame relative
    to a baseline (reference) column. Result = (1 - value/baseline) * 100.

    Args:
        df: DataFrame with numeric columns to compare
        col: Series or column to use as baseline reference

    Returns:
        DataFrame with percentage savings for each column

    Example:
        >>> import pandas as pd
        >>> from eppd.utils import pct_savings
        >>>
        >>> df = pd.DataFrame({
        ...     'baseline': [100, 200, 300],
        ...     'option_a': [80, 150, 250],
        ...     'option_b': [90, 180, 270]
        ... })
        >>> baseline_col = df['baseline']
        >>> savings = pct_savings(df, baseline_col)
        >>> # Shows percentage reduction relative to baseline
    """
    try:
        df = df.drop(col.name, axis=1)
    except (KeyError, AttributeError):
        # col.name doesn't exist or col has no name attribute - continue
        pass
    return (1 - trimdf(df.divide(col, axis="index"))) * 100



def upgrade_idf(idf_paths):
    """Upgrade one or more IDF files to the latest EnergyPlus version.

    Runs all available Transition executables in version order from the
    IDFVersionUpdater directory. Each transition program handles its own
    version check — files already at or beyond a transition's target version
    are passed through unchanged.

    Requires energyplus_config.energyplus_location to be set to the
    EnergyPlus executable (e.g. /usr/local/EnergyPlus-25-2-0/energyplus).

    Args:
        idf_paths: Path or list of Paths to IDF files to upgrade (modified in place)

    Example:
        >>> from eppd.utils import upgrade_idf
        >>> upgrade_idf(["model_a.idf", "model_b.idf"])
    """
    import os

#    ep_dir = os.environ.get("energyplus_config")
    ep_exe = energyplus_config.energyplus_location
    if ep_exe is None:
        raise EnvironmentError("energyplus_config.energyplus_location is not set.")

    if isinstance(idf_paths, (str, Path)):
        idf_paths = [idf_paths]

    updater_dir = Path(ep_exe).parent / "PreProcess" / "IDFVersionUpdater"

    def _version_key(p):
        m = re.match(r"Transition-V(\d+)-(\d+)-(\d+)-to-", p.name)
        return tuple(int(x) for x in m.groups()) if m else (0, 0, 0)

    transitions = sorted(updater_dir.glob("Transition-V*"), key=_version_key)
    for idf_path in idf_paths:
        idf_path = Path(idf_path).resolve()
        for transition in transitions:
            subprocess.call([str(transition), str(idf_path)], cwd=str(updater_dir))


def get_batch_eso(cases):
    """Load ESO results for a list of batch run cases.

    Args:
        cases: List of case name strings (without extension). Each case expects
               a .eso file in the current directory.

    Returns:
        SimpleNamespace with attributes:
            esosum      — dict mapping case name to Series of summed ESO data by variable
            <case_name> — DataFrame of ESO interval data per case
    """
    eso = SimpleNamespace(
        esosum={},
    )

    for case_name in cases:
        eso_path = Path(case_name + ".eso")
        intdat = read_eso(eso_path).data
        setattr(eso, case_name, intdat)
        eso.esosum[case_name] = intdat.sum().groupby(level=0).sum()
    return eso


def get_batch_xml(cases):
    """Load XML results for a list of batch run cases.

    Args:
        cases: List of case name strings (without extension). Each case expects
               a .xml file in the current directory. Missing files are skipped
               with a printed warning.

    Returns:
        SimpleNamespace with attributes:
            elec, gas, distcl, disthw, distst — DataFrames of PRM end-use energy by case
            eui          — Series of site EUI by case
            eui_dist     — DataFrame of EUI by end-use category by case
            unmet_hours  — DataFrame of unmet hours by case
            <case_name>  — Xmlpd instance per case
    """
    res = SimpleNamespace(
        eui_dist=pd.DataFrame(),
        elec=pd.DataFrame(),
        gas=pd.DataFrame(),
        distcl=pd.DataFrame(),
        disthw=pd.DataFrame(),
        distst=pd.DataFrame(),
        unmet_hours=pd.DataFrame(),
        eui=pd.Series(dtype=float),
    )

    for case_name in cases:
        case_path = Path(case_name + ".xml")
        if not case_path.exists():
            print(f'{case_name} unavailable')
            continue
        xml = read_xml(case_path)

        end_uses = xml.get_prm()
        setattr(res, case_name, xml)

        res.elec[case_name] = end_uses["ElectricityEnergyUse"]
        res.gas[case_name] = end_uses["NaturalGasEnergyUse"]
        res.distcl[case_name] = end_uses["DistrictCoolingUse"]
        res.disthw[case_name] = end_uses["DistrictHeatingWaterUse"]
        res.distst[case_name] = end_uses["DistrictHeatingSteamUse"]
        res.eui[case_name] = xml.get_eui()
        res.unmet_hours[case_name] = xml.get_unmet_hours()
        res.eui_dist[case_name] = xml.get_eui_dist()

    res.elec        = trimdf(res.elec)
    res.gas         = trimdf(res.gas)
    res.distcl      = trimdf(res.distcl)
    res.disthw      = trimdf(res.disthw)
    res.distst      = trimdf(res.distst)
    res.eui_dist    = trimdf(res.eui_dist)

    return res

__all__ = [
    "joinpar",
    "crosspar",
    "trimrows",
    "trimcols",
    "trimdf",
    "get_batch_eso",
    "get_batch_xml",
    "pct_savings",
]

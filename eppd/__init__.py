"""EPPD: EnergyPlus Python Preprocessor and Postprocessor.

A comprehensive Python library for programmatic manipulation of EnergyPlus
IDF files, running parallel batch and parametric simulations, and post
processing results.

Example Usage:

    Basic IDF manipulation:
        >>> from eppd import read_idf
        >>> model = read_idf('baseline.idf')
        >>> zones = list(model['zone', :, 1].index.get_level_values('name').unique())
        >>> model['lights', :, 5] = 10.76  # Set LPD
        >>> model.write_idf('modified.idf')

    Running simulations:
        >>> from eppd import run_batch
        >>> runs = {'output': ('model.idf', 'weather.epw')}
        >>> results = run_batch(runs)

    Post-processing:
        >>> from eppd import read_xml, read_eso
        >>> parser = read_xml('output_Table.xml')
        >>> energy = parser.get_end_use_energy()
        >>> eui = parser.get_eui()
        >>> hourly = read_eso('eplusout.eso')

    Batch simulations:
        >>> from eppd import run_batch
        >>> runs = {
        ...     'base': ('base.idf', 'weather.epw'),
        ...     'improved': ('improved.idf', 'weather.epw')
        ... }
        >>> results = run_batch(runs, max_workers=4)

    Output reports:
        >>> from eppd import apnd, Sobj
        >>> zones = ['Core', 'Perimeter']
        >>> outputs = apnd([Sobj.znt, Sobj.znlt], vlist=zones)
        >>> model.write_idf('modified.idf', append_string=outputs)

    Parametric studies:
        >>> from eppd import setup_param_db, run_parametric, mergex
        >>> # Create parameter grid
        >>> lpd = pd.DataFrame({'lpd': [10, 12, 14]})
        >>> params = lpd.copy()
        >>> params['runid'] = range(len(params))
        >>> params['idffile'] = 'baseline.idf'
        >>> params['weather'] = 'Chicago.epw'
        >>> # Setup database (runs trial sim(s) in parallel to detect output columns)
        >>> # Default uses get_standard_results, or specify custom parser
        >>> setup_param_db('study.db', params)  # or output_parser=my_parser
        >>> # OPTIMIZATION: Pre-define output columns and use run_trial=False to skip trials
        >>> param_map = [('lpd', ('lights', slice(None), 5))]
        >>> run_parametric('study.db', param_map)  # Results auto-exported to study.parquet
        >>> # Load results: results = pd.read_parquet('study.parquet')
"""

__version__ = "0.1.1"

# Core functionality
from .core import *

# systems
from .systems import *

# Simulation
from .simulation import *


# Post-processing
from .postprocess import *

# Configuration
from .config import energyplus_config

# Utilities
from .utils import *


__all__ = [
    # Version info
    "__version__",
    # Core
    "read_idf",       # Load an EnergyPlus IDF file into a pandas Series DataFrame.
    "Eidx",           # Enum of common IDF field shortcuts with built-in unit conversion (IP→SI).
    "Sobj",           # Enum of EnergyPlus objects as strings to add to the idf file.
    "apnd",           # convenience function to add zone,node etc to output:variable
    # Systems
    "createsys",      # Add a complete HVAC system to a model from a zone-system assignment DataFrame.
    "PlantConfig",    # Dataclass for specifying central plant equipment (hot water, chilled water, WLHP loops) for createsys.
    "pltsys",         # Namespace of available central plant equipment type constants (e.g. pltsys.ashp).
    "dhwsys",         # Namespace of available domestic hot water system type constants (e.g. dhwsys.heatpump).
    # Simulation
    "run_batch",      # Run one or more EnergyPlus simulations in parallel given a dict of {name: (idf, epw)}.
    "setup_param_db", # Initialise a SQLite database for a parametric study from a parameter DataFrame.
    "run_parametric", # Execute all pending runs in a parametric study database and export results to parquet.
    "runs_to_parquet",# Export completed parametric study runs from a SQLite database to a parquet file.
    # Post-processing
    "read_xml",       # Parse an EnergyPlus XML summary reports and convert to pandas DataFrame
    "read_eso",       # Read an EnergyPlus ESO file and return hourly/sub-hourly time-series data as a DataFrame.
    # Configuration
    "energyplus_config",  # Get or set the EnergyPlus installation path and executable used for simulations.
    # Utilities
    "joinpar",        # Vertically stack a list of parameter DataFrames (union of scenarios).
    "crosspar",       # Cartesian-product merge a list of parameter DataFrames (all combinations).
    "trimrows",       # Drop rows that are entirely zero/NaN from a DataFrame.
    "trimcols",       # Drop columns that are entirely zero/NaN from a DataFrame.
    "trimdf",         # Drop both all-zero rows and all-zero columns from a DataFrame.
    "pct_savings",    # Compute percentage savings of each column relative to a baseline Series.
    "get_batch_eso",  # Load ESO results for a list of batch run names into a single namespace.
    "get_batch_xml",  # Load XML results for a list of batch run names into a single namespace.
]

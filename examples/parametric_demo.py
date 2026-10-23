""" eppd EnergyPlus parametric study demo.

Demonstrates setting up and running a parametric study across multiple
building parameters and climate zones using a pre-built IDF template.

Workflow:
    1. Define parameter combinations (crosspar / joinpar)
    2. setup_param_db()   — creates SQLite database, runs trial simulation
                            to detect output columns
    3. run_parametric()   — applies parameters and runs all combinations
    4. runs_to_parquet()  — exports completed results to parquet for analysis

API Reference
-------------
Core
    read_idf            Load an EnergyPlus IDF file into a pandas Series DataFrame.
    Eidx                Enum of common IDF field shortcuts with built-in unit conversion (IP→SI).
    Sobj                Enum of EnergyPlus output object templates (zone temp, lighting, etc.).
    apnd                Build an output variable string from Sobj templates to append to an IDF.

Systems
    createsys           Add a complete HVAC system to a model from a zone-system assignment DataFrame.
    PlantConfig         Dataclass for specifying central plant equipment (hot water, chilled water, WLHP loops).
    pltsys              Namespace of available central plant equipment type constants (e.g. pltsys.boiler).
    dhwsys              Namespace of available domestic hot water system type constants (e.g. dhwsys.heatpump).

Simulation
    run_batch           Run one or more EnergyPlus simulations in parallel given a dict of {name: (idf, epw)}.
    setup_param_db      Initialise a SQLite database for a parametric study from a parameter DataFrame.
    run_parametric      Execute all pending runs in a parametric study database and export results to parquet.
    runs_to_parquet     Export completed parametric study runs from a SQLite database to a parquet file.

Post-processing
    read_xml            Parse an EnergyPlus XML summary reports and convert to pandas DataFrame
    read_eso            Read an EnergyPlus ESO file and return hourly/sub-hourly time-series as a DataFrame.

Configuration
    energyplus_config   Get or set the EnergyPlus installation path and executable used for simulations.

Utilities
    joinpar             Vertically stack a list of parameter DataFrames (union of scenarios).
    crosspar            Cartesian-product merge a list of parameter DataFrames (all combinations).
    trimrows            Drop rows that are entirely zero/NaN from a DataFrame.
    trimcols            Drop columns that are entirely zero/NaN from a DataFrame.
    trimdf              Drop both all-zero rows and all-zero columns from a DataFrame.
    pct_savings         Compute percentage savings of each column relative to a baseline Series.
    get_batch           Load XML (and ESO) results for a list of batch run names into a single namespace.

"""


from pathlib import Path

import numpy as np
import pandas as pd

from eppd import *
#from eppd import apnd, Eidx, read_eso, read_idf, read_xml, run_batch, Sobj
#from eppd.systems import *
#from eppd.systems.createsys import PlantConfig
#from eppd.simulation import setup_param_db, run_parametric
#from eppd.utils import *


# ---------------------------------------------------------------------------
# IDF files to run (required column)
# ---------------------------------------------------------------------------
idffile = pd.DataFrame(
    {"idffile": ["refbld/RefBldgMediumOfficeNew2004_Chicago_mod.idf"]}
)

# ---------------------------------------------------------------------------
# Specify Weather locations to run (required column)
# Columns: weather file, heating design db, heating db range,
#          cooling design db, cooling db range
# ---------------------------------------------------------------------------

# set your weather files path here
weadir = Path("~/Projects/WeatherData").expanduser()

wea = pd.DataFrame(
    [
        ("PRI_San.Juan-Luis.Munoz.Marin.Intl.AP.785263_TMY3.epw",  20.9,  0, 32.8,  6.1),  # 1a very-hot-humid
        ("USA_TX_Austin-Mueller.Muni.AP.722540_TMY3.epw",           -3.8,  0, 37.6, 12.5),  # 2a hot-humid
        ("USA_GA_Atlanta-Hartsfield-Jackson.Intl.AP.722190_TMY3.epw",-6.3, 0, 33.0,  9.5),  # 3a warm-humid
        ("USA_AZ_Phoenix-Sky.Harbor.Intl.AP.722780_TMY3.epw",        3.7,  0, 43.4, 12.0),  # 3b warm-dry
        ("USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw",             3.8,  0, 28.3,  8.5),  # 3c warm-marine
        ("USA_VA_Arlington-Ronald.Reagan.Washington.Natl.AP.724050_TMY3.epw", -8.7, 0, 34.6, 8.9),  # 4a mixed-humid
        ("USA_OR_Portland.Intl.AP.726980_TMY3.epw",                 -4.5,  0, 32.9, 12.2),  # 4c mixed-marine
        ("USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw",           -20.0,  0, 33.3, 10.5),  # 5a cool-humid
        ("USA_CO_Denver.Intl.AP.725650_TMY3.epw",                  -17.4,  0, 34.6, 15.2),  # 5b cool-dry
        ("USA_WI_Madison-Dane.County.Rgnl.AP.726410_TMY3.epw",     -22.8,  0, 32.1, 11.1),  # 6a cold-humid
        ("USA_ID_Boise.Air.Terminal.726810_TMY3.epw",              -16.3,  0, 36.7, 16.7),  # 6b cold-dry
        ("USA_AK_Fairbanks.Intl.AP.702610_TMY3.epw",              -41.0,  0, 27.4, 10.2),  # 7  very-cold
    ],
    columns=["weather", "htgdb", "htgrng", "clgdb", "clgrng"],
)
wea["weather"] = wea["weather"].map(lambda x: str(weadir / x))

# ---------------------------------------------------------------------------
# Parameter definitions
# Use joinpar() to stack alternatives back-to-back (independent measures).
# Use crosspar() to get the full Cartesian product.
# ---------------------------------------------------------------------------
wallins  = pd.DataFrame({"insulation_thickness": np.linspace(0.5, 12, 4)}).apply(Eidx.insulation_thickness.ip)
oaperson = pd.DataFrame({"oaperson": [0, 10, 30]}).apply(Eidx.oaperperson.ip)
equip    = pd.DataFrame({"inp:equip": np.array([0, 1, 2, 3, 5, 8, 13, 21, 34])}).apply(Eidx.epd.ip)
lpd      = pd.DataFrame({"lpd": [1.5, 1, 0.6]}).apply(Eidx.lpd.ip)

pmeasures = joinpar([wallins, lpd, oaperson])
pr = crosspar([pmeasures, idffile, wea])


# ---------------------------------------------------------------------------
# Optional runid column
# use optional runid column with unique values to specify custom names for parametric runs.
# ---------------------------------------------------------------------------

# pr["runid"]


# ---------------------------------------------------------------------------
# Output columns to collect from the parametric runs
# Output columns listed here must be generated by a xml output parsers
# Default xml output parser is Xmlpd.get_standard_results()
# other output parsers can be passed as a list of strings
# set this list to output_parser parameter of the run_parametric function
# ---------------------------------------------------------------------------
outputcols = [
    "DuringHeating",
    "DuringCooling",
    "DuringOccupiedHeating",
    "DuringOccupiedCooling",
    "EUI",
    "Heating_Electricity",
    "Heating_NaturalGas",
    "Cooling_Electricity",
    "InteriorLighting_Electricity",
    "InteriorEquipment_Electricity",
    "Fans_Electricity",
    "Pumps_Electricity",
    "WaterSystems_Electricity",
    "WaterSystems_NaturalGas",
    # "Heating_Electricity_demand",
    # "Heating_NaturalGas_demand",
    # "Heating_DistrictCooling",
    # "Heating_DistrictHeatingWater",
    # "Heating_DistrictHeatingSteam",
    # "Cooling_Electricity_demand",
    # "Cooling_DistrictCooling",
    # "InteriorLighting_Electricity_demand",
    # "InteriorEquipment_Electricity_demand",
    # "InteriorEquipment_NaturalGas",
    # "ExteriorEquipment_Electricity",
    # "ExteriorLighting_Electricity",
    # "ExteriorLighting_Electricity_demand",
    # "ExteriorEquipment_NaturalGas",
    # "Fans_Electricity_demand",
    # "Pumps_Electricity_demand",
    # "HeatRejection_Electricity",
    # "HeatRejection_Electricity_demand",
    # "Humidification_Electricity",
    # "Humidification_NaturalGas",
    # "HeatRecovery_Electricity",
    # "HeatRecovery_NaturalGas",
    # "WaterSystems_Electricity_demand",
    # "WaterSystems_NaturalGas_demand",
    # "WaterSystems_DistrictHeatingWater",
    # "WaterSystems_DistrictHeatingSteam",
    # "Refrigeration_Electricity",
]

pr[outputcols] = np.nan


# ---------------------------------------------------------------------------
# Parameter index mapping  (idf index → DataFrame column)
# This is a map that determines the idf parmeter the column name is refering to.
# If a map is not provided for a column that column does not change any parameter.
# ---------------------------------------------------------------------------
parmap = {
    "insulation_thickness": Eidx.insulation_thickness.get("steel frame nonres wall insulation"),
    "lpd":                  Eidx.lpd.get(),
    "oaperson":             Eidx.oaperperson.get(),

    "htgdb":                Eidx.sizingdb.get("chicago ann htg 99.6% condns db"),
    "htgrng":               Eidx.sizingrng.get("chicago ann htg 99.6% condns db"),

    "clgdb":                Eidx.sizingdb.get("chicago ann clg .4% condns wb=>mdb"),
    "clgrng":               Eidx.sizingrng.get("chicago ann clg .4% condns wb=>mdb")
}

# ---------------------------------------------------------------------------
# Run parametric study
# setup_param_db will not overwrite an existing database.
# run_parameteric will preserve completed runs and process unfinished runs.
# set the max_runs parameter to number of desired parallel runs (default 5)
# set the batch_size to specify how often data is persisted to the the database (default 20)
# If the program is stopped before each batch_size runs complete the results are lost.
# (ctrl+c) stops the simulations.
# Passing the same file to run_parametric will continue where it left off.
# ---------------------------------------------------------------------------
setup_param_db("prstudy.db", pr)
run_parametric("prstudy.db", parmap)

# ---------------------------------------------------------------------------
# convinience function to extract completed runs and save as a parquet file.
# ---------------------------------------------------------------------------
runs_to_parquet("prstudy.db")
pres = pd.read_parquet("prstudy.parquet")

# ---------------------------------------------------------------------------
# Sample analytics
# ---------------------------------------------------------------------------

# get mean EUI by weather
print("Mean EUI by climate",pres.groupby("weather")["EUI"].mean())

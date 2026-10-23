
from eppd import *
from pathlib import Path
import pandas as pd
import numpy as np

# Project paths
project_dir = Path.cwd()

# Weather file: full path to the EPW file
weadir = (
    project_dir
    / "skills"
    / "eppd-modeler"
    / "export"
    / "DEU_BW_Stuttgart.AP.107380_TMYx_fixed.epw"
).resolve()

# Input IDF model
idf_path = (
    project_dir
    / "skills"
    / "eppd-modeler"
    / "export"
    / "Geometry.idf"
).resolve()

# Verify input files exist before running
if not weadir.is_file():
    raise FileNotFoundError(f"Weather file not found: {weadir}")

if not idf_path.is_file():
    raise FileNotFoundError(f"IDF file not found: {idf_path}")

print(f"Weather file: {weadir}")
print(f"IDF file:     {idf_path}")

# Load baseline model
baseline = read_idf(str(idf_path))

baseline.drop_objects([
    "simulationcontrol",
    "outputcontrol:table:style",
    "output:table:summaryreports"
])

cases = {}

# Shared simulation settings
sim_objects = apnd([
    Sobj.simctl,
    Sobj.xmlout,
    Sobj.allsummary,
    Sobj.sysoa
])

# -- Baseline --
fname = "baseline"
baseline.write_idf(fname + ".idf", sim_objects)
cases[fname] = (fname + ".idf", str(weadir))

# -- Reduce lighting by 20% --
fname = "lpd_reduced"
mod = baseline.copy()
mod[Eidx.lpd.get()] *= 0.8
mod.write_idf(fname + ".idf", sim_objects)
cases[fname] = (fname + ".idf", str(weadir))

# -- Set equipment power density to 1 W/sqft --
fname = "epd_1wsf"
mod = baseline.copy()
mod[Eidx.epd.get()] = Eidx.epd.ip(1.0)
mod.write_idf(fname + ".idf", sim_objects)
cases[fname] = (fname + ".idf", str(weadir))

# Run all cases
run_batch(cases)

# Collect results
res = get_batch_xml(cases)
eso = get_batch_eso(cases)

pd.set_option("display.float_format", lambda x: f"{x:,.2f}")

print("\n" + "=" * 60, "Unmet Hours:\n", res.unmet_hours)
print("=" * 60)

for n, ea in eso.esosum.items():
    print("\n", n, ": Eso Sum--------\n", ea)

print("\n" + "=" * 60, "EUI Distribution:\n", res.eui_dist)
print("=" * 60)

# Access patterns:
# res.elec       - Electricity end-use DataFrame
# res.gas        - Gas end-use DataFrame
# res.unmet_hours - Unmet hours DataFrame
# res.eui_dist   - EUI distribution across cases
# eso.esosum     - Summary results for each case


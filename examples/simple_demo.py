"""
Simple eppd library demo

Demonstrates loading a reference IDF, applying energy efficiency measures,
and running and post-processing a batch of EnergyPlus simulations.
"""
# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

from pathlib import Path
from eppd import *

# Source IDF files
refbldfolder = Path("refbld")

# Set your weather files path here
weadir = Path("~/Projects/WeatherData").expanduser()

cases = {}

# ---------------------------------------------------------------------------
# Load base case
# ---------------------------------------------------------------------------
rtb = read_idf(refbldfolder / "tb.idf")

rtb.write_idf('tb_base.idf',apnd([Sobj.clcoil,Sobj.oadt]))
cases['tb_base'] = (Path("tb_base.idf"), weadir / "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")

# ---------------------------------------------------------------------------
# Apply modifications and write modified case
# ---------------------------------------------------------------------------

# Reduce lighting power density by 20%
rtb[Eidx.lpd.get()] *= 0.8

rtb.write_idf('tb_lpd.idf',apnd([Sobj.clcoil,Sobj.oadt]))
cases['tb_lpd'] = ("tb_lpd.idf", weadir / "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")

# Set insulation thickness
rtb[Eidx.insulation_thickness.get("board insulation (glass fiber board)_0.0435")] = Eidx.insulation_thickness.ip(6)

rtb.write_idf('tb_ins.idf',apnd([Sobj.clcoil,Sobj.oadt]))
cases['tb_ins'] = ("tb_ins.idf", weadir / "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")

# Turn off economizer
rtb[Eidx.economizer.get()] = "noeconomizer"

rtb.write_idf('tb_noeco.idf',apnd([Sobj.clcoil,Sobj.oadt]))
cases['tb_noeco'] = ("tb_noeco.idf", weadir / "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")

# Add occupancy-based demand control ventilation
rtb[Eidx.dcvsch.get()] = "office_openoff_occ"

rtb.write_idf('tb_dcv.idf',apnd([Sobj.clcoil,Sobj.oadt]))
cases['tb_dcv'] = ("tb_dcv.idf", weadir / "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")

# Set supply and extract fan static pressures
rtb[Eidx.fanstatic.get(("supply",))] = Eidx.fanstatic.ip(3.5)
rtb[Eidx.fanstatic.get(("extract",))] = Eidx.fanstatic.ip(2.5)

rtb.write_idf('tb_fan.idf',apnd([Sobj.clcoil,Sobj.oadt]))
cases['tb_fan'] = ("tb_fan.idf", weadir / "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")

# Turn off heat recovery 
rtb[Eidx.heatrec.get()] = "Off 24/7"
#rtb['heatexchanger:airtoair:sensibleandlatent',:,12] = 'no'
rtb.write_idf('tb_NoHeatRec.idf',apnd([Sobj.clcoil,Sobj.oadt]))
cases['tb_NoHeatRec'] = ("tb_NoHeatRec.idf", weadir / "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")

## Rotate building — uncomment to add a case for each 90-degree orientation
#ndir = rtb[Eidx.blddir.get()].values
#for d in [0, 90, 180, 270]:
#    rtb[Eidx.blddir.get()] = ndir + d
#    fname = f"roffice_{d}"
#    rtb.write_idf(fname + ".idf")
#    cases[fname] = (fname + ".idf", weadir / "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")

## ---------------------------------------------------------------------------
## Run simulations
## ---------------------------------------------------------------------------
## set energyplus version if different from value in config.toml
#from eppd.config import energyplus_config
#energyplus_config.energyplus_location = '/usr/local/EnergyPlus-26-1-0'

run_batch(cases, max_runs=3)

## ---------------------------------------------------------------------------
## Process results
## ---------------------------------------------------------------------------

## Read a single XML result file
#xtb = read_xml('tb_base.xml')
#print(xtb.get_unmet_hours())
#print(xtb.get_eui())

## Copy to clipboard for pasting into Word/Excel
#xtb.get_prm().to_clipboard()

# Load all cases using the batch convenience function
res = get_batch_xml(cases)


# print eui distribution of all cases
print(res.eui_dist)


## process eso file.
## Load eso only works if all hourly outputs have the same time interval and output does not include sizing period runs, meter data.
eso = get_batch_eso(cases)
#print(eso.tb_mod.groupby(eso.tb_mod.index.month).sum())
#print(eso.tb_NoHeatRec.groupby(eso.tb_NoHeatRec.index.month).sum())


##Temperature response (Experimental)
import matplotlib.pyplot as plt
from eppd.postprocess import changepoint_fit
oadt = eso.tb_base['Site Outdoor Air Drybulb Temperature','Environment']*1.9+32
clMbtu = eso.tb_base['Cooling Coil Total Cooling Energy','AHU1 CHW COOLING COIL']/1055/1000
tmp,response = changepoint_fit(oadt.values,clMbtu.values)
plt.plot(oadt,clMbtu,'+')
plt.plot(tmp,response)
plt.xlabel('Temperature')
plt.ylabel('MBtu')

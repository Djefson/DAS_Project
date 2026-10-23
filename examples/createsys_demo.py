"""EnergyPlus system creation demo.

Demonstrates use of createsys to replace HVAC systems in an IDF file,
run batch cases, and process results.

Create a System assignment DataFrame columns:
    zn      : Zone name (index)
    airloop : Air loop config string, format: [coolingCoil]_[heatingCoil]_[airloopType]
    sname   : Unique air loop name — zones sharing a name are served by one air loop
    zonesys : Zone system code (see System Types below)
    fan     : Air loop fan operation schedule name (must exist in the IDF)


Air Loop specification Pattern
------------------------------
[coolingCoil]_[heatingCoil]_[airloopType]

Cooling coil options:
    dx  : DX cooling coil
    chw : Chilled water coil (requires chilled water plant)

Heating coil options:
    el  : Electric coil
    ng  : Natural gas furnace
    hp  : Electric air-to-air heat pump
    hw  : Hot water coil (requires hot water plant)

Air loop type options:
    vav     : Variable air volume (zone system should only be vavel or vavhw)
    cv      : Constant volume (zone system should also be a cv)
    doas    : Dedicated outdoor air system (specify a zone unit such as fcu,whp etc.)
    vrfdoas : DOAS serving zone VRF units (zone systems should be vrf)


Zone System Types
-----------------
    cv     : Constant volume ADU                    | airloop: cv
    vavhw  : VAV with hot water reheat              | airloop: vav,  plant: hw
    vavel  : VAV with electric reheat               | airloop: vav
    cb     : Active/passive chilled beam            | airloop: doas, plant: hw + chw
    fcu    : Fan coil unit                          | airloop: doas, plant: hw + chw
    ahp    : Air-source heat pump                   | airloop: doas
    whp    : Water-source heat pump                 | airloop: doas, plant: whp loop + tower
    vrf    : Variable refrigerant flow terminal     | airloop: vrfdoas
    ptac   : Packaged terminal AC (no airloop)
    pthp   : Packaged terminal heat pump (no airloop)
    uhel   : Electric unit heater (no airloop)
    uhhw   : Hot water unit heater (no airloop),     plant: hw

Append _[baseboard] to zone system type to add a baseboard:
    bhw : Hot water baseboard
    bel : Electric baseboard


Central Plant Options
---------------------
    boiler             : Natural gas boiler
    aircooledchiller   : Air-cooled chiller
    watercooledchiller : Water-cooled chiller
    coolingtower       : Cooling tower (condenser rejection for chw or whp loop)
    fluidcooler        : Fluid cooler (condenser rejection for chw)
    distheating        : District heating
    distcooling        : District cooling
    airtowaterhp       : Air to water heat pump
    gshphtg            : Ground-source heat pump heating (pair with gshpclg)
    gshpclg            : Ground-source heat pump cooling (pair with gshphtg)


Domestic Hot Water
------------------
If the IDF contains wateruse:equipment, createsys automatically creates a water heater.
    dhwtype options: 'naturalgas' | 'electricity' | 'heatpump'


Notes
-----
1. All IDF object names must be lowercase (Python is case-sensitive).
2. Imported IDF should have designspecification:outdoorair, sizing:zone,
   and zonecontrol:thermostat objects for createsys to work.
3. IDF objects that do not follow the standard object/name pattern can be added
   back as strings at the start of simulation (e.g. simulationcontrol,
   hourly outputs, fluidproperties).
4. createsys creates new systems but controllers and parameters may need
   manual adjustment.

Createsys Limitations
---------------------
- Does not handle complex loops or multiple water loops of the same type
- Cannot model loops through attic spaces
- Humidifier system not implemented yet.
- Does not model plenum return


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

Utility functions
    joinpar             Vertically stack a list of parameter DataFrames (union of scenarios).
    crosspar            Cartesian-product merge a list of parameter DataFrames (all combinations).
    trimrows            Drop rows that are entirely zero/NaN from a DataFrame.
    trimcols            Drop columns that are entirely zero/NaN from a DataFrame.
    trimdf              Drop both all-zero rows and all-zero columns from a DataFrame.
    pct_savings         Compute percentage savings of each column relative to a baseline Series.
    get_batch           Load XML (and ESO) results for a list of batch run names into a single namespace.

"""

from pathlib import Path
from shutil import copyfile

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from eppd import *

## ---------------------------------------------------------------------------
# Paths
## ---------------------------------------------------------------------------

# source idf files
refbldfolder = Path("refbld")

# set your weatherfiles path here
weadir = Path("~/Projects/WeatherData").expanduser()

cases = {}

# ---------------------------------------------------------------------------
# Load and setup base case for testing file 
# ---------------------------------------------------------------------------
rtb = read_idf(refbldfolder / "RefBldgMediumOfficeNew2004_Chicago.idf")
#drop objects causing issues, we will re-add them to make them compatible with eppd library.
rtb.drop_objects(["output:environmentalimpactfactors","output:meter","output:variable",
                  "outputcontrol:table:style","output:table:summaryreports","simulationcontrol"])

simsettings =  apnd([Sobj.simctl, Sobj.xmlout, Sobj.allsummary])
rtb.append_from_string(simsettings)


fname = "roffice_base"
apnd_str =  apnd([Sobj.sysoa,Sobj.zrh])
rtb.write_idf(fname + ".idf", apnd_str)
cases[fname] = ( fname + ".idf", weadir / "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw",)

## ---------------------------------------------------------------------------

## --- define zone groups for convenience
botflr = ["perimeter_bot_zn_1","perimeter_bot_zn_2","perimeter_bot_zn_3","perimeter_bot_zn_4","core_bottom","firstfloor_plenum"]
midflr = ["perimeter_mid_zn_1","perimeter_mid_zn_2","perimeter_mid_zn_3","perimeter_mid_zn_4","core_mid","midfloor_plenum"]
topflr = ["perimeter_top_zn_1","perimeter_top_zn_2","perimeter_top_zn_3","perimeter_top_zn_4","core_top","topfloor_plenum"]
plnflr = ["firstfloor_plenum","midfloor_plenum","topfloor_plenum"]
corezn = ["core_bottom","core_mid","core_top"]
perimz = list(set(botflr+midflr+topflr)-set(plnflr+corezn))

## --- Setup systems assignment table
sysdf = pd.DataFrame(index=rtb[Eidx.znames.get()].index)
sysdf[["sname","airloop","zonesys"]] = ''
sysdf["fan"] = "hvacoperationschd"

sysdf.loc[botflr,"sname"] = "vav_bot"
sysdf.loc[midflr,"sname"] = "vav_mid"
sysdf.loc[topflr,"sname"] = "vav_top"
#sysdf.loc[plnflr,'sname'] = [ea+'_sys' for ea in plnflr]

sysdf = sysdf.drop(plnflr)
## ---------------------------------------------------------------------------
# Commented example runs (uncomment and adapt as needed)
## ---------------------------------------------------------------------------

## -- VAV + dx cooling, natural gas  + electric reheat --
#fname = "rtestdxngelec"
#sysdf["airloop"] = "dx_ng_vav"
#sysdf["zonesys"] = "vavel"
#rnew = createsys(rtb, sysdf)
#rnew[Eidx.heatrec.get()] = "always_off"

#rnew.write_idf(fname + ".idf", apnd_str
#+ "\nschedule:compact,always_off,fraction,through: 12/31,for:alldays,until:24:00,1;")
#cases[fname] = (fname + ".idf", weadir / "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")

#fname = "roffice_eem1"
#rnew[Eidx.insulation_thickness.get("steel frame nonres wall insulation")] = Eidx.insulation_thickness.ip(6)
#rnew[Eidx.lpd.get()] *= 0.8

#rnew.write_idf(fname + ".idf", apnd_str
#+ "\nschedule:compact,always_off,fraction,through: 12/31,for:alldays,until:24:00,1;")
#cases[fname] = (fname + ".idf", weadir / "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")

## -- DOAS + chilled water fan coil units, water-cooled chiller + fluid cooler --
fname = "rtestfluidcooler"
sysdf["airloop"] = "chw_hw_doas"
sysdf["zonesys"] = "fcu"
cp = PlantConfig(hw=pltsys.boiler, chw=(pltsys.watercooledchiller, pltsys.fluidcooler))
rnew = createsys(rtb, sysdf, cp=cp)
rnew.write_idf(fname + ".idf", apnd_str)
cases[fname] = (fname + ".idf", weadir / "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")

## -- VAV with DX cooling and natural gas heating (disable economizer, set DCV + fan static) --
#fname = "rdxngvav"
#sysdf["airloop"] = "dx_ng_vav"
#sysdf["zonesys"] = "vavel"
#rnew = createsys(rtb, sysdf)
#rnew[Eidx.economizer.get()] = "noeconomizer"
#rnew[Eidx.dcvsch.get()] = "bldg_occ_sch"
#rnew[Eidx.fanstatic.get(("supply",))] = Eidx.fanstatic.ip(3.5)
#rnew[Eidx.fanstatic.get(("extract",))] = Eidx.fanstatic.ip(3.5)
#rnew.write_idf(fname + ".idf", apnd_str)
#cases[fname] = (fname + ".idf", weadir / "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")

# -- DOAS + chilled beam with fan coil, air-cooled chiller + air to water heat pump, hot water baseboard in perimeter --
fname = "rcbfcu_hpcp"
sysdf["airloop"] = "chw_hw_doas"
sysdf["zonesys"] = "cb"
sysdf.loc[perimz, "zonesys"] = "fcu_bel"
cp=PlantConfig(hw=pltsys.airtowaterhp, chw=pltsys.aircooledchiller)
rnew = createsys(rtb, sysdf, cp=cp)
rnew[Eidx.insulation_thickness.get("iead nonres roof insulation")] = Eidx.insulation_thickness.ip(10)
rnew.write_idf(fname + ".idf", apnd_str)
cases[fname] = (fname + ".idf", weadir / "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")


## -- DOAS + VRF zone units --
#fname = "rvrfdoas"
#sysdf["airloop"] = "dx_hp_vrfdoas"
#sysdf["zonesys"] = "vrf"
#rnew = createsys(rtb, sysdf)
#rnew.write_idf(fname + ".idf", apnd_str)
#cases[fname] = (fname + ".idf", weadir / "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")


## -- DOAS + water-source heat pumps, boiler + cooling tower --
#fname = "rwhp"
#sysdf["airloop"] = "chw_hw_doas"
#sysdf["zonesys"] = "whp"
#cp = PlantConfig(whp=[pltsys.boiler, pltsys.coolingtower])
#rnew = createsys(rtb, sysdf,cp=cp)
#rnew.write_idf(fname + ".idf", apnd_str)
#cases[fname] = (fname + ".idf", weadir / "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")

## -- packaged terminal heat pump, zone only system, system per zone
fname = "pthp_test"
sysdf["airloop"] = None
sysdf["zonesys"] = "pthp"
rnew = createsys(rtb, sysdf)
#rnew["coil:heating:dx:singlespeed",:,1] = "off"
rnew.write_idf(fname + ".idf", apnd_str)
cases[fname] = (fname + ".idf", weadir / "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")


## -- DOAS + air-source heat pump zone units --
#fname = "rhpahp"
#sysdf["airloop"] = "dx_hp_doas"
#sysdf["zonesys"] = "ahp"
#rnew = createsys(rtb, sysdf)
#rnew.write_idf(fname + ".idf", apnd_str)
#cases[fname] = (fname + ".idf", weadir / "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")


## -- packaged terminal air conditioner, zone only system, system per zone
#fname = "ptac_test"
#sysdf["airloop"] = None
#sysdf["zonesys"] = "ptac"
#rnew = createsys(rtb, sysdf)
#rnew.write_idf(fname + ".idf", apnd_str)
#cases[fname] = (fname + ".idf", weadir / "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")

## -- DOAS + fan coil units, ground-source heat pump --
fname = "rgshp"
sysdf["airloop"] = "chw_hw_doas"
sysdf["zonesys"] = "fcu_bhw"
cp=PlantConfig(hw=pltsys.gshphtg, chw=pltsys.gshpclg)
rnew = createsys(rtb, sysdf,cp=cp)
rnew.write_idf(fname + ".idf", apnd_str)
cases[fname] = (fname + ".idf", weadir / "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")


## -- Constant volume per zone, DX cooling + natural gas boiler heating --
#fname = "rdxngcv"
#sysdf["airloop"] = "dx_hw_cv"
#sysdf["zonesys"] = "cv_bhw"
#sysdf["sname"] = sysdf.index+"_sys"
#cp = PlantConfig(hw=pltsys.boiler)
#rnew = createsys(rtb, sysdf,cp=cp)
#rnew[Eidx.maxsupplyT.get()] = Eidx.maxsupplyT.ip(95)
#rnew.write_idf( fname + ".idf",apnd_str
#+ apnd([Sobj.znt], vlist=["core_bottom"])
#+ apnd([Sobj.nodet], vlist=["core_bottom_sys demand side inlet node"])
#+ apnd([Sobj.fanflow], vlist=["core_bottom_sys supply fan"]),
#)
#cases[fname] = (fname + ".idf", weadir / "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")

## -- VAV with chilled water + hot water coils, water-cooled chiller + fluid cooler --
#fname = "rchwhw_fc"
#sysdf["airloop"] = "chw_hw_vav"
#sysdf["zonesys"] = "vavhw"
#cp=PlantConfig(hw=pltsys.boiler, chw=(pltsys.watercooledchiller, pltsys.fluidcooler))
#rnew = createsys(rtb, sysdf,cp=cp)
#rnew.write_idf(fname + ".idf", apnd_str)
#cases[fname] = (fname + ".idf", weadir / "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")
#
## -- VAV with chilled water + hot water coils, water-cooled chiller + fluid cooler --
#fname = "rchwhw_ct"
#sysdf["airloop"] = "chw_hw_doas"
#sysdf["zonesys"] = "fcu"
#cp=PlantConfig(hw=pltsys.boiler, chw=(pltsys.watercooledchiller, pltsys.fluidcooler))
#rnew = createsys(rtb, sysdf,cp=cp)
#rnew.write_idf(fname + ".idf", apnd_str)
#cases[fname] = (fname + ".idf", weadir / "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")
#
#
## -- DOAS + fan coil units, air-cooled chiller + boiler, hot water baseboard in perimeter --
#fname = "rchwfcu_boiler"
#sysdf["airloop"] = "chw_hw_doas"
#sysdf["zonesys"] = "fcu"
#sysdf.loc[perimz, "zonesys"] = "fcu_bhw"
#cp=PlantConfig(hw=pltsys.boiler, chw=pltsys.aircooledchiller)
#rnew = createsys(rtb, sysdf,cp=cp)
#rnew.write_idf(fname + ".idf", apnd_str)
#cases[fname] = (fname + ".idf", weadir / "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")

## -- DOAS + fan coil units, water-cooled chiller + boiler, hot water baseboard in perimeter --
#fname = "rchwfcu_ct"
#sysdf["airloop"] = "chw_hw_doas"
#sysdf["zonesys"] = "fcu"
#sysdf.loc[perimz, "zonesys"] = "fcu_bhw"
#cp=PlantConfig(hw=pltsys.boiler, chw=(pltsys.watercooledchiller, pltsys.coolingtower))
#rnew = createsys(rtb, sysdf,cp=cp)
#rnew.write_idf(fname + ".idf", apnd_str)
#cases[fname] = (fname + ".idf", weadir / "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")

## -- VAV with chilled water + hot water, district heating and cooling, system per floor --
#fname = "rchwhw"
#sysdf["airloop"] = "chw_hw_vav"
#sysdf["zonesys"] = "vavhw"
#cp=PlantConfig(hw=pltsys.distheating, chw=pltsys.distcooling)
#rnew = createsys(rtb, sysdf,cp=cp)
#rnew.write_idf(fname + ".idf", apnd_str)
#cases[fname] = (fname + ".idf", weadir / "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")

#-- DOAS + chilled beam, air-cooled chiller + boiler --
#fname = "rchwcb"
#sysdf["airloop"] = "chw_hw_doas"
#sysdf["zonesys"] = "cb"
#sysdf.loc[perimz, "zonesys"] = "fcu_bhw"
#cp=PlantConfig(hw=pltsys.boiler, chw=pltsys.aircooledchiller)
#rnew = createsys(rtb, sysdf,cp=cp)
#rnew.write_idf(fname + ".idf", apnd_str)
#cases[fname] = (fname + ".idf", weadir / "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")


## -- DOAS with fan coil units with chilled water + hot water coils, Boiler and air cooled chiller
#fname = "doas_compare"
#sysdf["airloop"] = "chw_hw_doas"
#sysdf["zonesys"] = "fcu"
#cp=PlantConfig(hw=pltsys.boiler, chw=pltsys.aircooledchiller)
#rnew = createsys(rtb, sysdf,cp=cp)
#rnew.write_idf(fname + ".idf", apnd_str)
#cases[fname] = (fname + ".idf", weadir / "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")

## -- VAV with chilled water + hot water coils, Boiler and air cooled chiller
#fname = "vav_compare"
#sysdf["airloop"] = "chw_hw_vav"
#sysdf["zonesys"] = "vavhw"
#cp=PlantConfig(hw=[pltsys.boiler,pltsys.distheating], chw=pltsys.aircooledchiller)
#rnew = createsys(rtb, sysdf,cp=cp)
#rnew[Eidx.economizer.get()] = 'noeconomizer'
#rnew.write_idf(fname + ".idf", apnd_str)
#cases[fname] = (fname + ".idf", weadir / "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")

## -- VAV with chilled water + hot water coils, Boiler and air cooled chiller
#fname = "dxel_compare"
#sysdf["airloop"] = "dx_ng_vav"
#sysdf["zonesys"] = "vavel"
#rnew = createsys(rtb, sysdf)
#rnew[Eidx.heatrec.get()] = 'off'
#rnew.write_idf(fname + ".idf", apnd_str)
#cases[fname] = (fname + ".idf", weadir / "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")

## -- Small hotel loaded from CSV system definition, natural gas DHW, rotated orientations --
fname = "smallhotel"
rhotel = read_idf(refbldfolder / "RefBldgSmallHotelNew2004_Chicago.idf")
rhotel.drop_objects([ "simulationcontrol", "outputcontrol:table:style", "output:table:summaryreports",
"output:variable", "output:environmentalimpactfactors", "output:meter"])
hotelsysdf = pd.read_csv(refbldfolder / "smallhotel.csv", index_col="zn")
rnew = createsys(rhotel, hotelsysdf, dhwtype=dhwsys.naturalgas)
rnew.write_idf(fname + ".idf", simsettings+apnd_str)
cases[fname] = (fname + ".idf", weadir / "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw")



## -- Loop to post-process all cases (copy from refbld, update infiltration) --
#for subf, (idf, wea) in cases.items():
#    idfc = read_idf(idf)
#    idfc[Eidx.infil_method.get()] = "flow/exteriorwallarea"
#    idfc[Eidx.infil_flowrate.get()] = 0.000402
#    idfc.write_idf(idf, apnd([Sobj.unmetcl_occ, Sobj.unmetht_occ]))


## ---------------------------------------------------------------------------
# Run simulations
## ---------------------------------------------------------------------------
run_batch(cases)

## ---------------------------------------------------------------------------
# Process results
## ---------------------------------------------------------------------------
res = get_batch_xml(cases)
eso = get_batch_eso(cases)

##format pandas numbers to display commas for 1000s 
pd.set_option('display.float_format', lambda x: f'{x:,.2f}')

print("\n" + "=" * 60, "Unmet Hours:\n", res.unmet_hours, "\n" + "=" * 60)
for n, ea in eso.esosum.items(): print("\n", n, ":Eso Sum--------\n", ea)
print("\n" + "=" * 60, "EUI Distribuiton:\n", res.eui_dist, "\n" + "=" * 60)

## ---------------------------------------------------------------------------
# Sample Hourly data plotting for rdxngcv case
## ---------------------------------------------------------------------------
#h = eso.rdxngcv
#cfm = h['Fan Air Mass Flow Rate'] *1757
#tsupp = h['System Node Temperature'] *1.8+32
#tzone = h['Zone Mean Air Temperature'] *1.8+32
#unmet = h['Zone Heating Setpoint Not Met While Occupied Time']


#cfm.loc[(unmet>0).values].plot(style='+')
#tzone.loc[(unmet>0).index].plot(style='+')
#tsupp.loc[(unmet>0).values].plot(style='+')

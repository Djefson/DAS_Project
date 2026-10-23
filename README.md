

# **_Data analytics for peak load stabilization in district heating networks (DAS)_.**

# **_EnergyPlus(E+) Using Python_.**
 
                         

# eppd

An open-source Python library for programmatic manipulation of EnergyPlus IDF files, concurrent execution of multiple EnergyPlus simulations, and processing simulation outputs.

The library loads EnergyPlus IDF models into a pandas MultiIndex Series and returns EnergyPlus outputs as pandas DataFrames.

## Features

- Vectorized parameter manipulation
- Queryable IDF data using pandas indexing
- Template-driven HVAC system generation
- Parallel batch simulations
- Data-centric post-processing workflows
- Transparent and repeatable analysis
- LLM-assisted workflow generation

---

## Tutorials

Download the [examples] folder to run sample scripts. The whole folder is needed because the scripts reference IDF files in the `refbld/` subfolder.

## Installation

```bash
pip install eppd
```

Requires a separate installation of EnergyPlus.

**Configure EnergyPlus location:**

1. Copy [`eppd/eppd.toml`] to your project directory.
2. Update `energyplus_location` in `eppd.toml` to the full path of EnergyPlus executable. Examples:

   ```toml
   [energyplus]
   # Linux
   energyplus_location = "/usr/local/EnergyPlus-26-1-0/energyplus"

   # macOS
   # energyplus_location = "/Applications/EnergyPlus-26-1-0/energyplus"

   # Windows
   # energyplus_location = "C:/EnergyPlusV26-1-0/energyplus.exe"
   ```

---

## Overview

```python
from eppd import *
```

A single import exposes everything needed for a full simulation workflow:

| Category | Functions |
|---|---|
| **Core** | `read_idf`, `Eidx`, `Sobj`, `apnd` |
| **Systems** | `createsys`, `PlantConfig`, `pltsys`, `dhwsys` |
| **Simulation** | `run_batch`, `setup_param_db`, `run_parametric`, `runs_to_parquet` |
| **Post-processing** | `read_xml`, `read_eso`, `get_batch_xml`, `get_batch_eso` |

---

## Workflows

### 1. IDF Manipulation

Load an IDF file and modify parameters:

```python
model = read_idf('building.idf')

# Modify parameters (Including converting from IP to SI units)
model[Eidx.lpd.get()] = Eidx.lpd.ip(1.0)          # set lighting power density to 1.0 W/sqft
model[Eidx.economizer.get()] = 'differentialenthalpy' # Modify economizer type
model[Eidx.blddir.get()] = 90                       # Rotate 90 degrees

# Regex based search of IDF objects.
model[Eidx.fanstatic.get('supply.*')] = Eidx.fanstatic.ip(3.5)  # set fan static of all fans with "supply" in its name

# Write updated IDF and append desired output objects
model.write_idf('modified.idf', apnd([Sobj.allsummary, Sobj.sysoa]))
```

---

### 2. HVAC System Creation

HVAC systems are defined through a zone-assignment DataFrame,
allowing entire system layouts to be generated programmatically.

```python
model = read_idf('building.idf')

# Build zone-system assignment table
sysdf = pd.DataFrame(index=model[Eidx.znames.get()].index)
sysdf['sname']   = 'vav_ahu'          # zones assigned to same system name share the air loop
sysdf['airloop'] = 'chw_hw_vav'       # VAV air loop with chilled water and hot water coils
sysdf['zonesys'] = 'vavhw'            # VAV with hot water reheat
sysdf['fan']     = 'hvacoperationschd' # assign system fan schedule.

# Create system with central plant
cp = PlantConfig(hw=pltsys.boiler, chw=pltsys.aircooledchiller) # central plant with hot water boiler and air cooled chiller
new_model = createsys(model, sysdf, cp=cp)
new_model.write_idf('modified_hvac.idf', apnd([Sobj.allsummary, Sobj.sysoa]))
```

**Air loop format:**

Air loop is defined with a simple set of strings.

`[cooling coil]_[heating coil]_[system type]`

| Cooling | Heating | System type |
|---|---|---|
| `chw` chilled water | `hw` hot water | `vav` variable air volume |
| `dx` direct expansion | `ng` natural gas | `cv` constant volume |
| | `el` electric | `doas` dedicated OA system |
| | `hp` heat pump | `vrfdoas` VRF with DOAS |

**Zone systems:**

Zone systems are defined using a separate system string:

`[Air distribution type]_[Optional baseboard type]`

Air distribution options: `cv`, `vavhw`, `vavel`, `fcu`, `cb`, `ahp`, `whp`, `vrf`, `ptac`, `pthp`, `uhel`, `uhhw`
Baseboard options: `_bhw` or `_bel` to add a hot water or electric baseboard.

---

### 3. Batch Simulation

Define simulation cases to run using a dictionary with idf file and weather file.

```python
cases = {
    'baseline': ('baseline.idf', 'Chicago.epw'),
    'eem1':     ('eem1.idf',     'Chicago.epw'),
    'eem2':     ('eem2.idf',     'Chicago.epw'),
}


run_batch(cases)

```

---

### 4. Post-processing

Parse EnergyPlus XML outputs and return as Pandas dataframe:

```python
# after run_batch library copies the xml output to <case_name>.xml)
xml = read_xml('baseline.xml')
eui     = xml.get_eui()               # Site EUI kBtu/sqft
energy  = xml.get_end_use_energy()    # DataFrame by end use and fuel
unmet   = xml.get_unmet_hours()       # Unmet heating and cooling hours

# Loads all xml outputs from batch simulation to compare results (operates on the case names)
res = get_batch_xml(cases)
print(res.eui)          # EUI by case
print(res.eui_dist)     # EUI breakdown by end use
print(res.unmet_hours)  # Unmet hours by case
```

Load ESO outputs into a Pandas DataFrame and create plots.

```python
eso = read_eso('basecase.eso')
eso.plot(style="+", subplots=True)
plt.show()
```

---


### 5. Parametric Study

Run large parameter studies across building parameters, multiple idf files and climate zones:

```python
# Define parameter ranges
wallins  = pd.DataFrame({'insulation_thickness': np.linspace(0.5, 12, 4)}).apply(Eidx.insulation_thickness.ip)
lpd      = pd.DataFrame({'lpd': [1.5, 1.0, 0.6]}).apply(Eidx.lpd.ip)
idffile  = pd.DataFrame({'idffile': ['building_template.idf']})
weather  = pd.DataFrame({'weather': ['Chicago.epw', 'Phoenix.epw', 'Miami.epw']})

# Stack measures and cross with locations
params = crosspar([joinpar([wallins, lpd]), idffile, weather])

# Pre-define output columns (the default parser is get_standard_results;
# any keys it returns must exist as columns before run_parametric writes to them)
for col in ['EUI', 'InteriorLights_Electricity', 'Cooling_Electricity', 'Heating_NaturalGas']:
    params[col] = np.nan

# Map parameter columns to IDF fields
pardict = {
    'insulation_thickness': Eidx.insulation_thickness.get('wall insulation'),
    'lpd':                  Eidx.lpd.get(),
}

# Run — preserves completed runs if interrupted, resumes where it left off
setup_param_db('study.db', params)
run_parametric('study.db', pardict)

# Export and analyse
runs_to_parquet('study.db')
results = pd.read_parquet('study.parquet')
print(results.groupby('weather')['EUI'].mean())
```

---

## AI Skill (Claude Integration)

The `skills/` folder contains a Claude skill that helps generate eppd scripts
from natural-language descriptions.


**Setup:** Copy the `skills/` folder into the `.claude/` directory of your working folder:

```
your_project/
  .claude/
    skills/
      eppd-modeler/    ← drop this here
```

Once set up, Claude will understand eppd's API and can generate complete simulation scripts from a description of your goal.

---

## Edited and Improved by

   Joseph NISHIMWE
   Email: joseph.nishimwe20@gmail.com
   M.Sc in informatics / Assistant Researcher Department of Information Technology
   University of Borås / Sweden
   
---






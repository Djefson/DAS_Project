# HVAC System Configuration

Guide for creating and modifying HVAC systems using `createsys` in the eppd library.

**When to use this reference:**
- Creating new HVAC systems for an IDF model
- Changing system type (e.g., VAV to DOAS + FCU)
- Configuring central plant equipment
- Setting up zone-level systems with baseboards or supplemental heating

## Required Imports

`from eppd import *` exports everything needed — `createsys`, `PlantConfig`, `pltsys`, `dhwsys`, `Eidx`, `get_coil_types`, `get_zone_systems`, `get_baseboard_types`, `get_plant_equipment`, etc.

## Core Workflow

Create a system assignment DataFrame — one row per zone — then call `createsys`:

```python
sysdf = pd.DataFrame(index=idf[Eidx.znames.get()].index)
sysdf["sname"]   = "ahu1"               # zones sharing a name share one air loop
sysdf["airloop"] = "chw_hw_vav"         # airloop type string
sysdf["zonesys"] = "vavhw"              # zone system type
sysdf["fan"]     = "office_openoff_fan" # fan operation schedule (must exist in IDF)

new_idf = createsys(idf, sysdf, cp=PlantConfig(hw=pltsys.boiler, chw=pltsys.aircooledchiller))
new_idf.write_idf("modified.idf", apnd([Sobj.simctl, Sobj.xmlout, Sobj.allsummary, Sobj.sysoa]))
```

## Discovery Functions

**Before any HVAC system setup, run the following command via Bash and read the output into context.** The static tables below are for reference only — keys and descriptions can change between library versions. Always use the live output:

```bash
python -c "
from eppd.systems import get_coil_types, get_zone_systems, get_baseboard_types, get_plant_equipment
print('coil_types:', get_coil_types())
print('zone_systems:', get_zone_systems())
print('baseboard_types:', get_baseboard_types())
print('plant_equipment:', get_plant_equipment())
"
```

Each function returns a dict of `{key: description}`. Use the keys when setting `airloop`, `zonesys`, baseboard suffixes, and `pltsys` members. Read and absorb all four results before writing any system configuration code.

## Airloop Definition

Format: `[coolingCoil]_[heatingCoil]_[airloopType]`

### Cooling Coil Options
| Key | Description |
|-----|-------------|
| `dx` | DX (packaged) cooling — no central plant needed |
| `chw` | Chilled water — requires `chw` in `PlantConfig` |

### Heating Coil Options
| Key | Description |
|-----|-------------|
| `ng` | Natural gas furnace |
| `el` | Electric coil |
| `hp` | Air-to-air heat pump |
| `hw` | Hot water coil — requires `hw` in `PlantConfig` |

### Airloop Type Options
| Key | Description |
|-----|-------------|
| `vav` | Variable air volume |
| `cv` | Constant volume |
| `doas` | Dedicated outdoor air system |
| `vrfdoas` | DOAS serving zone VRF units — use with `zonesys='vrf'` |

### Common Airloop Strings
```python
"dx_ng_vav"      # packaged VAV — no central plant
"dx_ng_cv"       # packaged CV — no central plant
"dx_el_cv"       # packaged CV with electric heat
"dx_hp_doas"     # DOAS with heat pump
"dx_hp_vrfdoas"  # VRF DOAS
"chw_hw_vav"     # central plant VAV
"chw_hw_doas"    # central plant DOAS
```

Leave `airloop` as `None` for zone-only systems (ptac, pthp, uhel, uhhw).

## Zone System Options

| Key | Description | Required Airloop | Requires Plant |
|-----|-------------|-----------------|----------------|
| `cv` | Constant volume single-zone AHU | `cv` | — |
| `vavel` | VAV with electric reheat | `vav` | — |
| `vavhw` | VAV with hot water reheat | `vav` | `hw` |
| `fcu` | Fan coil units | `doas` | `hw` + `chw` |
| `cb` | Chilled beams (hot + cold water) | `doas` | `hw` + `chw` |
| `ahp` | Air-source heat pump | `doas` | — |
| `whp` | Water-source heat pump | `doas` | `whp` loop |
| `vrf` | Variable refrigerant flow | `vrfdoas` | — |
| `ptac` | Packaged terminal AC (electric heat) | none | — |
| `pthp` | Packaged terminal heat pump | none | — |
| `uhel` | Electric unit heater | none | — |
| `uhhw` | Hot water unit heater | none | `hw` |

### Adding Baseboards

Append a baseboard suffix to any zone system key:

```python
"fcu_bhw"   # fan coil + hot water baseboard
"fcu_bel"   # fan coil + electric baseboard
"vavhw_bhw" # VAV HW reheat + hot water baseboard
```

Available suffixes: `_bhw` (hot water), `_bel` (electric).

## Central Plant — PlantConfig

```python
from eppd.systems.createsys import PlantConfig
from eppd.systems.centralplant import pltsys
```

`PlantConfig` accepts three keyword arguments: `hw`, `chw`, `whp`.

- Pass a **single value** for one piece of equipment
- Pass a **list** to stage multiple equipment items — EnergyPlus sequences them by capacity
- `chw` also accepts a **tuple** to pair a water-cooled chiller with its heat rejection device

### `hw` — Hot Water Source
```python
cp = PlantConfig(hw=pltsys.boiler)                              # single boiler
cp = PlantConfig(hw=pltsys.distheating)                         # district heating
cp = PlantConfig(hw=pltsys.gshphtg)                             # ground source heat pump (pair with gshpclg)
cp = PlantConfig(hw=[pltsys.boiler, pltsys.distheating])        # staged: boiler + district heating
cp = PlantConfig(hw=[pltsys.boiler, pltsys.boiler])             # staged: two boilers
```

### `chw` — Chilled Water Source
```python
cp = PlantConfig(chw=pltsys.aircooledchiller)                              # air-cooled chiller
cp = PlantConfig(chw=pltsys.distcooling)                                   # district cooling
cp = PlantConfig(chw=(pltsys.watercooledchiller, pltsys.coolingtower))     # water-cooled + cooling tower
cp = PlantConfig(chw=(pltsys.watercooledchiller, pltsys.fluidcooler))      # water-cooled + fluid cooler
cp = PlantConfig(chw=pltsys.gshpclg)                                       # ground source heat pump (pair with gshphtg)
cp = PlantConfig(chw=[pltsys.aircooledchiller, pltsys.aircooledchiller])   # staged: two air-cooled chillers
```

### `whp` — Water-Source Heat Pump Loop
```python
cp = PlantConfig(whp=[pltsys.boiler, pltsys.coolingtower])  # boiler + cooling tower on WHP loop
```

### Combined Plant Configurations
```python
# Boiler + air-cooled chiller
cp = PlantConfig(hw=pltsys.boiler, chw=pltsys.aircooledchiller)

# Boiler + water-cooled chiller + fluid cooler
cp = PlantConfig(hw=pltsys.boiler, chw=(pltsys.watercooledchiller, pltsys.fluidcooler))

# Boiler + water-cooled chiller + cooling tower
cp = PlantConfig(hw=pltsys.boiler, chw=(pltsys.watercooledchiller, pltsys.coolingtower))

# District heating + district cooling
cp = PlantConfig(hw=pltsys.distheating, chw=pltsys.distcooling)

# Ground source heat pump
cp = PlantConfig(hw=pltsys.gshphtg, chw=pltsys.gshpclg)

# Staged: boiler + district heating, air-cooled chiller
cp = PlantConfig(hw=[pltsys.boiler, pltsys.distheating], chw=pltsys.aircooledchiller)
```

### Plant Equipment Keys (from `get_plant_equipment()`)
| `pltsys` member | Description |
|----------------|-------------|
| `pltsys.boiler` | Natural gas boiler |
| `pltsys.aircooledchiller` | Air-cooled chiller |
| `pltsys.watercooledchiller` | Water-cooled chiller |
| `pltsys.coolingtower` | Cooling tower (water-cooled chiller or WHP loop) |
| `pltsys.fluidcooler` | Fluid cooler (water-cooled chiller) |
| `pltsys.distheating` | District heating |
| `pltsys.distcooling` | District cooling |
| `pltsys.gshphtg` | Ground source heat pump — heating side |
| `pltsys.gshpclg` | Ground source heat pump — cooling side |

## Complete Examples

### Packaged DX VAV — electric reheat, no central plant
```python
sysdf = pd.DataFrame(index=idf[Eidx.znames.get()].index)
sysdf["sname"]   = "ahu1"
sysdf["airloop"] = "dx_ng_vav"
sysdf["zonesys"] = "vavel"
sysdf["fan"]     = "office_openoff_fan"
new_idf = createsys(idf, sysdf)
```

### Packaged DX Constant Volume — one AHU per zone
```python
sysdf = pd.DataFrame(index=idf[Eidx.znames.get()].index)
sysdf["sname"]   = ["sys_" + zn for zn in sysdf.index]  # unique name per zone
sysdf["airloop"] = "dx_ng_cv"
sysdf["zonesys"] = "cv"
sysdf["fan"]     = "office_openoff_fan"
new_idf = createsys(idf, sysdf)
```

### Central Plant VAV — boiler + air-cooled chiller
```python
sysdf = pd.DataFrame(index=idf[Eidx.znames.get()].index)
sysdf["sname"]   = "ahu1"
sysdf["airloop"] = "chw_hw_vav"
sysdf["zonesys"] = "vavhw"
sysdf["fan"]     = "office_openoff_fan"
new_idf = createsys(idf, sysdf, cp=PlantConfig(hw=pltsys.boiler, chw=pltsys.aircooledchiller))
```

### Central Plant VAV — boiler + water-cooled chiller + fluid cooler, multiple AHUs per floor
```python
sysdf = pd.DataFrame(index=idf[Eidx.znames.get()].index)
sysdf["sname"]   = "ahub"
sysdf["airloop"] = "chw_hw_vav"
sysdf["zonesys"] = "vavhw"
sysdf.loc[["fg:cz","fg:ez","fg:nz","fg:sz","fg:wz"], "sname"] = "ahug"  # ground floor AHU
sysdf.loc[["fm:cz","fm:ez","fm:nz","fm:sz","fm:wz"], "sname"] = "ahum"  # mid floor AHU
sysdf.loc[["ft:cz","ft:ez","ft:nz","ft:sz","ft:wz"], "sname"] = "ahut"  # top floor AHU
sysdf["fan"]     = "office_openoff_fan"
new_idf = createsys(idf, sysdf,
    cp=PlantConfig(hw=pltsys.boiler, chw=(pltsys.watercooledchiller, pltsys.fluidcooler)))
```

### DOAS + Fan Coil — boiler + air-cooled chiller
```python
sysdf = pd.DataFrame(index=idf[Eidx.znames.get()].index)
sysdf["sname"]   = "ahu1"
sysdf["airloop"] = "chw_hw_doas"
sysdf["zonesys"] = "fcu"
sysdf["fan"]     = "office_openoff_fan"
new_idf = createsys(idf, sysdf, cp=PlantConfig(hw=pltsys.boiler, chw=pltsys.aircooledchiller))
```

### DOAS + Fan Coil + HW Baseboard — water-cooled chiller + cooling tower
```python
sysdf = pd.DataFrame(index=idf[Eidx.znames.get()].index)
sysdf["sname"]   = "ahu1"
sysdf["airloop"] = "chw_hw_doas"
sysdf["zonesys"] = "fcu_bhw"                                # baseboard in all zones
sysdf.loc[["fg:cz","fm:cz","ft:cz"], "zonesys"] = "fcu"    # no baseboard in core zones
sysdf["fan"]     = "office_openoff_fan"
new_idf = createsys(idf, sysdf,
    cp=PlantConfig(hw=pltsys.boiler, chw=(pltsys.watercooledchiller, pltsys.coolingtower)))
```

### DOAS + Chilled Beams — boiler + air-cooled chiller
```python
sysdf = pd.DataFrame(index=idf[Eidx.znames.get()].index)
sysdf["sname"]   = "ahu1"
sysdf["airloop"] = "chw_hw_doas"
sysdf["zonesys"] = "cb"
sysdf["fan"]     = "office_openoff_fan"
new_idf = createsys(idf, sysdf, cp=PlantConfig(hw=pltsys.boiler, chw=pltsys.aircooledchiller))
```

### DOAS + Water-Source Heat Pump — boiler + cooling tower on WHP loop
```python
sysdf = pd.DataFrame(index=idf[Eidx.znames.get()].index)
sysdf["sname"]   = "ahu1"
sysdf["airloop"] = "chw_hw_doas"
sysdf["zonesys"] = "whp"
sysdf["fan"]     = "office_openoff_fan"
new_idf = createsys(idf, sysdf, cp=PlantConfig(whp=[pltsys.boiler, pltsys.coolingtower]))
```

### DOAS + Air-Source Heat Pump — mixed zone systems
```python
sysdf = pd.DataFrame(index=idf[Eidx.znames.get()].index)
sysdf["sname"]   = "ahu1"
sysdf["airloop"] = "dx_hp_doas"
sysdf["zonesys"] = "ahp"
# basement zones use electric unit heaters (no airloop)
sysdf.loc[["bg:cz","bg:ez","bg:nz","bg:wz"], "airloop"] = None
sysdf.loc[["bg:cz","bg:ez","bg:nz","bg:wz"], "zonesys"] = "uhel"
sysdf["fan"]     = "office_openoff_fan"
new_idf = createsys(idf, sysdf)
```

### VRF DOAS
```python
sysdf = pd.DataFrame(index=idf[Eidx.znames.get()].index)
sysdf["sname"]   = "ahu1"
sysdf["airloop"] = "dx_hp_vrfdoas"
sysdf["zonesys"] = "vrf"
sysdf["fan"]     = "office_openoff_fan"
new_idf = createsys(idf, sysdf)
```

### District Heating + Cooling — multiple AHUs per floor
```python
sysdf = pd.DataFrame(index=idf[Eidx.znames.get()].index)
sysdf["sname"]   = "ahub"
sysdf["airloop"] = "chw_hw_vav"
sysdf["zonesys"] = "vavhw"
sysdf.loc[["fg:cz","fg:ez","fg:nz","fg:sz","fg:wz"], "sname"] = "ahug"
sysdf.loc[["fm:cz","fm:ez","fm:nz","fm:sz","fm:wz"], "sname"] = "ahum"
sysdf.loc[["ft:cz","ft:ez","ft:nz","ft:sz","ft:wz"], "sname"] = "ahut"
sysdf["fan"]     = "office_openoff_fan"
new_idf = createsys(idf, sysdf, cp=PlantConfig(hw=pltsys.distheating, chw=pltsys.distcooling))
```

### Ground Source Heat Pump — DOAS + fan coil
```python
sysdf = pd.DataFrame(index=idf[Eidx.znames.get()].index)
sysdf["sname"]   = "ahu1"
sysdf["airloop"] = "chw_hw_doas"
sysdf["zonesys"] = "fcu"
sysdf["fan"]     = "office_openoff_fan"
new_idf = createsys(idf, sysdf, cp=PlantConfig(hw=pltsys.gshphtg, chw=pltsys.gshpclg))
```

## Domestic Hot Water

`createsys` automatically creates a DHW system when the IDF contains `wateruse:equipment` objects.
Control the heater type with the `dhwtype` parameter:

```python
new_idf = createsys(idf, sysdf, cp=cp, dhwtype=dhwsys.naturalgas)   # default
new_idf = createsys(idf, sysdf, cp=cp, dhwtype=dhwsys.electricity)
new_idf = createsys(idf, sysdf, cp=cp, dhwtype=dhwsys.heatpump)
```

## Loading System Definition from CSV

For complex buildings with many zones, load the sysdf from a CSV file:

```python
sysdf = pd.read_csv("smallhotel.csv", index_col="zn")
new_idf = createsys(idf, sysdf, dhwtype=dhwsys.naturalgas)
```

CSV columns: `zn` (index), `sname`, `airloop`, `zonesys`, `fan`.

## Post-createsys Modifications

After creating the system, apply Eidx modifications as normal:

```python
new_idf[Eidx.economizer.get()] = "noeconomizer"
new_idf[Eidx.dcvsch.get()] = "office_openoff_occ"
new_idf[Eidx.fanstatic.get("ahu1 supply fan")] = Eidx.fanstatic.ip(3.5)
new_idf[Eidx.fanstatic.get("ahu1 extract fan")] = Eidx.fanstatic.ip(2.5)
new_idf[Eidx.heatrec.get()] = "always_off"
```

## Prerequisites

Before calling `createsys`, the IDF must contain:
- `designspecification:outdoorair` objects for each zone
- `sizing:zone` objects for each zone
- `zonecontrol:thermostat` objects for each zone
- Fan schedule referenced in `sysdf["fan"]` must exist in the IDF

## Notes

1. Object names in IDF fields must be **lowercase** (`createsys` is case-sensitive)
2. Zones sharing the same `sname` are served by a single air loop
3. Set `airloop = None` for zone-only systems (ptac, pthp, uhel, uhhw)
4. `hw` and `chw` accept a list for staged equipment — EnergyPlus sequences by capacity
5. `chw` accepts a tuple `(chiller, heat_rejection)` to pair a water-cooled chiller with its tower/fluid cooler
6. GSHP: always pair `pltsys.gshphtg` (hw) with `pltsys.gshpclg` (chw)
7. Water-cooled chillers require a heat rejection device: `coolingtower` or `fluidcooler`
8. `createsys` removes existing HVAC objects and replaces them — apply parameter changes after

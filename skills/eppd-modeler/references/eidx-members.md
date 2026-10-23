# Eidx Enum Members Reference

All members available in the current library version. Always verify live before writing code:

```bash
python -c "from eppd import Eidx; print(Eidx._member_names_)"
```

## Access Patterns (all members)

```python
idf[Eidx.lpd.get()]                    # all matching objects
idf[Eidx.lpd.get('zone1 lights')]      # exact name match
idf[Eidx.lpd.get(['z1 lights', 'z2 lights'])]  # multiple exact names
idf[Eidx.lpd.get(('bg',))]             # partial match — objects with 'bg' in name
idf[Eidx.lpd.get(('bg', 'fl1'))]       # partial match — 'bg' OR 'fl1' in name

idf[Eidx.lpd.get()] *= 0.8             # multiply
idf[Eidx.epd.get()] = Eidx.epd.ip(1.0) # set via .ip() for imperial input
idf[Eidx.economizer.get()] = 'NoEconomizer'  # set string
```

`.ip(x)` converts an imperial value `x` to the SI value EnergyPlus expects. Use only when the user provides imperial units; for SI inputs assign the raw number directly.

---

## Simulation Control

| Member | IDF Object | Description |
|--------|-----------|-------------|
| `runperiod` | `runperiod` | Run period begin/end month and day |
| `blddir` | `building` | Building north axis (orientation, degrees) |
| `sizingdb` | `sizingperiod:designday` | Sizing design day dry-bulb temperature; `.ip()` converts °F |
| `sizingrng` | `sizingperiod:designday` | Sizing design day dry-bulb range; `.ip()` converts Δ°F |
| `sizingwb` | `sizingperiod:designday` | Sizing design day wet-bulb temperature; `.ip()` converts °F |

---

## Building Loads

| Member | IDF Object | Description |
|--------|-----------|-------------|
| `lpd` | `lights` | Lighting power density (W/m²); `.ip()` converts W/sqft |
| `epd` | `electricequipment` | Equipment/plug load power density (W/m²); `.ip()` converts W/sqft |

```python
idf[Eidx.lpd.get()] *= 0.8              # reduce all lighting 20%
idf[Eidx.epd.get()] = Eidx.epd.ip(1.0) # set EPD to 1 W/sqft
idf[Eidx.lpd.get(('bg',))] = Eidx.lpd.ip(0.9)  # set basement zones to 0.9 W/sqft
```

---

## Ventilation & Infiltration

| Member | IDF Object | Description |
|--------|-----------|-------------|
| `oamethod` | `designspecification:outdoorair` | OA calculation method string (e.g. `'Sum'`, `'Maximum'`) |
| `oaperperson` | `designspecification:outdoorair` | OA per person (m³/s·person); `.ip()` converts cfm/person |
| `oapersqft` | `designspecification:outdoorair` | OA per floor area (m³/s·m²); `.ip()` converts cfm/sqft |
| `infil_method` | `zoneinfiltration:designflowrate` | Infiltration calculation method string |
| `infil_flowrate` | `zoneinfiltration:designflowrate` | Infiltration design flow rate |

```python
idf[Eidx.oaperperson.get()] = Eidx.oaperperson.ip(5)  # 5 cfm/person
idf[Eidx.infil_flowrate.get()] *= 0.5                  # reduce infiltration 50%
```

---

## HVAC — Air System

| Member | IDF Object | Description |
|--------|-----------|-------------|
| `economizer` | `controller:outdoorair` | Economizer control type string |
| `dcvsch` | `controller:outdoorair` | DCV availability schedule name |
| `maxsupplyT` | `setpointmanager:warmest` | Max supply air temperature (°C); `.ip()` converts °F |
| `faneff` | `fan:variablevolume` | Fan total efficiency (decimal 0–1) |
| `fanstatic` | `fan:variablevolume` | Fan design static pressure (Pa); `.ip()` converts in.w.g. |
| `heatrec` | `heatexchanger:airtoair:sensibleandlatent` | Heat recovery availability schedule name |

```python
idf[Eidx.economizer.get()] = 'NoEconomizer'
idf[Eidx.economizer.get()] = 'DifferentialEnthalpy'
idf[Eidx.economizer.get()] = 'DifferentialDryBulb'
idf[Eidx.dcvsch.get()] = 'office_openoff_occ'
idf[Eidx.faneff.get()] = 0.96
idf[Eidx.fanstatic.get('ahu1 supply fan')] = Eidx.fanstatic.ip(3.5)  # 3.5 in.w.g.
idf[Eidx.heatrec.get()] = 'always_off'
idf[Eidx.maxsupplyT.get()] = Eidx.maxsupplyT.ip(95)   # 95°F max supply
```

---

## Envelope

| Member | IDF Object | Description |
|--------|-----------|-------------|
| `nomass_rvalue` | `material:nomass` | NoMass R-value (m²·K/W); `.ip()` converts hr·ft²·°F/Btu |
| `conductivity_material` | `material` | Material thermal conductivity (W/m·K) |
| `insulation_thickness` | `material` | Material layer thickness (m) |
| `window_ufactor` | `windowmaterial:simpleglazingsystem` | Window U-factor (W/m²·K); `.ip()` converts Btu/hr·ft²·°F |
| `window_shgc` | `windowmaterial:simpleglazingsystem` | Window SHGC (dimensionless, 0–1) |

**NoMass R-value:**
```python
idf[Eidx.nomass_rvalue.get()] = Eidx.nomass_rvalue.ip(10)  # set R-10
idf[Eidx.nomass_rvalue.get()] *= 1.2                        # increase 20%
```

**Material (thickness-based) R-value:**
```python
# Set to R-20 (thickness = conductivity × R)
idf[Eidx.insulation_thickness.get()] = idf[Eidx.conductivity_material.get()] * Eidx.nomass_rvalue.ip(20)
idf[Eidx.insulation_thickness.get()] *= 1.1   # increase R-value 10%
```

**Windows:**
```python
idf[Eidx.window_ufactor.get()] = Eidx.window_ufactor.ip(0.3)  # U-0.30 Btu/hr·ft²·°F
idf[Eidx.window_shgc.get()] = 0.25
```

---

## Zone Info

| Member | IDF Object | Description |
|--------|-----------|-------------|
| `znames` | `zone` | Zone names — used as sysdf index for `createsys` |

```python
sysdf = pd.DataFrame(index=idf[Eidx.znames.get()].index)
```

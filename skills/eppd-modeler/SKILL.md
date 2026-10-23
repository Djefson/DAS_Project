---
name: eppd-modeler
description: "Create and modify EnergyPlus IDF building energy models using the eppd library. Use when: (1) User mentions IDF files, EnergyPlus, energy modeling, or building simulation, (2) Modifying building parameters like lighting power density (LPD), equipment power density (EPD), HVAC systems, economizers, fan efficiency, (3) Setting up batch simulations with weather files (.epw), (4) Creating parametric studies or design alternatives, (5) Working with the Eidx enum for building component access. Output is always a ready-to-run Python script file — never execute it."
---

# EnergyPlus eppd Modeler

Work with EnergyPlus IDF files using the eppd library to create parametric building energy models and run batch simulations.

## Guidelines

1. **Write script, don't run it**: The deliverable is a `.py` file. Write it and stop — never execute the assembled case script or `run_batch()` yourself. Short `python -c` discovery commands via Bash are permitted only for library-level queries (Eidx member names, Sobj member names, HVAC system keys) — never to inspect a specific IDF file. The script must include `run_batch(cases)` and the output processing block so the user can run it end-to-end.
2. **Library verification**: Verify with `python -c 'import eppd; print(eppd.__version__)'`. If it fails, stop and tell the user to install/activate the eppd environment — do not attempt to install it yourself.
3. **Minimal changes**: Only implement explicitly requested modifications
4. **Compact code**: Avoid unnecessary indirection or abstraction
5. **Clean output**: Don't add confirmation print statements unless requested
6. **Required imports**: Use `from eppd import *` for all eppd functions. Also always include `import pandas as pd` and `import numpy as np` — these are NOT exported by eppd and must be imported explicitly.
7. **Use Eidx enum only**: Only implement modifications available in the Eidx enum. Before concluding a member is unavailable, do a substring search: `[m for m in Eidx._member_names_ if 'keyword' in m.lower()]`. If still not found, inform the user it needs to be added to Eidx. Always discover live members before writing parameter code (see [Eidx Parameter Access](#eidx-parameter-access))
8. **Always include output processing in new scripts**: When creating a script from scratch, always end with the full output processing template from the [Processing Outputs](#processing-outputs) section. When *modifying* an existing script, do not add the output block unless requested.
9. **Never read or parse IDF files as plain text**: Do not use `cat`, file I/O, or any text-based read on `.idf` files. Always load via `read_idf()` and inspect the resulting object through the eppd library (`Eidx`, `createsys`, `drop_objects`, etc.)

## Core Workflow

### Reading IDF Files

Read a single IDF file:
```python
baseline = read_idf('baseline.idf')
# Drop objects re-added via apnd() on write to avoid duplicate object errors
baseline.drop_objects(["simulationcontrol", "outputcontrol:table:style", "output:table:summaryreports"])
```

### Inspecting IDF Objects

Do not load or inspect a specific IDF file before writing the script. Scripts must be written generically so they work across different IDF files. Use Eidx-based access patterns that resolve at runtime, not hardcoded values discovered before writing.

If the user needs IDF-specific introspection (e.g. to find object names for filtering), include the inspection code as commented examples inside the script so they can run it themselves:

```python
# Uncomment to discover object names in your IDF:
# idf['lights', :, 1].index.get_level_values('name')
# idf['schedule:compact', :, 1].index.get_level_values('name')
# idf.data.index.get_level_values('object').unique()
```

**Never use** `idf.get_objects('object:type')` with arguments — `get_objects()` takes no parameters.

### Creating Modified Cases

Standard pattern for creating a modified case:

```python
# -- Brief case description (e.g., reduce lighting by 20%) --
fname = 'descriptive_case_name'
modified_idf = baseline.copy()

# Make modifications using Eidx
modified_idf[Eidx.lpd.get()] *= 0.8

modified_idf.write_idf(fname + '.idf', apnd([Sobj.simctl, Sobj.xmlout, Sobj.allsummary, Sobj.sysoa]))
cases[fname] = (fname + '.idf', weadir / 'Chicago.epw')
```

Key patterns:
- Use `# -- description --` comment style for each case
- Use `fname` as the case name variable (snake_case)
- Always `.copy()` the base IDF before modifications
- Use `apnd()` with `Sobj` enum members to configure simulation outputs
- Keep case definition together with modifications

### Eidx Parameter Access

**Before writing any parameter modification code, run the following command via Bash and read the output into context.** The static reference in [references/eidx-members.md](references/eidx-members.md) may be outdated — always use the live output:

```bash
python -c "from eppd import Eidx; print(Eidx._member_names_)"
```

The Eidx enum provides access to building parameters. Access patterns:

**All matching objects:**
```python
idf[Eidx.lpd.get()]  # All lighting power density objects
```

**Filter by name (exact match on the IDF object name, not the zone name):**
```python
idf[Eidx.lpd.get('zone1 lighting')]  # Single object — must match the Lights object name, not zone name
idf[Eidx.lpd.get(['zone1 lighting', 'zone2 lighting'])]  # Multiple objects
```
Discover actual object names before filtering: `idf['lights', :, 1].index.get_level_values('name')`

**Filter by partial match (substring on IDF object name, OR across multiple terms):**
```python
idf[Eidx.lpd.get(('bg',))]           # objects with 'bg' in name
idf[Eidx.lpd.get(('bg', 'fl1'))]     # objects with 'bg' OR 'fl1' in name
```

**Common operations:**
- Multiply: `idf[Eidx.lpd.get()] *= 1.2` (increase by 20%)
- Set value: `idf[Eidx.epd.get()] = Eidx.epd.ip(1.0)` (set to 1 W/sqft)
- Set string: `idf[Eidx.economizer.get()] = 'NoEconomizer'`

**Unit conversion:**
`.ip(x)` converts an imperial value `x` to the SI value EnergyPlus expects. Use it only when the user provides imperial units. For SI inputs, assign the raw number directly.
```python
Eidx.epd.ip(1.0)  # converts 1 W/sqft → SI equivalent
```

### Envelope insulation

To change insulation for Envelope, wall or roof, ensure user specifies if it is for "material" or "nomass":

**NoMass materials (R-value directly):**
 - Set "nomass" R-Value to R-10: `idf[Eidx.nomass_rvalue.get()] = Eidx.nomass_rvalue.ip(10)`
 - Increase "nomass" R-Value by 20%: `idf[Eidx.nomass_rvalue.get()] *= 1.2`

**Material objects (thickness-based, requires conductivity):**
 - Set "material" R-Value to R-10: `idf[Eidx.insulation_thickness.get()] = idf[Eidx.conductivity_material.get()] * Eidx.nomass_rvalue.ip(10)`  # nomass_rvalue.ip() converts R-10 imperial → SI (m²·K/W); thickness = conductivity × R
 - Increase "material" R-Value by 10%: `idf[Eidx.insulation_thickness.get()] *= 1.1`
 - Reduce "material" R-Value by 15%: `idf[Eidx.insulation_thickness.get()] *= 0.85`

Note: For material objects, R-value changes require thickness adjustments (thickness = conductivity × R-value).


### Sobj Output Configuration

**Before writing any `apnd()` calls, run the following command via Bash and read the output into context** to know what output objects are available in the installed library version:

```bash
python -c "from eppd import Sobj; print(Sobj._member_names_)"
```

### Batch Simulation Setup

Initialize cases dictionary at the beginning of the script:
```python
from eppd import *
from pathlib import Path
import pandas as pd
import numpy as np

weadir = Path('/path/to/weather/dir').expanduser()  # ask user for actual path
cases = {}
```

Add cases using pattern:
```python
cases[fname] = (fname + '.idf', weadir / 'weather_file.epw')
```

**Weather file handling:**
- Always ask the user for the weather directory path and exact `.epw` filename — do not search the filesystem for them
- If the user has already provided a weather path earlier in the conversation, use it without re-asking
- If the user provides a location name but not a path/filename, ask for both before writing the script
- Within a single script, use the first specified weather file as default for all cases unless the user specifies otherwise
- Don't create additional variables for individual weather files

## HVAC System Configuration

For modifying HVAC systems, coil types, airloop configurations, or plant equipment, see the comprehensive guide:

**[references/hvac-systems.md](references/hvac-systems.md)**

This reference covers:
- `createsys` workflow and sysdf DataFrame format
- Airloop strings and zone system options
- `PlantConfig` + `pltsys` for central plant definition
- Complete examples for all common system types
- Domestic hot water and post-createsys modifications

Only load this reference when the user needs to modify HVAC system configurations. When loaded, run only the library-level discovery functions via Bash (coil types, zone systems, plant equipment keys) — do not inspect the IDF to discover fan schedules or zone names. Ask the user for the fan schedule name if it is not already known.



## Processing Outputs

**Always include this block at the end of every new script** so the user can run it to review results. Do not execute it yourself.

```python
run_batch(cases)

res = get_batch_xml(cases)
eso = get_batch_eso(cases)

pd.set_option('display.float_format', lambda x: f'{x:,.2f}')
print("\n" + "=" * 60, "Unmet Hours:\n", res.unmet_hours, "\n" + "=" * 60)
for n, ea in eso.esosum.items(): print("\n", n, ":Eso Sum--------\n", ea)
print("\n" + "=" * 60, "EUI Distribution:\n", res.eui_dist, "\n" + "=" * 60)

# Access patterns:
# res.elec              # All cases' electricity end-use DataFrame
# res.gas               # All cases' gas end-use DataFrame
# res.unmet_hours       # Unmet hours DataFrame
# res.eui_dist          # EUI distribution across cases
# eso.<case_name>       # Hourly ESO DataFrame for a specific case
```

**For extended output processing (costs, end-use comparisons, ESO time-series), see [references/examples.md](references/examples.md)**

## Additional Resources

- **Eidx enum members**: See [references/eidx-members.md](references/eidx-members.md)
- **HVAC system configuration**: See [references/hvac-systems.md](references/hvac-systems.md)
- **Template script**: See [scripts/case_template.py](scripts/case_template.py)

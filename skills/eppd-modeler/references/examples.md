# Output Processing Examples

Extended output processing patterns beyond the basic block in SKILL.md.

## Energy End-Use Comparison

```python
# Electricity and gas end-uses across all cases
print(res.elec)   # DataFrame: cases × end-uses, electricity
print(res.gas)    # DataFrame: cases × end-uses, gas

# Total energy per case
total_elec = res.elec.sum(axis=1)
total_gas  = res.gas.sum(axis=1)
print(pd.DataFrame({'elec': total_elec, 'gas': total_gas}))
```

## Cost Comparison

```python
# Adjust rates and units to match your simulation output
elec_rate = 0.12   # $/kWh
gas_rate  = 1.00   # $/therm

elec_cost  = res.elec.sum(axis=1) * elec_rate
gas_cost   = res.gas.sum(axis=1) * gas_rate
total_cost = elec_cost + gas_cost

savings = total_cost['baseline'] - total_cost  # requires 'baseline' case in dict
print(pd.DataFrame({
    'elec_cost': elec_cost,
    'gas_cost': gas_cost,
    'total_cost': total_cost,
    'savings_vs_baseline': savings,
}))
```

## ESO Time-Series Data

```python
# Hourly data for a specific case
h = eso.baseline
cfm   = h['Fan Air Mass Flow Rate'] * 1757
tzone = h['Zone Mean Air Temperature'] * 1.8 + 32
unmet = h['Zone Heating Setpoint Not Met While Occupied Time']

# Plot zones with unmet hours
tzone.loc[(unmet > 0).values].plot(style='+')
```

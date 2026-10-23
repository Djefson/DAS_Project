"""
Bharath Karambakkam
e-mail:kBharathk@gmail.com
function: Domestic Hot water sys used by createsys function
"""

from types import SimpleNamespace

dhwtypes = {"naturalgas", "electricity", "heatpump"}
dhwsys = SimpleNamespace(**{ea: ea for ea in dhwtypes})


def dhwloop(zndhw: list, systype: str):
    """Generate domestic hot water loop IDF string.

    Args:
        zndhw: List of zones with DHW equipment (wateruse:equipment objects)
        systype: Type of DHW heating system

    Returns:
        Complete IDF string for DHW loop including heater, pump, and demand side

    Raises:
        ValueError: If no DHW zones provided or invalid system type

    Notes:
        - All energyplus class definitions are in lowercase (Python is case-sensitive)
        - Heat pump option may consume more energy than electricity in some months
          (needs investigation)
    """
    if not zndhw:
        raise ValueError(
            "No DHW zones provided. At least one zone with water use equipment is required."
        )

    valid_types = {"naturalgas", "electricity", "heatpump"}
    if systype not in valid_types:
        raise ValueError(
            f"Invalid DHW system type: {systype}. Must be one of {valid_types}"
        )
    match systype:
        case "naturalgas" | "electricity":
            ht = (
                f"waterheater:mixed,dhw heater,2.0,dhw setpoint,2.0,82.2222,cycle,autosize,,,,{systype},0.8,,20,electricity,0.8,,electricity,,outdoors,,,dhwhp oa node,6.0,,6.0,,,,,dhwheater inlet,dhwheater outlet,1.0,,,1.0,autosize,autosize,1.5;"
                "plantequipmentlist,dhw equipment list,waterheater:mixed,dhw heater;"
                "branch,dhwheater supply side branch,,waterheater:mixed,dhw heater,dhwheater inlet,dhwheater outlet;"
            )
        case "heatpump":
            # need to check why heatpump is consuming more energy than electricity some months.
            ht = (
                "waterheater:mixed,dhw heater,2.0,dhw setpoint,2.0,82.2222,cycle,autosize,,,,electricity,0.8,,20,electricity,0.8,,electricity,,outdoors,,,dhwhp oa node,6.0,,6.0,,,,,dhwheater inlet,dhwheater outlet,1.0,dhwheater condenser outlet,dhwheater condenser inlet,1.0,autosize,autosize,1.5;"
                "plantequipmentlist,dhw equipment list,waterheater:heatpump:pumpedcondenser,dhw heatpump heater;"
                "branch,dhwheater supply side branch,,WaterHeater:HeatPump:PumpedCondenser,dhw heatpump heater,dhwheater inlet,dhwheater outlet;"
                "waterheater:heatpump:pumpedcondenser,dhw heatpump heater,on 24/7,dhw setpoint,2.0,dhwheater condenser inlet,dhwheater condenser outlet,autocalculate,autocalculate,outdooraironly,,,dhwhp oa node,dhw hp exhaust node,,,,waterheater:mixed,dhw heater,dhwheater inlet,dhwheater outlet,coil:waterheating:airtowaterheatpump:pumped,dhwhp coil,5.0,,outdoors,,fan:systemmodel,dhwhp fan,blowthrough,15.0,5.0,outdoors;"
                "fan:systemmodel,dhwhp fan,on 24/7,dhwhp oa node,dhwhp evap inlet node,0.2685,discrete,0.0,100.0,0.9,1.0,autosize,totalefficiencyandpressure,,,0.70;"
                "coil:waterheating:airtowaterheatpump:pumped,dhwhp coil,4000.0,3.2,0.6956,29.44,22.22,55.72,autocalculate,autocalculate,no,no,no,150.0,0.1,dhwhp evap inlet node,dhw hp exhaust node,dhwheater condenser inlet,dhwheater condenser outlet,100.0,,5.0,wetbulbtemperature,hpwhheatingcapftemp,,,hpwhheatingcopftemp,,,hpwhplffplr;"
            )
    return ht + (
        "WaterHeater:Sizing,dhw heater,PeakDraw,0.538503,2.0,1.0;"
        "plantloop,dhw loop,water,,dhw operation,dhw supply side outlet node,60,10.00,autosize,0.000000,autocalculate,dhw supply side inlet node,dhw supply side outlet node,dhw supply side branch list,dhw supply side connector list,dhw demand side inlet node,dhw demand side outlet node,dhw demand side branch list,dhw demand side connector list,optimal;"
        "sizing:plant,dhw loop,heating,60,5.0;"
        "outdoorair:node,dhwhp oa node;"
        "setpointmanager:scheduled,dhw loop setpoint manager,temperature,dhw setpoint,dhw supply side outlet node;"
        "plantequipmentoperationschemes,dhw operation,plantequipmentoperation:heatingload,dhw operation scheme,on 24/7;"
        "plantequipmentoperation:heatingload,dhw operation scheme,0.0,1000000000000000,dhw equipment list;"
        "schedule:compact,ambient temps,temperature,through: 12/31,for: alldays,until: 24:00,22.0;"
        "schedule:compact,dhw setpoint,temperature,through: 12/31,for: alldays,until: 24:00,60.0;"
        # supply side
        "branch,dhw supply side inlet branch,,pump:variablespeed,dhw supply pump,dhw supply side inlet node,dhw supply pump water outlet node;"
        "pump:variablespeed,dhw supply pump,dhw supply side inlet node,dhw supply pump water outlet node,autosize,179345.39,autosize,0.60,0.00,0.0000,1.0000,0.0000,0.0000,0.000000,intermittent;"
        "branch,dhw supply side bypass branch,,pipe:adiabatic,dhw supply side bypass pipe,dhw supply side bypass pipe inlet node,dhw supply side bypass pipe outlet node;"
        "pipe:adiabatic,dhw supply side bypass pipe,dhw supply side bypass pipe inlet node,dhw supply side bypass pipe outlet node;"
        "branch,dhw supply side outlet branch,,pipe:adiabatic,dhw supply side outlet branch pipe,dhw supply side outlet branch pipe inlet node,dhw supply side outlet node;"
        "pipe:adiabatic,dhw supply side outlet branch pipe,dhw supply side outlet branch pipe inlet node,dhw supply side outlet node;"
        "connectorlist,dhw supply side connector list,connector:splitter,dhw supply splitter,connector:mixer,dhw supply mixer;"
        "connector:mixer,dhw supply mixer,dhw supply side outlet branch,dhw supply side bypass branch, dhwheater supply side branch;"
        "connector:splitter,dhw supply splitter,dhw supply side inlet branch,dhw supply side bypass branch, dhwheater supply side branch;"
        "branchlist,dhw supply side branch list,dhw supply side inlet branch,dhw supply side bypass branch, dhwheater supply side branch,dhw supply side outlet branch;"
        # demand side
        "branch,dhw demand side bypass branch,,pipe:adiabatic,dhw demand side bypass pipe,dhw demand side bypass pipe inlet node,dhw demand side bypass pipe outlet node;"
        "pipe:adiabatic,dhw demand side bypass pipe,dhw demand side bypass pipe inlet node,dhw demand side bypass pipe outlet node;"
        "branch,dhw demand side inlet branch,,pipe:adiabatic,dhw demand side inlet branch pipe,dhw demand side inlet node,dhw demand side inlet branch pipe outlet;"
        "pipe:adiabatic,dhw demand side inlet branch pipe,dhw demand side inlet node,dhw demand side inlet branch pipe outlet;"
        "branch,dhw demand side outlet branch,,pipe:adiabatic,dhw demand side outlet branch pipe,dhw demand side outlet branch pipe inlet,dhw demand side outlet node;"
        "pipe:adiabatic,dhw demand side outlet branch pipe,dhw demand side outlet branch pipe inlet,dhw demand side outlet node;"
        "connectorlist,dhw demand side connector list,connector:splitter,dhw demand splitter,connector:mixer,dhw demand mixer;"
        f"connector:mixer,dhw demand mixer,dhw demand side outlet branch,dhw demand side bypass branch"
        f"{' '.join(f',{s} dhw demand side branch' for s in zndhw)};"
        f"connector:splitter,dhw demand splitter,dhw demand side inlet branch,dhw demand side bypass branch"
        f"{' '.join(f',{s} dhw demand side branch' for s in zndhw)};"
        f"branchlist,dhw demand side branch list,dhw demand side inlet branch,dhw demand side bypass branch"
        f"{' '.join(f',{s} dhw demand side branch' for s in zndhw)}"
        f",dhw demand side outlet branch;"
        f"{' '.join(f'wateruse:connections,{zd} dhw connection,{zd} dhw inlet node,{zd} dhw outlet node,,,,,,,,{zd};' for zd in zndhw)}"
        f"{' '.join(f'branch,{zd} dhw demand side branch,,wateruse:connections,{zd} dhw connection,{zd} dhw inlet node,{zd} dhw outlet node;' for zd in zndhw)}"
    )

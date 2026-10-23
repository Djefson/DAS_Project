"""EnergyPlus output variable and report configurations.

This module provides predefined output variable strings for EnergyPlus simulations
as a discoverable Enum. Use these to easily add output requests to IDF files via
the write_idf append_string parameter.

Example:
    >>> from eppd import apnd, Sobj
    >>>
    >>> model = read_idf('baseline.idf')
    >>>
    >>> # Add zone temperature outputs for all zones
    >>> output_str = apnd([Sobj.znt], vlist=['*'])
    >>> model.write_idf('output.idf', append_string=output_str)
    >>>
    >>> # Add specific zone outputs
    >>> output_str = apnd([Sobj.znt, Sobj.znlt], vlist=['Zone 1', 'Zone 2'])
    >>> model.write_idf('output.idf', append_string=output_str)
    >>>
    >>> # Add simulation control and summary reports
    >>> output_str = apnd([Sobj.simctl, Sobj.allsummary, Sobj.rdd])
"""

from enum import Enum


class Sobj(Enum):
    """EnergyPlus output variable and report templates.

    Each member name is a short discoverable key; the value is the
    raw EnergyPlus IDF string.  Members that target a specific object
    use ``{sval}`` as a placeholder — the :func:`apnd` function fills
    this in from *vlist*.

    Groupings
    ---------
    Simulation control / reports
        simctl, xmlout, allsummary, rdd, mtr_el, mtr_gas, mtr_hw, mtr_st, mtr_chw
    Weather / schedules
        oadt, sch, lgt
    Zone loads
        znlt, zneq, znpl, znoa, znt
    Zone HVAC
        zntht, zntcl, znsetptht, znsetptcl
    Unmet hours
        unmetht, unmetcl, unmetht_occ, unmetcl_occ
    Coils / fans
        htcoil, clcoil, clcoilsensible, fanw, fanflow, econstatus, sysoa, sysair
    Boiler
        blrgas, blrti, blrto, blrflow
    Chiller / cooling tower
        chillerelec, ctti, ctto, ctflow, ctfan, pumpw, pumpflow
    System nodes
        nodet, nodestpt, nodeflow
    """

    # Simulation Control and Reports
    simctl     = "simulationcontrol,yes,yes,yes,no,yes,no,1;"
    xmlout     = "outputcontrol:table:style,xmlandhtml,inchpound;"
    allsummary = "output:table:summaryreports,allsummary;"
    rdd        = "output:variabledictionary, idf;"
    mtr_el     = "output:meter,electricity:facility;"
    mtr_gas    = "output:meter,naturalgas:facility;"
    mtr_hw     = "output:meter,districtheatingwater:facility;"
    mtr_st     = "output:meter,districtheatingsteam:facility;"
    mtr_chw    = "output:meter,districtcooling:facility;"

    # Weather and Schedules
    oadt = "output:variable,{sval},site outdoor air drybulb temperature,hourly;" # !- zone average [c]
    sch  = "output:variable,{sval},schedule value,hourly;" # !- zone average []
    lgt  = "Output:Variable,{sval},Lights Electricity Rate,hourly;" # !- Zone Average [W]

    # Zone Loads
    znlt = "output:variable,{sval},zone lights electricity rate,hourly;" # !- zone average [w]
    zneq = "output:variable,{sval},zone electric equipment electricity rate,hourly;" # !- zone average [w]
    znpl = "output:variable,{sval},zone people occupant count,hourly;" # !- zone average []
    znoa = "output:variable,{sval},zone mechanical ventilation mass flow rate,hourly;" # !- hvac average [kg/s]
    znt  = "Output:Variable,{sval},Zone Mean Air Temperature,hourly;" # !- Zone Average [C]
    zrh  = "Output:Variable,*,Zone Air Relative Humidity,hourly;" # !- HVAC Average [%]
    zW   = "Output:Variable,*,Zone Air Humidity Ratio,hourly;" # !- HVAC Average []

    # Zone HVAC
    zntht     = "output:variable,{sval},zone air terminal sensible heating energy,hourly;" # !- hvac sum [j]
    zntcl     = "output:variable,{sval},zone air terminal sensible cooling energy,hourly;" # !- hvac sum [j]
    znsetptht = "output:variable,{sval},zone thermostat heating setpoint temperature,hourly;" # !- hvac average [c]
    znsetptcl = "output:variable,{sval},zone thermostat cooling setpoint temperature,hourly;" # !- hvac average [c]

    # Unmet Hours
    unmetht     = "output:variable,{sval},zone heating setpoint not met time,hourly;" # !- zone sum [hr]
    unmetcl     = "output:variable,{sval},zone cooling setpoint not met time,hourly;" # !- zone sum [hr]
    unmetht_occ = "output:variable,{sval},zone heating setpoint not met while occupied time,hourly;" # !- zone sum [hr]
    unmetcl_occ = "output:variable,{sval},zone cooling setpoint not met while occupied time,hourly;" # !- zone sum [hr]

    # HVAC Coils and Fans
    htcoil         = "output:variable,{sval},heating coil heating energy,hourly;" # !- hvac sum [j]
    clcoil         = "output:variable,{sval},cooling coil total cooling energy,hourly;" # !- hvac sum [j]
    clcoilsensible = "output:variable,{sval},cooling coil total cooling energy,hourly;" # !- hvac sum [j]
    fanw           = "output:variable,{sval},fan electricity rate,hourly;" # !- hvac average [w]
    fanflow        = "output:variable,{sval},fan air mass flow rate,hourly;" # !- hvac average [kg/s]
    econstatus     = "output:variable,{sval},air system outdoor air economizer status,hourly;" # !- hvac average []
    sysoa          = "output:variable,{sval},air system outdoor air mass flow rate,hourly;" # !- hvac average [kg/s]
    sysair         = "output:variable,{sval},air system mixed air mass flow rate,hourly;" # !- hvac average [kg/s]

    # Plant Equipment - Boiler
    blrgas  = "output:variable,{sval},boiler naturalgas energy,hourly;" # !- hvac sum [j]
    blrti   = "output:variable,{sval},boiler inlet temperature,hourly;" # !- hvac average [c]
    blrto   = "output:variable,{sval},boiler outlet temperature,hourly;" # !- hvac average [c]
    blrflow = "output:variable,{sval},boiler mass flow rate,hourly;" # !- hvac average [kg/s]

    # Plant Equipment - Chiller / Cooling Tower
    chillerelec = "output:variable,{sval},chiller electricity rate,hourly;" # !- hvac average [w]
    ctti        = "output:variable,{sval},cooling tower inlet temperature,hourly;" # !- hvac average [c]
    ctto        = "output:variable,{sval},cooling tower outlet temperature,hourly;" # !- hvac average [c]
    ctflow      = "output:variable,{sval},cooling tower mass flow rate,hourly;" # !- hvac average [kg/s]
    ctfan       = "output:variable,{sval},cooling tower fan electricity rate,hourly;" # !- hvac average [w]
    pumpw       = "output:variable,{sval},pump electricity rate,hourly;" # !- hvac average [w]
    pumpflow    = "output:variable,{sval},pump mass flow rate,hourly;" # !- hvac average [kg/s]

    # System Nodes
    nodet    = "output:variable,{sval},system node temperature,hourly;" # !- hvac average [c]
    nodestpt = "output:variable,{sval},system node setpoint temperature,hourly;" # !- hvac average [c]
    nodeflow = "output:variable,{sval},system node mass flow rate,hourly;" # !- hvac average [kg/s]


def apnd(apndlst: list[Sobj], vlist: list[str] = ["*"]) -> str:
    """Generate EnergyPlus output variable strings from report templates.

    Args:
        apndlst: List of :class:`Sobj` members to include.
        vlist:  List of values to apply to ``*`` in output:variable).

    Returns:
        Formatted string of EnergyPlus output variables to append to IDF.

    Example:
        >>> output = apnd([Sobj.znt])
        >>> print(output)
        Output:Variable,*,Zone Mean Air Temperature,hourly; !- Zone Average [C]

        >>> output = apnd([Sobj.znt, Sobj.znlt], vlist=['Core', 'Perimeter'])

        >>> output = apnd([Sobj.simctl, Sobj.allsummary])
    """
    return "\n" + "\n".join(
        [("\n".join([a.value for a in apndlst])).format(sval=ea) for ea in vlist]
    )

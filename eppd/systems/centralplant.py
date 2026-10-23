"""
Bharath Karambakkam
e-mail:kBharathk@gmail.com
function: Central plant systems utilized by createsys function
"""

from collections import namedtuple
from types import SimpleNamespace

# sysname: Named tuple structure for defining plant equipment
# Each plant equipment (boiler, chiller, etc.) is represented as a sysname with:
#   - name (str): Equipment identifier used in IDF object naming (e.g., 'boiler', 'aircooledchiller')
#   - fun (callable): Function that generates IDF string for this equipment
#   - obj (str): EnergyPlus object type (e.g., 'boiler:hotwater', 'chiller:electric:eir')
#   - desc (str): Human-readable description to help LLMs understand user intent when using SKILL.md
sysname = namedtuple("sysname", "name fun obj desc")


# Central plants
def waterloop(
    lp: str,
    cplist: list,
    htc=None,
    clc=None,
    znhtc=None,
    znclc=None,
    znhwbb=None,
):
    """Generate water loop plant system IDF string.

    Args:
        lp: Loop type ('hw' for hot water, 'chw' for chilled water, 'whp' for water loop heat pump)
        cplist: List of plant equipment (sysname tuples or tuples for compound equipment like water-cooled chillers)
        htc: List of air loop systems with heating coils (default: None)
        clc: List of air loop systems with cooling coils (default: None)
        znhtc: List of zones with heating coils (default: None)
        znclc: List of zones with cooling coils (default: None)
        znhwbb: List of zones with hot water baseboards (default: None)

    Returns:
        Complete IDF string for water loop including supply, demand, and equipment
    """

    # Initialize default empty lists
    htc = htc or []
    clc = clc or []
    znhtc = znhtc or []
    znclc = znclc or []
    znhwbb = znhwbb or []

    if not isinstance(cplist, list):
        cplist = [cplist]

    # if user provided a tupple for watercooled chiller etc extract primary system.
    eqlist = [ea if isinstance(ea, sysname) else ea[0] for ea in cplist]

    wlp = (
        f"plantloop,{lp} loop,water,,{lp} operation,{lp} supply side outlet node,100.00,0.00,autosize,0.000000,autocalculate,{lp} supply side inlet node,{lp} supply side outlet node,{lp} supply side branch list,{lp} supply side connector list,{lp} demand side inlet node,{lp} demand side outlet node,{lp} demand side branch list,{lp} demand side connector list,sequentialload,,singlesetpoint;"
        # supply side
        f"branch,{lp} supply side inlet branch,,pump:variablespeed,{lp} supply pump,{lp} supply side inlet node,{lp} supply pump water outlet node;"
        f"pump:variablespeed,{lp} supply pump,{lp} supply side inlet node,{lp} supply pump water outlet node,autosize,179345.39,autosize,0.60,0.00,0.0000,1.0000,0.0000,0.0000,0.000000,intermittent;"
        f"branch,{lp} supply side bypass branch,,pipe:adiabatic,{lp} supply side bypass pipe,{lp} supply side bypass pipe inlet node,{lp} supply side bypass pipe outlet node;"
        f"pipe:adiabatic,{lp} supply side bypass pipe,{lp} supply side bypass pipe inlet node,{lp} supply side bypass pipe outlet node;"
        f"branch,{lp} supply side outlet branch,,pipe:adiabatic,{lp} supply side outlet branch pipe,{lp} supply side outlet branch pipe inlet node,{lp} supply side outlet node;"
        f"pipe:adiabatic,{lp} supply side outlet branch pipe,{lp} supply side outlet branch pipe inlet node,{lp} supply side outlet node;"
        f"connectorlist,{lp} supply side connector list,connector:splitter,{lp} supply splitter,connector:mixer,{lp} supply mixer;"
        f"connector:mixer,{lp} supply mixer,{lp} supply side outlet branch,{lp} supply side bypass branch"
        f"{' '.join(f',{s.name}{i} supply side branch' for i, s in enumerate(eqlist))};"
        f"connector:splitter,{lp} supply splitter,{lp} supply side inlet branch,{lp} supply side bypass branch"
        f"{' '.join(f',{s.name}{i} supply side branch' for i, s in enumerate(eqlist))};"
        f"branchlist,{lp} supply side branch list,{lp} supply side inlet branch,{lp} supply side bypass branch"
        f"{' '.join(f',{s.name}{i} supply side branch' for i, s in enumerate(eqlist))}"
        f",{lp} supply side outlet branch;"
        #
        # demand side
        f"branch,{lp} demand side bypass branch,,pipe:adiabatic,{lp} demand side bypass pipe,{lp} demand side bypass pipe inlet node,{lp} demand side bypass pipe outlet node;"
        f"pipe:adiabatic,{lp} demand side bypass pipe,{lp} demand side bypass pipe inlet node,{lp} demand side bypass pipe outlet node;"
        f"branch,{lp} demand side inlet branch,,pipe:adiabatic,{lp} demand side inlet branch pipe,{lp} demand side inlet node,{lp} demand side inlet branch pipe outlet;"
        f"pipe:adiabatic,{lp} demand side inlet branch pipe,{lp} demand side inlet node,{lp} demand side inlet branch pipe outlet;"
        f"branch,{lp} demand side outlet branch,,pipe:adiabatic,{lp} demand side outlet branch pipe,{lp} demand side outlet branch pipe inlet,{lp} demand side outlet node;"
        f"pipe:adiabatic,{lp} demand side outlet branch pipe,{lp} demand side outlet branch pipe inlet,{lp} demand side outlet node;"
        f"connectorlist,{lp} demand side connector list,connector:splitter,{lp} demand splitter,connector:mixer,{lp} demand mixer;"
        f"connector:mixer,{lp} demand mixer,{lp} demand side outlet branch,{lp} demand side bypass branch"
        f"{' '.join(f',{s} hw demand side branch' for s in htc)}"
        f"{' '.join(f',{s} chw demand side branch' for s in clc)}"
        f"{' '.join(f',{z} zone hw demand side branch' for z in znhtc)}"
        f"{' '.join(f',{z} zone chw demand side branch' for z in znclc)}"
        f"{' '.join(f',{z} zone baseboard demand side branch' for z in znhwbb)};"
        f"connector:splitter,{lp} demand splitter,{lp} demand side inlet branch,{lp} demand side bypass branch"
        f"{' '.join(f',{s} hw demand side branch' for s in htc)}"
        f"{' '.join(f',{s} chw demand side branch' for s in clc)}"
        f"{' '.join(f',{z} zone hw demand side branch' for z in znhtc)}"
        f"{' '.join(f',{z} zone chw demand side branch' for z in znclc)}"
        f"{' '.join(f',{z} zone baseboard demand side branch' for z in znhwbb)};"
        f"branchlist,{lp} demand side branch list,{lp} demand side inlet branch,{lp} demand side bypass branch"
        f"{' '.join(f',{s} hw demand side branch' for s in htc)}"
        f"{' '.join(f',{s} chw demand side branch' for s in clc)}"
        f"{' '.join(f',{z} zone hw demand side branch' for z in znhtc)}"
        f"{' '.join(f',{z} zone chw demand side branch' for z in znclc)}"
        f"{' '.join(f',{z} zone baseboard demand side branch' for z in znhwbb)}"
        f",{lp} demand side outlet branch;"
    )

    for i, (fa, par) in enumerate(zip(eqlist, cplist)):
        wlp += fa.fun(i, par)

    match lp:
        case "hw":
            return wlp + (
                "sizing:plant,hw loop,heating,80.00,10.00;"
                "setpointmanager:scheduled,hw loop setpoint manager,temperature,hot water flow set point temperature: always 80.0 c,hw supply side outlet node;"
                "plantequipmentoperationschemes, hw operation, plantequipmentoperation:heatingload,hw scheme 1,on 24/7;"
                "plantequipmentoperation:heatingload,hw scheme 1,0.00,1000000000000000.00,hw scheme 1 equipment list;"
                f"plantequipmentlist,{lp} scheme 1 equipment list"
                f"{' '.join(f',{s.obj},{s.name}{i}' for i, s in enumerate(eqlist))};"
            )

        case "chw":
            return wlp + (
                "sizing:plant,chw loop,cooling,6.00,4.00;"
                "setpointmanager:scheduled,chw loop setpoint manager,temperature,chilled water flow set point temperature: always 6 c,chw supply side outlet node;"
                "plantequipmentoperationschemes,chw operation,plantequipmentoperation:coolingload,chw scheme 1,on 24/7;"
                "plantequipmentoperation:coolingload,chw scheme 1,0.00,1000000000000000.00,chw scheme 1 equipment list;"
                f"plantequipmentlist,{lp} scheme 1 equipment list"
                f"{' '.join(f',{s.obj},{s.name}{i}' for i, s in enumerate(eqlist))};"
            )

        case "whp":
            return wlp + (
                # ensure first item specified is a water side heating equipment. and second one is cooling equipment.
                # only one heating and one coolingtower allowed currently
                f"sizing:plant,whp loop,condenser,29.44,5.56;"
                f"setpointmanager:scheduled:dualsetpoint,central boiler setpoint manager,temperature,wlhp high,wlhp low,{eqlist[0].name}0 outlet node;"
                "setpointmanager:scheduled:dualsetpoint,water loop setpoint manager,temperature,wlhp high,wlhp low,whp supply side outlet node;"
                "plantequipmentoperationschemes,whp operation,plantequipmentoperation:heatingload,wlhp heating,on 24/7,plantequipmentoperation:coolingload,wlhp cooling,on 24/7;"
                "plantequipmentoperation:heatingload,wlhp heating,0,1000000000000,whp heatingplant eq list;"
                "plantequipmentoperation:coolingload,wlhp cooling,0,1000000000000,whp coolingplant eq list;"
                #           'plantequipmentlist,whp heatingplant eq list,boiler:hotwater,boiler0;'
                f"plantequipmentlist,whp heatingplant eq list,{eqlist[0].obj},{eqlist[0].name}0;"
                f"plantequipmentlist,whp coolingplant eq list,{eqlist[1].obj},{eqlist[1].name}1;"
                #            coolingtower:singlespeed,coolingtower1;'
            )


def CoolingTower(i, *args):
    """Generate cooling tower IDF string for WLHP systems.

    Args:
        i: Equipment index number for unique naming
        *args: Reserved for future additional parameters

    Note:
        Primarily used for water loop heat pump (WLHP) systems
    """
    return (
        # to be used primarily for wlhp examplefiles/5zonewlhpplantlooptower.idf
        f"branch,coolingtower{i} supply side branch,,coolingtower:twospeed,coolingtower{i},coolingtower{i} water inlet node,coolingtower{i} water outlet node;"
        f"coolingtower:twospeed,coolingtower{i},coolingtower{i} water inlet node,coolingtower{i} water outlet node,autosize,autosize,autosize,autosize,autocalculate,0.5000,autocalculate,0.1600,autocalculate,0.6000,autocalculate,0.1000,autocalculate,0.1000,ufactortimesareaanddesignwaterflowrate,1.2500,20000.0000,autocalculate,0.5000,autocalculate,0.1000,35.00,25.60,3.90,5.60,0.00,2.00,on 24/7,saturatedexit,0.2000,0,concentrationratio,3.00,on 24/7,,,,minimalcell,0.3300,2.5000,1.00;"
    )


def FluidCooler(i, *args):
    """Generate Fluid Cooler IDF string for WLHP systems.

    Args:
        i: Equipment index number for unique naming
        *args: Reserved for future additional parameters

    Note:
        Primarily used for water loop heat pump (WLHP) systems
    """
    return (
        f"branch,coolingtower{i} supply side branch,,fluidcooler:twospeed,coolingtower{i},coolingtower{i} water inlet node,coolingtower{i} water outlet node;"
        #        f"fluidcooler:twospeed,coolingtower{i},coolingtower{i} water inlet node,coolingtower{i} water outlet node,nominalcapacity,,,0.6,582060,291030,0.5,51.67,35,25.6,autosize,autosize,43776.2410666667,autocalculate,0.5,autocalculate,0.16;"
        f"fluidcooler:twospeed,coolingtower{i},coolingtower{i} water inlet node,coolingtower{i} water outlet node,nominalcapacity,,,0.6,582060,291030,0.5,51.67,27,25.6,autosize,autosize,43776.2410666667,autocalculate,0.5,autocalculate,0.16;"
    )


def WaterCooledChiller(i, equipment_config, *args):
    """Generate water-cooled chiller with condenser loop IDF string.

    Args:
        i: Equipment index number for unique naming
        equipment_config: Tuple of (chiller_sysname, condenser_equipment_sysname) where
                         condenser_equipment is typically a cooling tower or fluid cooler
        *args: Reserved for future additional parameters
    """
    _, cweq = equipment_config
    wch = cweq.fun(i)

    return wch + (
        # condenser plant
        f"condenserloop,condenser loop{i},water,,condenser loop{i} operation,condenser loop{i} supply side outlet node,50.00,5.00,autosize,0.000000,autocalculate,condenser loop{i} supply side inlet node,condenser loop{i} supply side outlet node,condenser loop{i} supply side branches,condenser loop{i} supply side connectors,condenser loop{i} demand side inlet node,condenser loop{i} demand side outlet node,condenser loop{i} demand side branches,condenser loop{i} demand side connectors,sequentialload,none;"
        # condenser supply side
        f"branch,condenser loop{i} supply side inlet branch,,pump:constantspeed,condenser loop{i} supply pump,condenser loop{i} supply side inlet node,condenser loop{i} supply pump water outlet node;"
        f"pump:constantspeed,condenser loop{i} supply pump,condenser loop{i} supply side inlet node,condenser loop{i} supply pump water outlet node,autosize,235241.37,autosize,0.90,0.00,intermittent;"
        f"branch,condenser loop{i} supply side bypass branch,,pipe:adiabatic,condenser loop{i} supply side bypass pipe,condenser loop{i} supply side bypass pipe inlet node,condenser loop{i} supply side bypass pipe outlet node;"
        f"pipe:adiabatic,condenser loop{i} supply side bypass pipe,condenser loop{i} supply side bypass pipe inlet node,condenser loop{i} supply side bypass pipe outlet node;"
        f"branch,condenser loop{i} supply side outlet branch,,pipe:adiabatic,condenser loop{i} supply side outlet branch pipe,condenser loop{i} supply side outlet branch pipe inlet,condenser loop{i} supply side outlet node;"
        f"pipe:adiabatic,condenser loop{i} supply side outlet branch pipe,condenser loop{i} supply side outlet branch pipe inlet,condenser loop{i} supply side outlet node;"
        f"connectorlist,condenser loop{i} supply side connectors,connector:splitter,condenser loop{i} supply splitter,connector:mixer,condenser loop{i} supply mixer;"
        f"connector:mixer,condenser loop{i} supply mixer,condenser loop{i} supply side outlet branch,condenser loop{i} supply side bypass branch,coolingtower{i} supply side branch;"
        f"connector:splitter,condenser loop{i} supply splitter,condenser loop{i} supply side inlet branch,condenser loop{i} supply side bypass branch,coolingtower{i} supply side branch;"
        f"branchlist,condenser loop{i} supply side branches,condenser loop{i} supply side inlet branch,condenser loop{i} supply side bypass branch,coolingtower{i} supply side branch,condenser loop{i} supply side outlet branch;"
        # condenser demand side
        f"branch,condenser loop{i} demand side inlet branch,,pipe:adiabatic,condenser loop{i} demand side inlet branch pipe,condenser loop{i} demand side inlet node,condenser loop{i} demand side inlet branch pipe outlet;"
        f"pipe:adiabatic,condenser loop{i} demand side inlet branch pipe,condenser loop{i} demand side inlet node,condenser loop{i} demand side inlet branch pipe outlet;"
        f"branch,condenser loop{i} demand side bypass branch,,pipe:adiabatic,condenser loop{i} demand side bypass pipe,condenser loop{i} demand side bypass pipe inlet node,condenser loop{i} demand side bypass pipe outlet node;"
        f"pipe:adiabatic,condenser loop{i} demand side bypass pipe,condenser loop{i} demand side bypass pipe inlet node,condenser loop{i} demand side bypass pipe outlet node;"
        f"branch,condenser loop{i} demand side outlet branch,,pipe:adiabatic,condenser loop{i} demand side outlet branch pipe,condenser loop{i} demand side outlet branch pipe inlet,condenser loop{i} demand side outlet node;"
        f"pipe:adiabatic,condenser loop{i} demand side outlet branch pipe,condenser loop{i} demand side outlet branch pipe inlet,condenser loop{i} demand side outlet node;"
        f"connectorlist,condenser loop{i} demand side connectors,connector:splitter,condenser loop{i} demand splitter,connector:mixer,condenser loop{i} demand mixer;"
        f"connector:mixer,condenser loop{i} demand mixer,condenser loop{i} demand side outlet branch,chiller condenser loop{i} demand side branch,condenser loop{i} demand side bypass branch;"
        f"connector:splitter,condenser loop{i} demand splitter,condenser loop{i} demand side inlet branch,condenser loop{i} demand side bypass branch,chiller condenser loop{i} demand side branch;"
        f"branchlist,condenser loop{i} demand side branches,condenser loop{i} demand side inlet branch,condenser loop{i} demand side bypass branch,chiller condenser loop{i} demand side branch,condenser loop{i} demand side outlet branch;"
        f"sizing:plant,condenser loop{i},condenser,29.44,5.56;"
        f"setpointmanager:followoutdoorairtemperature,condenser loop{i} setpoint manager,temperature,outdoorairwetbulb,0.00,29.44,21.11,condenser loop{i} supply side outlet node;"
        f"condenserequipmentoperationschemes,condenser loop{i} operation,plantequipmentoperation:coolingload,condenser loop{i} scheme 1,on 24/7;"
        f"plantequipmentoperation:coolingload,condenser loop{i} scheme 1,0.00,1000000000000000.00,condenser loop{i} scheme 1 range 1 equipment list;"
        f"condenserequipmentlist,condenser loop{i} scheme 1 range 1 equipment list,{cweq.obj},coolingtower{i};"
        #   f'setpointmanager:outdoorairreset,chw setpoint manager,temperature,12.22,15.56,6.67,26.67,primary chw setpoint manager node list;'
        #   f'setpointmanager:scheduled,chw loop setpoint manager,temperature,chilled water flow set point temperature: always 6 c,chw loop setpoint manager node list;'
        # water cooled chiller branch
        f"branch,chiller condenser loop{i} demand side branch,,chiller:electric:eir,watercooledchiller{i} ,watercooledchiller{i} condenser inlet node,watercooledchiller{i} condenser outlet node;"
        f"branch,watercooledchiller{i} supply side branch,,chiller:electric:eir,watercooledchiller{i},watercooledchiller{i} inlet node,watercooledchiller{i} outlet node;"
        f"chiller:electric:eir,watercooledchiller{i},autosize,5.50,6.67,29.40,autosize,autosize,doe-2 centrifugal/5.50cop capft,doe-2 centrifugal/5.50cop eirft,doe-2 centrifugal/5.50cop eirfplr,0.10,1.00,1.00,0.10,watercooledchiller{i} inlet node,watercooledchiller{i} outlet node,watercooledchiller{i} condenser inlet node,watercooledchiller{i} condenser outlet node,watercooled,0.00,1.00,2.00,notmodulated,0.0;"
    )


def AirCooledChiller(i, *args):
    """Generate air-cooled chiller IDF string.

    Args:
        i: Equipment index number for unique naming
        *args: Reserved for future additional parameters
    """
    return (
        f"branch,aircooledchiller{i} supply side branch,,chiller:electric:eir,aircooledchiller{i},aircooledchiller{i} inlet node,aircooledchiller{i} outlet node;"
        f"chiller:electric:eir,aircooledchiller{i},autosize,2.78,6.67,29.40,autosize,autosize,air cooled centcapft,air cooled centeirft,air cooled centeirfplr,0.00,1.00,1.00,0.25,aircooledchiller{i} inlet node,aircooledchiller{i} outlet node,,,aircooled,0.04,1.00,5.00,notmodulated;"
    )


def DistCooling(i, *args):
    """Generate district cooling connection IDF string.

    Args:
        i: Equipment index number for unique naming
        *args: Reserved for future additional parameters
    """
    return (
        f"branch,distcooling{i} supply side branch,,districtcooling,distcooling{i},distcooling{i} water inlet node,distcooling{i} water outlet node;"
        f"districtcooling,distcooling{i},distcooling{i} water inlet node,distcooling{i} water outlet node,99999999.9,on 24/7;"
    )


def Boiler(i, *args):
    """Generate natural gas boiler IDF string.

    Args:
        i: Equipment index number for unique naming
        *args: Reserved for future additional parameters
    """
    return (
        f"branch,boiler{i} supply side branch,,boiler:hotwater,boiler{i},boiler{i} inlet node,boiler{i} outlet node;"
        f"boiler:hotwater,boiler{i},naturalgas,autosize,0.8,leavingboiler,noncondensingboilereff,autosize,0.00,1.00,1.00,boiler{i} inlet node,boiler{i} outlet node,100.0,notmodulated,25.00,1.00;"
        #    f'boiler:hotwater,boiler{i},naturalgas,autosize,0.95,leavingboiler,heatsys1 boiler condensing boiler curve,autosize,0.00,1.00,1.00,boiler{i} water inlet node,boiler{i} water outlet node,100.0,notmodulated,25.00,1.00;'
    )


def DistHeating(i, *args):
    """Generate district heating connection IDF string.

    Args:
        i: Equipment index number for unique naming
        *args: Reserved for future additional parameters
    """
    return (
        f"branch,distheating{i} supply side branch,,districtheating:water,distheating{i},distheating{i} water inlet node,distheating{i} water outlet node;"
        f"districtheating:water,distheating{i},distheating{i} water inlet node,distheating{i} water outlet node,99999999.9,on 24/7;"
    )


def GSHPClg(i, *args):
    """Generate ground source heat pump cooling with vertical ground heat exchanger IDF string.

    Args:
        i: Equipment index number for unique naming
        *args: Reserved for future additional parameters
    """
    return (
        # condenser plant
        #'site:groundtemperature:deep,13.03,13.03,13.13,13.30,13.43,13.52,13.62,13.77,13.78,13.55,13.44,13.20;'
        f"setpointmanager:followgroundtemperature,mycondensercontrol,temperature,site:groundtemperature:deep,0,80.0,10.0,groundloop{i} supply side outlet node;"
        f"plantequipmentoperationschemes,groundloop{i} operation,plantequipmentoperation:uncontrolled,groundloop{i} scheme 1,on 24/7;"
        f"plantequipmentoperation:uncontrolled,groundloop{i} scheme 1,groundloop{i} scheme 1 range 1 equipment list;"
        f"condenserequipmentlist,groundloop{i} scheme 1 range 1 equipment list,groundheatexchanger:system,verticalghe{i};"
        "groundheatexchanger:vertical:properties,vertical ground heat exchanger props,1,76.2,0.127016,0.692626e+00,3.90e+06,0.391312e+00,1.542e+06,2.66667e-02,2.41285e-03,5.1225e-02;"
        "site:groundtemperature:undisturbed:kusudaachenbach,vertical ground heat exchanger ground temps,0.692626e+00,920,2551.09,13.375,3.2,8;"
        "groundheatexchanger:responsefactors,vertical ground heat exchanger g-functions,vertical ground heat exchanger props,120,0.0005,-15.2996,-0.348322,-14.201,0.022208,-13.2202,0.412345,-12.2086,0.867498,-11.1888,1.357839,-10.1816,1.852024,-9.1815,2.345656,-8.6809,2.593958,-8.5,2.679,-7.8,3.023,-7.2,3.32,-6.5,3.681,-5.9,4.071,-5.2,4.828,-4.5,6.253,-3.963,7.894,-3.27,11.82,-2.864,15.117,-2.577,18.006,-2.171,22.887,-1.884,26.924,-1.191,38.004,-0.497,49.919,-0.274,53.407,-0.051,56.632,0.196,59.825,0.419,62.349,0.642,64.524,0.873,66.412,1.112,67.993,1.335,69.162,1.679,70.476,2.028,71.361,2.275,71.79,3.003,72.511;"
        f"sizing:plant,groundloop{i},condenser,29.44,5.56;"
        f"plantloop,groundloop{i},water,,groundloop{i} operation,groundloop{i} supply side outlet node,50.00,5.00,autosize,0.000000,autocalculate,groundloop{i} supply side inlet node,groundloop{i} supply side outlet node,groundloop{i} supply side branches,,groundloop{i} demand side inlet node,groundloop{i} demand side outlet node,groundloop{i} demand side branches,,optimal;"
        f"branchlist,groundloop{i} supply side branches,groundloop{i} supply side branch;"
        f"branch,groundloop{i} supply side branch,,pump:variablespeed,groundloop{i} pump,groundloop{i} supply side inlet node,groundloop{i} supply intermediate node,groundheatexchanger:system,verticalghe{i},groundloop{i} supply intermediate node,groundloop{i} supply side outlet node;"
        f"pump:variablespeed,groundloop{i} pump,groundloop{i} supply side inlet node,groundloop{i} supply intermediate node,0.003,30000,200,0.87,0.0,0,1,0,0,0,intermittent;"
        f"groundheatexchanger:system,verticalghe{i},groundloop{i} supply intermediate node,groundloop{i} supply side outlet node,0.00330000,site:groundtemperature:undisturbed:kusudaachenbach,vertical ground heat exchanger ground temps,0.692626e+00,0.234700e+07,vertical ground heat exchanger g-functions;"
        f"branchlist,groundloop{i} demand side branches,groundloop{i} demand side branch;"
        f"branch,groundloop{i} demand side branch,,heatpump:plantloop:eir:heating,gshphtg{i},groundloop{i} demand side inlet node,groundloop{i} demand intermediate node,heatpump:plantloop:eir:cooling,gshpclg{i},groundloop{i} demand intermediate node,groundloop{i} demand side outlet node;"
        f"branch,gshpclg{i} supply side branch,,heatpump:plantloop:eir:cooling,gshpclg{i},gshpclg{i} inlet node,gshpclg{i} outlet node;"
        f"heatpump:plantloop:eir:cooling,gshpclg{i},gshpclg{i} inlet node,gshpclg{i} outlet node,watersource,groundloop{i} demand intermediate node,groundloop{i} demand side outlet node,,,gshphtg{i},0.005,0.003,,400000,3.5,,capcurvefunctemp2,eircurvefunctemp2,eircurvefuncplr2;"
    )


def GSHPHtg(i, *args):
    """Generate ground source heat pump heating IDF string.

    Args:
        i: Equipment index number for unique naming (companion to GSHPClg)
        *args: Reserved for future additional parameters
    """
    return (
        f"branch,gshphtg{i} supply side branch,,heatpump:plantloop:eir:heating,gshphtg{i},gshphtg{i} inlet node,gshphtg{i} outlet node;"
        f"heatpump:plantloop:eir:heating,gshphtg{i},gshphtg{i} inlet node,gshphtg{i} outlet node,watersource,groundloop{i} demand side inlet node,groundloop{i} demand intermediate node,,,gshpclg{i},0.005,0.002,,80000,3.5,,capcurvefunctemp,eircurvefunctemp,eircurvefuncplr;"
    )


def AirToWaterHP(i, *args):
    """Generate air-to-water heat pump IDF string.

    Args:
        i: Equipment index number for unique naming
        *args: Reserved for future additional parameters

    Note:
        Incomplete - may need companion HP cooling inputs
    """
    return (
        # does not work. may need a companion HP cooling inputs.
        f"branch,airtowaterhp{i} supply side branch,,heatpump:airtowater,airtowaterhp{i},airtowaterhp{i} inlet node,airtowaterhp{i} outlet node;"
        f"heatpump:airtowater,airtowaterhp{i},,,load,singlemode,,,20,autosize,50,autosize,-20,25,,,1.0,,,,,,,,,,hp oa inlet node{i},hp oa outlet node{i},airtowaterhp{i} inlet node,airtowaterhp{i} outlet node,,,,timed,0.2,150,,2,fixedspeed,100,crankcaseheaterpowercurve,5,2,20000,3.49,capcurvefunctempht,eircurvefunctempht,eircurvefuncplr,autosize,3.51,capcurvefunctempht2,eircurvefunctempht2,eircurvefuncplr2;"
        f"outdoorair:node,hp oa inlet node{i};"
    )


# Central plant system options.
# Format: 'key': (function, energyplus_object_type, description)


pltlist = [
    sysname( "boiler", Boiler, "boiler:hotwater", "Hot water boiler for hydronic heating systems",),
    sysname( "aircooledchiller", AirCooledChiller, "chiller:electric:eir", "Air-cooled electric chiller with air-cooled condenser",),
    sysname( "watercooledchiller", WaterCooledChiller, "chiller:electric:eir", "Water-cooled electric chiller requiring cooling tower",),
    sysname( "coolingtower", CoolingTower, "coolingtower:twospeed", "Two-speed cooling tower for condenser water heat rejection",),
    sysname( "fluidcooler", FluidCooler, "fluidcooler:twospeed", "Two-speed fluid cooler for condenser water heat rejection",),
    sysname( "distheating", DistHeating, "districtheating:water", "District heating connection for hot water supply",),
    sysname( "distcooling", DistCooling, "districtcooling", "District cooling connection for chilled water supply",),
    sysname( "airtowaterhp", AirToWaterHP, "heatpump:airtowater", "Air to water heat pump for heating only",),
    sysname( "gshphtg", GSHPHtg, "heatpump:plantloop:eir:heating", "Ground-source heat pump for heating",),
    sysname( "gshpclg", GSHPClg, "heatpump:plantloop:eir:cooling", "Ground-source heat pump for cooling",),
]

# pltsys: SimpleNamespace providing attribute-based access to all plant equipment
# This allows users to reference equipment using dot notation, e.g.:
#   - pltsys.boiler -> sysname for boiler
#   - pltsys.aircooledchiller -> sysname for air-cooled chiller
#   - pltsys.watercooledchiller -> sysname for water-cooled chiller
#
# Usage example in PlantConfig:
#   cp = PlantConfig(hw=(pltsys.boiler,), chw=(pltsys.aircooledchiller,))
#
# This design provides type safety - users can only specify equipment that exists,
# and IDEs can provide autocomplete for available equipment types.
pltsys = SimpleNamespace(**{ea.name: ea for ea in pltlist})


def get_plant_equipment():
    """Return dict of available plant equipment with descriptions.

    This function is primarily used by LLMs (via SKILL.md) to understand
    available plant equipment options and map user requests to the correct
    equipment types.

    Returns:
        Dict[str, str]: Mapping of equipment name to human-readable description

    Example:
        >>> equipment = get_plant_equipment()
        >>> print(equipment['boiler'])
        'Hot water boiler for hydronic heating systems'
        >>> print(equipment['aircooledchiller'])
        'Air-cooled electric chiller with air-cooled condenser'
    """
    return {ea.name: ea.desc for ea in pltlist}

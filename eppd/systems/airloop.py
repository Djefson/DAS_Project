"""
Bharath Karambakkam
e-mail:kBharathk@gmail.com
function: templates to construct a energyplus idf,
          utilized by  readidf.createsys function.

"""


from collections import namedtuple
lpcoil = namedtuple("lpcoil", "fun obj type desc")


def airLoop(sname: str, znames: list, coils: str, fsch: str) -> str:
    """Generate complete air loop IDF string.

    Node connection map:
        - exhaust fan: Exhaust outlet -> Mixed Outlet
        - clcoil: Mixed Outlet -> clcoil outlet/fan Inlet
        - htcoil: Mixed Outlet/clcoil outlet -> Fan Inlet
        - supply fan: Fan Inlet -> Supply Outlet

    Args:
        sname: System name
        znames: List of zone names served by this air loop
        coils: Coil configuration string (format: 'coil1_coil2_systemtype')
               e.g., 'chw_hw_doas' for chilled water, hot water, DOAS system
        fsch: Fan schedule name

    Returns:
        Complete IDF string for air loop system

    Air loop types: cv (constant volume), vav (variable air volume),
                   doas (dedicated outdoor air), vrfdoas (VRF with DOAS)
    """

    *coillist, tunit = coils.split('_')
    hwcoil = 'hw' in coillist
    chwcoil = 'chw' in coillist
    doas = tunit in ('doas','vrfdoas')
    cv = tunit == 'cv'
    lp = ''.join([

        f'branchlist,{sname} branches,{sname} main branch;'

        #--oa and hr setup
        f'airloophvac:outdoorairsystem,{sname} outdoor air system,{sname} outdoor air controller list,{sname} outdoor air equipment list;'#check if this is superflous
        f'airloophvac:controllerlist,{sname} outdoor air controller list,controller:outdoorair,{sname} outdoor air controller;'
        f'controller:outdoorair,{sname} outdoor air controller,{sname} relief air outlet node,{sname} extract fan air outlet node,{sname} mixed air outlet node,{sname} outdoor air inlet,autosize,autosize,differentialdrybulb,modulateflow,21.11,,,,,lockoutwithheating,fixedminimum,{fsch},,,,,no,,1,yes,bypasswhenwithineconomizerlimits;'
        f'airloophvac:outdoorairsystem:equipmentlist,{sname} outdoor air equipment list,heatexchanger:airtoair:sensibleandlatent,{sname} heat recovery device,outdoorair:mixer,{sname} outdoor air mixer;'
        f'availabilitymanagerassignmentlist,{sname} availabilitymanager list,availabilitymanager:nightcycle,{sname} night cycle operation;'

        f'heatexchanger:airtoair:sensibleandlatent,{sname} heat recovery device,on 24/7,autosize,0.70,0.60,0.75,0.60,{sname} outdoor air inlet,{sname} heat recovery supply outlet,{sname} relief air outlet node,{sname} heat recovery relief outlet,0.000,yes,rotary,exhaustonly,1.70,0.167,0.0240,yes,seneffectivenesstable,lateffectivenesstable,seneffectivenesstable,lateffectivenesstable;'
        f'outdoorair:mixer,{sname} outdoor air mixer,{sname} mixed air outlet node,{sname} heat recovery supply outlet,{sname} relief air outlet node,{sname} extract fan air outlet node;'
        f'outdoorair:nodelist,{sname} outdoor air inlet;'

        f'setpointmanager:mixedair,{sname} outdoor air system mixed air manager,temperature,{sname} supply side outlet node,{sname} mixed air outlet node,{sname} supply fan outlet node,{sname} mixed air outlet node;'
#        f'setpointmanager:scheduled,{sname} heat recovery device setpoint manager,temperature,cooling set point temperature: always 14.0 c,{sname} heat recovery supply outlet;'

        f'setpointmanager:mixedair,{sname} heat recovery device setpoint manager,temperature,{sname} supply side outlet node,{sname} mixed air outlet node,{sname} supply fan outlet node,{sname} heat recovery supply outlet;'

        #--linking zone loop with air loop
        f'airloophvac:supplypath,{sname} demand side supply path,{sname} demand side inlet node,airloophvac:zonesplitter,{sname} zone splitter;'
        f'airloophvac:zonesplitter,{sname} zone splitter,{sname} demand side inlet node'
        f'{" ".join(f",{c} zone splitter outlet node" for c in znames)} ;'

        f'airloophvac:returnpath,{sname} demand side return path,{sname} demand side outlet node,airloophvac:zonemixer,{sname} zone mixer;'
        f'airloophvac:zonemixer,{sname} zone mixer,{sname} demand side outlet node'
        f'{" ".join(f",{c} zone mixer inlet node" for c in znames)};'
        #---

        #setpoint managers
        , # this comma is required to merge above single string with logic based items below.

        #sizing for doas
        (f'sizing:system,{sname},ventilationrequirement,autosize,1,5.00,0.00800,11.00,0.00800,12.22,15.56,coincident,yes,yes,0.00800,0.00800,designday,,,,,designday,,,,,,zonesum,1.0000,coolingdesigncapacity,autosize,,,heatingdesigncapacity,autosize,,,vav;'
        f'availabilitymanager:nightcycle,{sname} night cycle operation,on 24/7,{fsch},cycleonanyzonefansonly,1,thermostatwithminimumruntime;' if doas else
        f'availabilitymanager:nightcycle,{sname} night cycle operation,on 24/7,{fsch},cycleonany,1,thermostatwithminimumruntime;'
         ),
        #sizing for cv
        (f'sizing:system,{sname},sensible,autosize,1,7.00,0.00800,11.00,0.00800,12.22,35,noncoincident,no,no,0.00800,0.00800,designday,,,,,designday,,,,,,zonesum,1.0000,coolingdesigncapacity,autosize,,,heatingdesigncapacity,autosize,,,vt;' if cv else ''),
        # sizing for vav
        (f'sizing:system,{sname},sensible,autosize,.30,7.00,0.00800,11.00,0.00800,12.22,15.56,coincident,no,no,0.00800,0.00800,designday,,,,,designday,,,,,,zonesum,1.0000,coolingdesigncapacity,autosize,,,heatingdesigncapacity,autosize,,,vav;' if not (cv + doas) else ''),

        # specify fans based on cv or vav
        (f'fan:constantvolume,{sname} extract fan,{fsch},0.700000,373.26,autosize,0.900000,1.00,{sname} supply side inlet node,{sname} extract fan air outlet node,general;'
        f'fan:constantvolume,{sname} supply fan,{fsch},0.700000,900.26,autosize,0.900000,1.00,{sname} mixed air outlet node,{sname} supply fan outlet node,general;' if cv else
        f'fan:variablevolume,{sname} extract fan,{fsch},0.600000,622.11,autosize,fraction,0.3000,0.000000,0.900000,1.00,0.0013000000,0.1470000000,0.9506000000,-0.0998000000,0.0000000000,{sname} supply side inlet node,{sname} extract fan air outlet node,general;'
        f'fan:variablevolume,{sname} supply fan,{fsch},0.600000,995.37,autosize,fraction,0.3000,0.000000,0.900000,1.00,0.0013000000,0.1470000000,0.9506000000,-0.0998000000,0.0000000000,{sname} mixed air outlet node,{sname} supply fan outlet node,general;'),

        # controllers if ahu has cooling coil and heating coil.
        (f'airloophvac,{sname},{sname} controllers,{sname} availabilitymanager list,autosize,{sname} branches,,{sname} supply side inlet node,{sname} demand side outlet node,{sname} demand side inlet node,{sname} supply side outlet node;' if (hwcoil or chwcoil) else 
        f'airloophvac,{sname},,{sname} availabilitymanager list,autosize,{sname} branches,,{sname} supply side inlet node,{sname} demand side outlet node,{sname} demand side inlet node,{sname} supply side outlet node;'),
        (f'airloophvac:controllerlist,{sname} controllers,controller:watercoil,{sname} cooling coil controller,controller:watercoil,{sname} heating coil controller;' if (hwcoil * chwcoil) else ''),   #needed here to create controller list with chw and hw coil
        (f'airloophvac:controllerlist,{sname} controllers,controller:watercoil,{sname} heating coil controller;' if (hwcoil * (not chwcoil)) else ''),
        (f'airloophvac:controllerlist,{sname} controllers,controller:watercoil,{sname} cooling coil controller;' if (chwcoil * (not hwcoil)) else '')
        ])

    if cv: 
        mainbr = f'branch,{sname} main branch,,fan:constantvolume,{sname} extract fan,{sname} supply side inlet node,{sname} extract fan air outlet node,airloophvac:outdoorairsystem,{sname} outdoor air system,{sname} extract fan air outlet node,{sname} mixed air outlet node,fan:constantvolume,{sname} supply fan,{sname} mixed air outlet node,{sname} supply fan outlet node,'
    else:
        mainbr = f'branch,{sname} main branch,,fan:variablevolume,{sname} extract fan,{sname} supply side inlet node,{sname} extract fan air outlet node,airloophvac:outdoorairsystem,{sname} outdoor air system,{sname} extract fan air outlet node,{sname} mixed air outlet node,fan:variablevolume,{sname} supply fan,{sname} mixed air outlet node,{sname} supply fan outlet node,'

    inode = f'{sname} supply fan outlet node'
    lpctl = ''
    for i,ea in enumerate(coillist[:-1]): # loop until second last coil
        onode = f'{sname} coil {i+1} outlet node'
        mainbr += f'{dictcoil[ea].obj},{sname} {ea} {dictcoil[ea].type},{inode},{onode},'
        lp += dictcoil[ea].fun(sname,inode,onode,ea)
        lpctl+= mstpt(sname,onode,cv,doas,ea)
        inode = onode
    lcoil = coillist[-1] # get last coil and supply setpoint manager
    onode = f'{sname} supply side outlet node'
    mainbr += f'{dictcoil[lcoil].obj},{sname} {lcoil} {dictcoil[lcoil].type},{inode},{onode};'
    lp += dictcoil[lcoil].fun(sname,inode,onode,lcoil)
    lpctl+= mstpt(sname,onode,cv,doas,lcoil)

    lp += mainbr+lpctl
    if tunit == 'vrfdoas':lp += vrf_sys(sname, znames)
    return lp

def mstpt(sname: str, onode: str, cv: bool, doas: bool, cl: str):
    """Generate setpoint manager for coil outlet node.

    Args:
        sname: System name
        onode: Outlet node name
        cv: True if constant volume system
        doas: True if dedicated outdoor air system
        cl: Coil type ('chw', 'dx', 'hw', 'el', 'ng', 'hp')

    Returns:
        IDF string for setpoint manager
    """

    "TODO: look into humidtity control SetpointManager:SystemNodeReset:Humidity (5ZoneSystemNodeReset.idf)"

    match [cv,doas,cl]:

        #vav system
        case [False,False,'chw'|'dx']:return (f'setpointmanager:warmest,{sname} cooling coil setpoint manager,temperature,{sname},12.75,20.78,maximumtemperature,{onode};')
        case [False,False,'hw'|'el'|'ng'|'hp']:return (f'setpointmanager:warmest,{sname} setpoint manager,temperature,{sname},12.75,12.78,maximumtemperature,{onode};')

        #doas system
        case [False,True,'chw'|'dx']:return (f'setpointmanager:warmest,{sname} cooling coil setpoint manager,temperature,{sname},12.75,12.78,maximumtemperature,{onode};')
        case [False,True,'hw'|'el'|'ng'|'hp']:return (f'setpointmanager:warmest,{sname} setpoint manager,temperature,{sname},12.75,12.78,maximumtemperature,{onode};')

        #constant volume syste
        case [True,False,'chw'|'dx']:return (f'setpointmanager:warmest,{sname} cooling coil setpoint manager,temperature,{sname},11.75,20.78,maximumtemperature,{onode};')
        case [True,False,'hw'|'el'|'ng'|'hp']:return (f'setpointmanager:coldest,{sname} setpoint manager,temperature,{sname},12.75,45.00,minimumtemperature,{onode};')
        #case [True,False,'chw'|'dx']:return (f'setpointmanager:multizone:cooling:average,{sname} cooling coil setpoint manager,{sname},11.75,20.78,{onode};')
        #case [True,False,'hw'|'el'|'ng'|'hp']:return (f'setpointmanager:multizone:heating:average,{sname} setpoint manager,{sname},12.75,45.00,{onode};')


## Central AHU Coils

def el_coil(sname, inode, onode, coilno):
    """Generate electric heating coil IDF string."""
    return ''.join([
            #------------ pvav hw reheat ashrae appen g sys#5
            f'coil:heating:electric,{sname} {coilno} heating coil,on 24/7,1.00,autosize,{inode},{onode},{sname} supply side outlet node;'
           ])


def ng_coil(sname, inode, onode, coilno):
    """Generate natural gas heating coil IDF string."""
    return ''.join([
            f'coil:heating:fuel,{sname} {coilno} heating coil,on 24/7,naturalgas,0.80,autosize,{inode},{onode},{sname} supply side outlet node,0.000,,0.000;'
           ])


def hw_coil(sname, inode, onode, coilno):
    """Generate hot water heating coil IDF string."""
    return ''.join([
            f'branch,{sname} hw demand side branch,,coil:heating:water,{sname} {coilno} heating coil,{sname} heating coil water inlet node,{sname} heating coil water outlet node;'
            f'coil:heating:water,{sname} {coilno} heating coil,on 24/7,autosize,autosize,{sname} heating coil water inlet node,{sname} heating coil water outlet node,{inode},{onode},nominalcapacity,autosize,82.2222222222222,16,54.4444444444444,35,0.50;'
            f'controller:watercoil,{sname} heating coil controller,temperature,normal,flow,{onode},{sname} heating coil water inlet node,autosize,autosize,0.000000;'
           ])


def dx_coil(sname, inode, onode, coilno):
    """Generate DX cooling coil IDF string."""
    return ''.join([
            #------------ pvav hw reheat ashrae appen g sys#5

            f'coilsystem:cooling:dx,{sname} {coilno} cooling coil,on 24/7,{inode},{onode},{sname} supply side outlet node,coil:cooling:dx:twospeed,{sname} {coilno} cooling coil,none,yes,no,no,2.0000;'
            f'coil:cooling:dx:twospeed,{sname} {coilno} cooling coil,on 24/7,autosize,autosize,3.0,autosize,,,,{inode},{onode},varspeedcoolcapft,packagedratedcoolcapfflow,varspeedcooleirft,packagedratedcooleirfflow,varspeedcyclingplffplr,autosize,autosize,4.2,autosize,,,varspeedcoolcaplsft,varspeedcooleirlsft,,aircooled,,,,,,,,,,200,2,;'
           ])

def chw_coil(sname, inode, onode, coilno):
    """Generate chilled water cooling coil IDF string."""
    return ''.join([
            f'branch,{sname} chw demand side branch,,coil:cooling:water,{sname} {coilno} cooling coil,{sname} cooling coil water inlet node,{sname} cooling coil water outlet node;'
            f'coil:cooling:water,{sname} {coilno} cooling coil,on 24/7,autosize,autosize,autosize,autosize,autosize,autosize,autosize,{sname} cooling coil water inlet node,{sname} cooling coil water outlet node,{inode},{onode},simpleanalysis,crossflow;'
            f'controller:watercoil,{sname} cooling coil controller,temperature,reverse,flow,{onode},{sname} cooling coil water inlet node,autosize,autosize,0.000000;'

#           f'setpointmanager:mixedair,{sname} {coilno} cooling coil mixed air manager,temperature,{sname} supply side outlet node,{sname} mixed air outlet node,{sname} supply fan outlet node,{sname} supply side outlet node;'
           ])


def hp_coil(sname, inode, onode, coilno):
    """Generate heat pump heating coil IDF string."""
    return ''.join([
            #------------ pvav hw reheat ashrae appen g sys#5

            f'coilsystem:heating:dx,{sname} {coilno} heating coil,on 24/7,coil:heating:dx:singlespeed,{sname} {coilno} heating coil;'
            f'coil:heating:dx:singlespeed,{sname} {coilno} heating coil,on 24/7,autosize,3.0,autosize,,,{inode},{onode},hpacheatcapft,hpacheatcapfff,hpacheateirft,hpacheateirfff,hpaccoolplffplr,,-5.0,,5.0,200.0,,10.0,resistive,timed,0.166667,autosize,,;'

           ])


def vrf_sys(sname, znames):
    """Generate VRF system IDF string."""
    return  (
    # vrf sys
    f'airconditioner:variablerefrigerantflow,{sname} outdoor unit,on 24/7,autosize,3.300,-6.00,43.00,vrfcoolcapft,vrfcoolcapftboundary,vrfcoolcapfthi,vrfcooleirft,vrfcooleirftboundary,vrfcooleirfthi,coolingeirlowplr,coolingeirhiplr,coolingcombratio,vrfcplffplr,autosize,1.00,3.400,-20.00,40.00,vrfheatcapft,vrfheatcapftboundary,vrfheatcapfthi,vrfheateirft,vrfheateirftboundary,vrfheateirfthi,wetbulbtemperature,heatingeirlowplr,heatingeirhiplr,heatingcombratio,vrfcplffplr,0.20,,loadpriority,,{sname} outdoor unit zone list,yes,50.00,15.00,coolinglengthcorrectionfactor,-0.00,50.00,vrf piping correction factor for length in heating mode,0.0000,15.000,2,0.5000,5.00,resistive,timed,,0.0000,autosize,5.00,aircooled,{sname} outdoor unit outdoor air node,,autosize,0.9000,autosize,autosize,,0.000,2.00,on 24/7,electricity,-10.00,40.00,vrf heat recovery cooling capacity modifier,0.50,0.1500,vrf heat recovery cooling energy modifier,1.0000,0.0000,vrf heat recovery heating capacity modifier,1.0000,0.1500,vrf heat recovery heating energy modifier,1.0000,0.0000;'

    f'outdoorair:nodelist,{sname} outdoor unit outdoor air node;'

    f'zoneterminalunitlist,{sname} outdoor unit zone list'
    f'{" ".join(f",{c} zone sys" for c in znames)} ;'
    )



dictcoil = {
    'hw':lpcoil(hw_coil, 'coil:heating:water', 'heating coil', 'Hot water heating coil connected to hot water plant loop'),
    'el':lpcoil(el_coil, 'coil:heating:electric', 'heating coil', 'Electric resistance heating coil'),
    'ng':lpcoil(ng_coil, 'coil:heating:fuel', 'heating coil', 'Natural gas heating coil with combustion'),
    'chw':lpcoil(chw_coil, 'coil:cooling:water', 'cooling coil', 'Chilled water cooling coil connected to chilled water plant loop'),
    'dx':lpcoil(dx_coil, 'coilsystem:cooling:dx', 'cooling coil', 'Direct expansion (DX) cooling coil with refrigerant'),
    'hp':lpcoil(hp_coil, 'coilsystem:heating:dx', 'heating coil', 'Heat pump heating coil (DX heating mode)'),
    }

# Coil type groups derived from dictcoil
AIRLOOP_CLG_COILS = "chw|dx"
AIRLOOP_HTG_COILS = "hw|ng|hp"



def get_coil_types():
    """Return dict of available air loop coil types with descriptions.

    Returns:
        Dict mapping coil type to description string

    Example:
        >>> coils = get_coil_types()
        >>> print(coils['chw'])
        'Chilled water cooling coil connected to chilled water plant loop'
        >>> # For validation, just use .keys()
        >>> valid_types = coils.keys()
    """
    return {key: val.desc for key, val in dictcoil.items()}


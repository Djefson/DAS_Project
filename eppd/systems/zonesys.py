"""
Bharath Karambakkam
e-mail:kBharathk@gmail.com
function: zone systems used by createsys function.
          utilized by  readidf.createsys function.

"""


# Zone sys

from collections import namedtuple
bb = namedtuple("bb", "fun obj desc")

def zcv(zname, zbb):
    """Generate constant volume air terminal with optional baseboard.

    Args:
        zname: Zone name
        zbb: Baseboard type or None
    """
    if zbb:
        zeq = dictbaseboard[zbb].fun(zname) + f'zonehvac:equipmentlist,{zname} equipment,sequentialload,zonehvac:airdistributionunit,{zname} adu,1,1,,,{dictbaseboard[zbb].obj},{zname} baseboard,2,2;'
    else:
        zeq = f'zonehvac:equipmentlist,{zname} equipment,sequentialload,zonehvac:airdistributionunit,{zname} adu,1,1;'

    return zeq + (
       f'zonehvac:equipmentconnections,{zname},{zname} equipment,{zname} adu outlet node,,{zname} zone air node,{zname} zone mixer inlet node;'
       f'zonehvac:airdistributionunit,{zname} adu,{zname} adu outlet node,airterminal:singleduct:constantvolume:noreheat,{zname} single duct cav no reheat,0.0,0.0;'
       f'airterminal:singleduct:constantvolume:noreheat,{zname} single duct cav no reheat,on 24/7,{zname} zone splitter outlet node,{zname} adu outlet node,autosize;'
    )


def zvavel(zname, zbb):
    """Generate VAV terminal with electric reheat and optional baseboard.

    Args:
        zname: Zone name
        zbb: Baseboard type or None
    """
    if zbb:
        zeq = dictbaseboard[zbb].fun(zname) + f'zonehvac:equipmentlist,{zname} equipment,sequentialload,zonehvac:airdistributionunit,{zname} adu,1,1,,,{dictbaseboard[zbb].obj},{zname} baseboard,2,2;'
    else:
        zeq = f'zonehvac:equipmentlist,{zname} equipment,sequentialload,zonehvac:airdistributionunit,{zname} adu,1,1;'

    return zeq + (
        f'zonehvac:equipmentconnections,{zname},{zname} equipment,{zname} adu outlet node,,{zname} zone air node,{zname} zone mixer inlet node;'
        f'zonehvac:airdistributionunit,{zname} adu,{zname} adu outlet node,airterminal:singleduct:vav:reheat,{zname} single duct vav reheat,0.0,0.0;'
        f'airterminal:singleduct:vav:reheat,{zname} single duct vav reheat,on 24/7,{zname} single duct vav reheat damper outlet,{zname} zone splitter outlet node,autosize,constant,0.30,,min supply air flow fraction schedule: always 0.3,coil:heating:electric,{zname} zone heating coil,,,{zname} adu outlet node,0.0010,reverse,,,40.000000;'
        f'coil:heating:electric,{zname} zone heating coil,on 24/7,1.00,autosize,{zname} single duct vav reheat damper outlet,{zname} adu outlet node,{zname} adu outlet node;'
    )


def zvavhw(zname, zbb):
    """Generate VAV terminal with hot water reheat and optional baseboard.

    Args:
        zname: Zone name
        zbb: Baseboard type or None
    """
    if zbb:
        zeq = dictbaseboard[zbb].fun(zname) + f'zonehvac:equipmentlist,{zname} equipment,sequentialload,zonehvac:airdistributionunit,{zname} adu,1,1,,,{dictbaseboard[zbb].obj},{zname} baseboard,2,2;'
    else:
        zeq = f'zonehvac:equipmentlist,{zname} equipment,sequentialload,zonehvac:airdistributionunit,{zname} adu,1,1;'

    return zeq + (
        f'zonehvac:equipmentconnections,{zname},{zname} equipment,{zname} adu outlet node,,{zname} zone air node,{zname} zone mixer inlet node;'
        f'zonehvac:airdistributionunit,{zname} adu,{zname} adu outlet node,airterminal:singleduct:vav:reheat,{zname} single duct vav reheat,0.0,0.0;'
        f'airterminal:singleduct:vav:reheat,{zname} single duct vav reheat,on 24/7,{zname} single duct vav reheat damper outlet,{zname} zone splitter outlet node,autosize,constant,0.30,,min supply air flow fraction schedule: always 0.3,coil:heating:water,{zname} zone heating coil,autosize,0,{zname} adu outlet node,0.0010,reverse,,,35.000000;'
        f'coil:heating:water,{zname} zone heating coil,on 24/7,autosize,autosize,{zname} zone heating coil water inlet node,{zname} zone heating coil water outlet node,{zname} single duct vav reheat damper outlet,{zname} adu outlet node,ufactortimesareaanddesignwaterflowrate,autosize,80,16,70,35,0.50;'
        f'branch,{zname} zone hw demand side branch,,coil:heating:water,{zname} zone heating coil,{zname} zone heating coil water inlet node,{zname} zone heating coil water outlet node;'
    )


def zcb(zname,zbb):

    if zbb:
        zeq = dictbaseboard[zbb].fun(zname) + f'zonehvac:equipmentlist,{zname} equipment,sequentialload,zonehvac:airdistributionunit,{zname} adu ,1,1,,,{dictbaseboard[zbb].obj},{zname} baseboard,2,2;'
    else:
        zeq = f'zonehvac:equipmentlist,{zname} equipment,sequentialload,zonehvac:airdistributionunit,{zname} adu,1,1;'

    return zeq + (
#   chilled beam to be used with a doas system        
#  f'zonecontrol:thermostat,{zname} thermostat,{zname},control type schedule: always 4,thermostatsetpoint:dualsetpoint,dual sp;'
   f'zonehvac:equipmentconnections,{zname},{zname} equipment,{zname} zone supply nodelist,,{zname} zone air node,{zname} zone mixer inlet node;'
   f'zonehvac:airdistributionunit,{zname} adu,{zname} adu outlet node,airterminal:singleduct:constantvolume:fourpipebeam,{zname} 4pipe beam;'
   f'nodelist,{zname} zone supply nodelist,{zname} adu outlet node;'

   f'airterminal:singleduct:constantvolume:fourpipebeam,{zname} 4pipe beam,on 24/7,on 24/7,on 24/7,{zname} zone splitter outlet node,{zname} adu outlet node,{zname} zone cooling coil water inlet node,{zname} zone cooling coil water outlet node,{zname} zone heating coil water inlet node,{zname} zone heating coil water outlet node,autosize,autosize,autosize,autosize,0.036,597,10.0,5.2e-5,capmodfuncoftempdiff,coolcapmodfuncofsaflow,capmodfuncofwaterflow,1548,27.8,5.2e-5,capmodfuncoftempdiff,heatcapmodfuncofsaflow,capmodfuncofwaterflow;'
   f'branch,{zname} zone hw demand side branch,,airterminal:singleduct:constantvolume:fourpipebeam,{zname} 4pipe beam,{zname} zone heating coil water inlet node,{zname} zone heating coil water outlet node;'
   f'branch,{zname} zone chw demand side branch,,airterminal:singleduct:constantvolume:fourpipebeam,{zname} 4pipe beam,{zname} zone cooling coil water inlet node,{zname} zone cooling coil water outlet node;'
    )

def zahp(zname,zbb):

    if zbb:
        zeq = dictbaseboard[zbb].fun(zname) + f'zonehvac:equipmentlist,{zname} equipment,sequentialload,zonehvac:airdistributionunit,{zname} adu,1,1,,,zonehvac:packagedterminalheatpump,{zname} zone sys,2,2,,,{dictbaseboard[zbb].obj},{zname} baseboard,3,3;'
    else:
        zeq = f'zonehvac:equipmentlist,{zname} equipment,sequentialload,zonehvac:airdistributionunit,{zname} adu,1,1,,,zonehvac:packagedterminalheatpump,{zname} zone sys,2,2;'

    return zeq + (
#  f'zonecontrol:thermostat,{zname} thermostat,{zname},control type schedule: always 4,thermostatsetpoint:dualsetpoint,dual sp;'
   f'zonehvac:equipmentconnections,{zname},{zname} equipment,{zname} zone supply nodelist,{zname} zone return node,{zname} zone air node,{zname} zone mixer inlet node;'
   f'zonehvac:airdistributionunit,{zname} adu,{zname} adu outlet node,airterminal:singleduct:vav:noreheat,{zname} single duct vav no reheat,0.0,0.0;'
   f'airterminal:singleduct:vav:noreheat,{zname} single duct vav no reheat,on 24/7,{zname} adu outlet node,{zname} zone splitter outlet node,autosize,constant,1;'
   f'nodelist,{zname} zone supply nodelist,{zname} adu outlet node,{zname} zone sys outlet node;'

   f'zonehvac:packagedterminalheatpump,{zname} zone sys,on 24/7,{zname} zone return node,{zname} zone sys outlet node,outdoorair:mixer,{zname} zone outdoor air mixer,autosize,autosize,,,0.0,0.0,0.0,fan:constantvolume,{zname} zone supply fan,coil:heating:dx:singlespeed,{zname} zone heating coil,0.0010,coil:cooling:dx:singlespeed,{zname} zone cooling coil,0.0010,coil:heating:electric,{zname} zone electric coil,50,21.00,blowthrough,on 24/7;'
   f'fan:constantvolume,{zname} zone supply fan,on 24/7,0.700000,100.00,autosize,0.900000,1.00,{zname} zone mixed air outlet node,{zname} zone supply fan outlet node,general;'

   f'coil:cooling:dx:singlespeed,{zname} zone cooling coil,on 24/7,autosize,autosize,3.0000,autosize,,,{zname} zone supply fan outlet node,{zname} zone cooling coil outlet node,windaccoolcapft,windaccoolcapfff,windaceirft,windaceirfff,windacplffplr;' 
   f'coil:heating:dx:singlespeed,{zname} zone heating coil,on 24/7,autosize,3.0000,autosize,,,{zname} zone cooling coil outlet node,{zname} zone heating coil outlet node,hpacheatcapft,hpacheatcapfff,hpacheateirft,hpacheateirfff,hpaccoolplffplr,,-5.0,,5.0,200.0,,10.0,resistive,timed,0.166667,20000;'
   f'coil:heating:electric,{zname} zone electric coil,on 24/7,1.00,autosize,{zname} zone heating coil outlet node,{zname} zone sys outlet node,{zname} zone sys outlet node;'

   f'outdoorair:mixer,{zname} zone outdoor air mixer,{zname} zone mixed air outlet node,{zname} outdoor air node name,{zname} air relief node name,{zname} zone return node;'
   f'outdoorair:nodelist,{zname} outdoor air node name;'
)


# NOTE: incomplete — kept as a reference for future PSZ/ASHRAE Appendix G Sys#3 work.
# Not registered in dictzonesys, so users cannot reach it through createsys.
def zpsz(zname,zbb):

    # incomplete (dfference between using coil system on air loop and unitaryheatcool ??)
    return ''.join([
            #------------ psz ashrae appen g sys#3
            f'branch,{zname} main branch,,airloophvac:outdoorairsystem,{zname} outdoor air system,{zname} supply side inlet node,{zname} mixed air outlet node,airloophvac:unitaryheatcool,{zname},{zname} mixed air outlet node,{zname} supply side outlet node;'
            f'airloophvac:unitaryheatcool,{zname},on 24/7,{zname} mixed air outlet node,{zname} supply side outlet node,on 24/7,autosize,autosize,autosize,autosize,{zname},fan:constantvolume,{zname} supply fan,blowthrough,coil:heating:fuel,{zname} heating coil,coil:cooling:dx:singlespeed,{zname} dx cooling coil,none;'
            f'coil:cooling:dx:singlespeed,{zname} dx cooling coil,on 24/7,autosize,autosize,3.0000,autosize,773.300000,{zname} supply fan outlet,{zname} dx cooling coil outlet,dxclgcoiltotalclgcapfunctemperature,dxclgcoiltotalclgcapfuncflowfraction,dxclgcoilenergyinputratiofunctemperature,dxclgcoilenergyinputratiofuncflowfraction,dxcoilpartloadfractioncorrelation,-25.00,0.0,0.0,0.0,0.0,,aircooled,0.90,autosize,0.00,0.000,10.00;'
            f'setpointmanager:mixedair,{zname} heating coil mixed air manager,temperature,{zname} supply side outlet node,{zname} supply fan inlet node,{zname} supply side outlet node,{zname} supply fan inlet node;'
           ])



def zwhp(zname,zbb):
    if zbb:
        zeq = dictbaseboard[zbb].fun(zname) + f'zonehvac:equipmentlist,{zname} equipment,sequentialload,zonehvac:airdistributionunit,{zname} adu,1,1,,,zonehvac:watertoairheatpump,{zname} zone sys,2,2,,,{dictbaseboard[zbb].obj},{zname} baseboard,3,3;'
    else:
        zeq = f'zonehvac:equipmentlist,{zname} equipment,sequentialload,zonehvac:airdistributionunit,{zname} adu,1,1,,,zonehvac:watertoairheatpump,{zname} zone sys,2,2;'

    return zeq + (
#   f'zonecontrol:thermostat,{zname} thermostat,{zname},control type schedule: always 4,thermostatsetpoint:dualsetpoint,dual sp;'
   f'zonehvac:equipmentconnections,{zname},{zname} equipment,{zname} zone supply nodelist,{zname} zone return node,{zname} zone air node,{zname} zone mixer inlet node;'
   f'zonehvac:airdistributionunit,{zname} adu,{zname} adu outlet node,airterminal:singleduct:vav:noreheat,{zname} single duct vav no reheat,0.0,0.0;'
   f'airterminal:singleduct:vav:noreheat,{zname} single duct vav no reheat,on 24/7,{zname} adu outlet node,{zname} zone splitter outlet node,autosize,constant,1;'
   f'nodelist,{zname} zone supply nodelist,{zname} adu outlet node,{zname} zone sys outlet node;'

   f'zonehvac:watertoairheatpump,{zname} zone sys,on 24/7,{zname} zone return node,{zname} zone sys outlet node,outdoorair:mixer,{zname} zone outdoor air mixer,autosize,autosize,autosize,,0,0,0,fan:systemmodel,{zname} zone supply fan,coil:heating:watertoairheatpump:equationfit,{zname} zone heating coil,coil:cooling:watertoairheatpump:equationfit,{zname} zone cooling coil,coil:heating:electric,{zname} zone electric coil,autosize,20.0,,blowthrough,on 24/7;'
   f'fan:systemmodel,{zname} zone supply fan,on 24/7,{zname} zone mixed air outlet node,{zname} zone supply fan outlet node,autosize,discrete,0.0,75.0,0.9,1.0,autosize,totalefficiencyandpressure,,,0.7;'
#   f'fan:constantvolume,{zname} zone supply fan,on 24/7,0.700000,100.00,autosize,0.900000,1.00,{zname} zone mixed air outlet node,{zname} zone supply fan outlet node,general;'

   f'branch,{zname} zone hw demand side branch,,coil:heating:watertoairheatpump:equationfit,{zname} zone heating coil,{zname} zone heating coil water inlet node,{zname} zone heating coil water outlet node;'
   f'branch,{zname} zone chw demand side branch,,coil:cooling:watertoairheatpump:equationfit,{zname} zone cooling coil,{zname} zone cooling coil water inlet node,{zname} zone cooling coil water outlet node;'

   f'coil:cooling:watertoairheatpump:equationfit,{zname} zone cooling coil,on 24/7,{zname} zone cooling coil water inlet node,{zname} zone cooling coil water outlet node,{zname} zone supply fan outlet node,{zname} zone cooling coil outlet node,autosize,autosize,autosize,autosize,4.5,30.0,27.0,19.0,totcoolcapcurve,coolsenscapcurve,coolpowcurve,hpaccoolplffplr,0,0,2.5,60,60;'
   f'coil:heating:watertoairheatpump:equationfit,{zname} zone heating coil,on 24/7,{zname} zone heating coil water inlet node,{zname} zone heating coil water outlet node,{zname} zone cooling coil outlet node,{zname} zone heating coil outlet node,autosize,autosize,autosize,5,20.0,20.0,1.0,heatcapcurve,heatpowcurve,hpacheatplffplr;'
   f'coil:heating:electric,{zname} zone electric coil,on 24/7,1.00,autosize,{zname} zone heating coil outlet node,{zname} zone sys outlet node,{zname} zone sys outlet node;'

   f'outdoorair:mixer,{zname} zone outdoor air mixer,{zname} zone mixed air outlet node,{zname} zone outdoor air node name,{zname} zone air relief node name,{zname} zone return node;'
   f'outdoorair:nodelist,{zname} zone outdoor air node name;'
    )


def zfcu(zname,zbb):

    if zbb:
        zeq = dictbaseboard[zbb].fun(zname) + f'zonehvac:equipmentlist,{zname} equipment,sequentialload,zonehvac:airdistributionunit,{zname} adu,1,1,,,zonehvac:fourpipefancoil,{zname} zone sys,2,2,,,{dictbaseboard[zbb].obj},{zname} baseboard,3,3;'
    else:
        zeq = f'zonehvac:equipmentlist,{zname} equipment,sequentialload,zonehvac:airdistributionunit,{zname} adu,1,1,,,zonehvac:fourpipefancoil,{zname} zone sys,2,2;'


    return zeq + (
    # other air delivery option is to use airterminal:singleduct:mixer
#   f'zonecontrol:thermostat,{zname} thermostat,{zname},control type schedule: always 4,thermostatsetpoint:dualsetpoint,dual sp;'
   f'zonehvac:equipmentconnections,{zname},{zname} equipment,{zname} zone supply nodelist,{zname} zone return node,{zname} zone air node,{zname} zone mixer inlet node;'
   f'zonehvac:airdistributionunit,{zname} adu,{zname} adu outlet node,airterminal:singleduct:vav:noreheat,{zname} single duct vav no reheat,0.0,0.0;'
   f'airterminal:singleduct:vav:noreheat,{zname} single duct vav no reheat,on 24/7,{zname} adu outlet node,{zname} zone splitter outlet node,autosize,constant,1;'
   f'nodelist,{zname} zone supply nodelist,{zname} adu outlet node,{zname} zone sys outlet node;'

   f'zonehvac:fourpipefancoil,{zname} zone sys,on 24/7,constantfanvariableflow,autosize,0.33,0.66,0.0,,{zname} zone return node,{zname} zone sys outlet node,outdoorair:mixer,{zname} zone outdoor air mixer,fan:constantvolume,{zname} zone supply fan,coil:cooling:water,{zname} zone cooling coil,autosize,0.000000,0.0010,coil:heating:water,{zname} zone heating coil,autosize,0.000000,0.0010;'
   f'fan:constantvolume,{zname} zone supply fan,on 24/7,0.700000,100.00,autosize,0.900000,1.00,{zname} zone mixed air outlet node,{zname} zone supply fan outlet node,general;'

   f'branch,{zname} zone hw demand side branch,,coil:heating:water,{zname} zone heating coil,{zname} zone heating coil water inlet node,{zname} zone heating coil water outlet node;'
   f'branch,{zname} zone chw demand side branch,,coil:cooling:water,{zname} zone cooling coil,{zname} zone cooling coil water inlet node,{zname} zone cooling coil water outlet node;'
   f'coil:cooling:water,{zname} zone cooling coil,on 24/7,autosize,autosize,autosize,autosize,autosize,autosize,autosize,{zname} zone cooling coil water inlet node,{zname} zone cooling coil water outlet node,{zname} zone supply fan outlet node,{zname} zone cooling coil outlet node,simpleanalysis,crossflow,;'
   f'coil:heating:water,{zname} zone heating coil,on 24/7,autosize,autosize,{zname} zone heating coil water inlet node,{zname} zone heating coil water outlet node,{zname} zone cooling coil outlet node,{zname} zone sys outlet node,ufactortimesareaanddesignwaterflowrate,autosize,80.0,16.0,70.0,35.0,0.50;' 

   f'outdoorair:mixer,{zname} zone outdoor air mixer,{zname} zone mixed air outlet node,{zname} zone outdoor air node name,{zname} zone air relief node name,{zname} zone return node;'
   f'outdoorair:nodelist,{zname} zone outdoor air node name;'
    )

def zvrf(zname,zbb):
#   if ((zbb:=zname.split('_')[-1]) in list(dictbaseboard.keys())):
    if zbb:
        zeq = dictbaseboard[zbb].fun(zname) + f'zonehvac:equipmentlist,{zname} equipment,sequentialload,zonehvac:airdistributionunit,{zname} adu,1,1,,,zonehvac:terminalunit:variablerefrigerantflow,{zname} zone sys,2,2,,,{dictbaseboard[zbb].obj},{zname} baseboard,3,3;'
    else:
        zeq = f'zonehvac:equipmentlist,{zname} equipment,sequentialload,zonehvac:airdistributionunit,{zname} adu,1,1,,,zonehvac:terminalunit:variablerefrigerantflow,{zname} zone sys,2,2;'

    return zeq + (
   # vrf zone sys
#  f'zonecontrol:thermostat,{zname} thermostat,{zname},control type schedule: always 4,thermostatsetpoint:dualsetpoint,dual sp;'
   f'zonehvac:equipmentconnections,{zname},{zname} equipment,{zname} zone supply nodelist,{zname} zone return node,{zname} zone air node,{zname} zone mixer inlet node;'
   f'zonehvac:airdistributionunit,{zname} adu,{zname} adu outlet node,airterminal:singleduct:vav:noreheat,{zname} single duct vav no reheat,0.0,0.0;'
   f'airterminal:singleduct:vav:noreheat,{zname} single duct vav no reheat,on 24/7,{zname} adu outlet node,{zname} zone splitter outlet node,autosize,constant,1;'
   f'nodelist,{zname} zone supply nodelist,{zname} adu outlet node,{zname} zone sys outlet node;'

   f'zonehvac:terminalunit:variablerefrigerantflow,{zname} zone sys,on 24/7,{zname} zone return node,{zname} zone sys outlet node,autosize,autosize,autosize,autosize,0.0,0.0,0.0,on 24/7,blowthrough,fan:constantvolume,{zname} zone supply fan,outdoorair:mixer,{zname} zone outdoor air mixer,coil:cooling:dx:variablerefrigerantflow,{zname} zone dx cooling coil,coil:heating:dx:variablerefrigerantflow,{zname} zone dx heating coil,30.0000,20.0000,,;'
   f'fan:constantvolume,{zname} zone supply fan,on 24/7,0.700000,100.00,autosize,0.900000,1.00,{zname} zone mixed air outlet node,{zname} zone supply fan outlet node,general;'

   f'coil:cooling:dx:variablerefrigerantflow,{zname} zone dx cooling coil,on 24/7,autosize,autosize,autosize,vrftucoolcapft,vrfaccoolcapfff,{zname} zone supply fan outlet node,{zname} zone cooling coil outlet node,;'
   f'coil:heating:dx:variablerefrigerantflow,{zname} zone dx heating coil,on 24/7,autosize,autosize,{zname} zone cooling coil outlet node,{zname} zone sys outlet node,vrftuheatcapft,vrfaccoolcapfff;'

   f'outdoorair:mixer,{zname} zone outdoor air mixer,{zname} zone mixed air outlet node,{zname} zone outdoor air node name,{zname} zone air relief node name,{zname} zone return node;'
   f'outdoorair:nodelist,{zname} zone outdoor air node name;'
   )


# zone only ADU types


def zptac(zname,_zbb):
    # zone unit only cannot have air loop/no airloop terminal distribution included
    #this appears to be delivering more oa than ptac under similar settings causing a higher energy consumption than ptac need to review. 
    return ''.join([

               f'zonehvac:packagedterminalairconditioner,{zname} ptac,on 24/7,{zname} ptac inlet node,{zname} ptac outlet node,outdoorair:mixer,{zname} ptac oa mixer,autosize,autosize,autosize,,autosize,autosize,autosize,fan:onoff,{zname} ptfan,coil:heating:electric,{zname} ptac heat coil,coil:cooling:dx:singlespeed,{zname} ptac dxcoil,blowthrough,off;'
               f'outdoorair:mixer,{zname} ptac oa mixer,{zname} ptac mixedair node ,{zname} ptac oa node,{zname} ptac relief node,{zname} ptac inlet node;'
               f'fan:onoff,{zname} ptfan,on 24/7,0.52,331,autosize,0.8,1.0,{zname} ptac mixedair node,{zname} ptac fanoutlet node;'
               f'coil:cooling:dx:singlespeed,{zname} ptac dxcoil,on 24/7,autosize,autosize,3.0,autosize,,934.4,{zname} ptac fanoutlet node,{zname} ptac ccoutlet node ,ptachpaccoolcapft,ptachpaccoolcapfff,ptachpaceirft,ptachpaceirfff,ptachpacplffplr;'
               f'coil:heating:electric,{zname} ptac heat coil,on 24/7,1.0,autosize,{zname} ptac ccoutlet node,{zname} ptac outlet node;'
               f'outdoorair:node,{zname} ptac oa node;'
               f'zonehvac:equipmentconnections,{zname},{zname} equipment,{zname} ptac outlet node,{zname} ptac inlet node,{zname} air node,;'
               f'zonehvac:equipmentlist,{zname} equipment,sequentialload,zonehvac:packagedterminalairconditioner,{zname} ptac,1,1,,;'
   #           f'zonecontrol:thermostat,{zname} thermostat,{zname},control type schedule: always 4,thermostatsetpoint:dualsetpoint,dual sp;'
           ])




def zpthp(zname,_zbb):
    # zone unit only cannot have air loop/no airloop terminal distribution included
    return ''.join([
               f'zonehvac:packagedterminalheatpump,{zname} pthp,on 24/7,{zname} pthp inlet node,{zname} pthp outlet node,outdoorair:mixer,{zname} pthp oa mixer,autosize,autosize,autosize,,autosize,autosize,autosize,fan:onoff,{zname} ptfan,coil:heating:dx:singlespeed,{zname} pthpdxheatcoil,0.001,coil:cooling:dx:singlespeed,{zname} pthpdxcoolcoil,0.001,coil:heating:electric,{zname} pthpsupheater,autosize,-8.0,blowthrough,off;'
               f'outdoorair:mixer,{zname} pthp oa mixer,{zname} pthp mixer outlet node,{zname} pthp oa node,{zname} pthp exhaust node,{zname} pthp inlet node;'
               f'fan:onoff,{zname} ptfan,on 24/7,0.52,331,autosize,0.8,1.0,{zname} pthp mixer outlet node,{zname} pthp fan outlet node;'
               f'coil:cooling:dx:singlespeed,{zname} pthpdxcoolcoil,on 24/7,autosize,autosize,3.0,autosize,,934.4,{zname} pthp fan outlet node,{zname} pthp coolcoil outlet node,hpaccoolcapft,hpaccoolcapfff,hpaceirft,hpaceirfff,hpacplffplr;' 
               f'coil:heating:dx:singlespeed,{zname} pthpdxheatcoil,on 24/7,autosize,3.75,autosize,,934.4,{zname} pthp coolcoil outlet node,{zname} pthp dxheatcoil outlet node,hpacheatcapft,hpacheatcapfff,hpacheateirft,hpacheateirfff,hpaccoolplffplr,,-8.0,,5.0,200.0,,10.0,resistive,ondemand,0.166667,5000;'
               f'coil:heating:electric,{zname} pthpsupheater,on 24/7,1.0,autosize,{zname} pthp dxheatcoil outlet node,{zname} pthp outlet node;'
               f'outdoorair:node,{zname} pthp oa node;'
               f'zonehvac:equipmentconnections,{zname},{zname} equipment,{zname} pthp outlet node,{zname} pthp inlet node,{zname} zone air node,;'
               f'zonehvac:equipmentlist,{zname} equipment,sequentialload,zonehvac:packagedterminalheatpump,{zname} pthp,1,1,,;'
#               f'zonecontrol:thermostat,{zname} thermostat,{zname},control type schedule: always 4,thermostatsetpoint:dualsetpoint,dual sp;'
           ])

def zuhel(zname,_zbb):
    # zone unit only cannot have air loop/no airloop terminal distribution included
    return ''.join([
            f'zonehvac:unitheater,{zname} unit heater,on 24/7,{zname} exhaust node,{zname} inlet node,fan:constantvolume,{zname} unit heaterfan,autosize,coil:heating:electric,{zname} unit heater coil,,no,autosize,0.0,0.001;'
            f'fan:constantvolume,{zname} unit heaterfan,on 24/7,0.53625,49.8,autosize,0.825,1.0,{zname} exhaust node,{zname} fan outlet node,;'
            f'coil:heating:electric,{zname} unit heater coil,on 24/7,1.0,autosize,{zname} fan outlet node,{zname} inlet node;'


            f'zonehvac:equipmentconnections,{zname},{zname} equipment,{zname} inlet node,{zname} exhaust node,{zname} air node,{zname} return node;'
            f'zonehvac:equipmentlist,{zname} equipment,sequentialload,zonehvac:unitheater,{zname} unit heater,1,1,,;'
#            f'zonecontrol:thermostat,{zname} thermostat,{zname},control type schedule: always 4,thermostatsetpoint:dualsetpoint,dual sp;'
           ])




def zuhhw(zname,_zbb):
    # zone unit only cannot have air loop/no airloop terminal distribution included
    return ''.join([
            f'zonehvac:unitheater,{zname} unit heater,on 24/7,{zname} exhaust node,{zname} inlet node,fan:constantvolume,{zname} unit heaterfan,autosize,coil:heating:water,{zname} unit heater coil,,no,autosize,0.0,0.001;'
            f'fan:constantvolume,{zname} unit heaterfan,on 24/7,0.53625,49.8,autosize,0.825,1.0,{zname} exhaust node,{zname} fan outlet node,;'

            f'zonehvac:equipmentconnections,{zname},{zname} equipment,{zname} inlet node,{zname} exhaust node,{zname} air node,{zname} return node;'
            f'zonehvac:equipmentlist,{zname} equipment,sequentialload,zonehvac:unitheater,{zname} unit heater,1,1,,;'

            f'coil:heating:water,{zname} unit heater coil,on 24/7,autosize,autosize,{zname} zone heating coil water inlet node,{zname} zone heating coil water outlet node,{zname} fan outlet node,{zname} inlet nodeufactortimesareaanddesignwaterflowrate,autosize,80,16,70,35,0.50;'
            f'branch,{zname} zone hw demand side branch,,coil:heating:water,{zname} zone heating coil,{zname} zone heating coil water inlet node,{zname} zone heating coil water outlet node;'

#           f'zonecontrol:thermostat,{zname} thermostat,{zname},control type schedule: always 4,thermostatsetpoint:dualsetpoint,dual sp;'
           ])


def hwbaseboard(zname):
    """Generate hot water baseboard heater IDF string.

    Args:
        zname: Zone name
    """
    return ''.join([
        f'branch,{zname} zone baseboard demand side branch,,zonehvac:baseboard:convective:water,{zname} baseboard,{zname} zone baseboard water inlet node,{zname} zone baseboard water outlet node;',
        f'zonehvac:baseboard:convective:water,{zname} baseboard,on 24/7,{zname} zone baseboard water inlet node,{zname} zone baseboard water outlet node,heatingdesigncapacity,autosize,,,500.,0.0013,0.001;'
    ])

def elbaseboard(zname):
    """Generate electric baseboard heater IDF string.

    Args:
        zname: Zone name
    """
    return f'zonehvac:baseboard:convective:electric,{zname} baseboard,on 24/7,heatingdesigncapacity,autosize,,,0.95;'




# Baseboard heating systems
# Format: 'key': (function, energyplus_object_type, description)
dictbaseboard = {
    'bhw':bb(hwbaseboard, 'zonehvac:baseboard:convective:water', 'Hot water baseboard heater connected to hot water plant loop'),
    'bel':bb(elbaseboard, 'zonehvac:baseboard:convective:electric', 'Electric baseboard heater with resistance heating')
    }


# Zone air distribution units
# Format: 'key': (function, description)
dictzoneADU = {
    'cv':(zcv, 'Constant volume air terminal with no reheat'),
    'vavhw':(zvavhw, 'VAV terminal with hot water reheat coil'),
    'vavel':(zvavel, 'VAV terminal with electric reheat coil'),
    'cb':(zcb, 'Chilled beam system (active or passive) [DOAS Only]'),
    'fcu':(zfcu, 'Fan coil unit with heating and cooling coils [DOAS Only]'),
    'ahp':(zahp, 'Air-source heat pump serving single zone [DOAS Only]'),
    'whp':(zwhp, 'Water-source heat pump connected to condenser water loop [DOAS Only]'),
    'vrf':(zvrf, 'Variable refrigerant flow (VRF) terminal unit [DOAS Only]'),

    'ptac':(zptac, 'Packaged terminal air conditioner [zone-only, no air loop]'),
    'pthp':(zpthp, 'Packaged terminal heat pump [zone-only, no air loop]'),
    'uhel':(zuhel, 'Electric unit heater [zone-only, no air loop]'),
    'uhhw':(zuhhw, 'Hot water unit heater [zone-only, no air loop]'),
}


# Zone systems requiring hot water (hw) or chilled water (chw) loops. And baseboard systems containing hw coil.
# List Types are separated by | operator 
ZNSYS_HW   = "vavhw|fcu|cb|whp|uhhw"
ZNSYS_CHW  = "fcu|cb|whp"
ZNSYS_HWBB = "bhw"


def get_zone_systems():
    """Return dict of available zone system types with descriptions.

    Returns:
        Dict mapping zone system type to description string

    Example:
        >>> systems = get_zone_systems()
        >>> print(systems['fcu'])
        'Fan coil unit with heating and cooling coils'
        >>> # For validation, just use .keys()
        >>> valid_types = systems.keys()
    """
    return {key: val[1] if len(val) > 1 else 'No description' for key, val in dictzoneADU.items()}


def get_baseboard_types():
    """Return dict of available baseboard types with descriptions.

    Returns:
        Dict mapping baseboard type to description string

    Example:
        >>> baseboards = get_baseboard_types()
        >>> print(baseboards['bhw'])
        'Hot water baseboard heater connected to hot water plant loop'
        >>> # For validation, just use .keys()
        >>> valid_types = baseboards.keys()
    """
    return {key: val.desc for key, val in dictbaseboard.items()}




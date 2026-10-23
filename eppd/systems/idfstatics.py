"""
Bharath Karambakkam
e-mail:kBharathk@gmail.com

Purpose: holds static items and library items to be used by createsys function
"""

# Building parameters
# All energyplus class definitions should be in lowercase as python is case-sensitive.

# Simulation control objects
_SIMULATION_OBJECTS = [
    "building",
    "shadowcalculation",
    "surfaceconvectionalgorithm:inside",
    "surfaceconvectionalgorithm:outside",
    "heatbalancealgorithm",
    "heatbalancesettings:conductionfinitedifference",
    "zoneairheatbalancealgorithm",
    "zoneaircontaminantbalance",
    "zoneairmassflowconservation",
    "zonecapacitancemultiplier:researchspecial",
    "timestep",
    "output:diagnostics",
    "convergencelimits",
    "hvacsystemrootfindingalgorithm",
    "compliance:building",
]

# Site and weather objects
_SITE_WEATHER_OBJECTS = [
    "site:location",
    "site:variablelocation",
    "sizingperiod:designday",
    "sizingperiod:weatherfiledays",
    "sizingperiod:weatherfileconditiontype",
    "runperiod",
    "runperiodcontrol:specialdays",
    "runperiodcontrol:daylightsavingtime",
    "weatherproperty:skytemperature",
    "site:weatherstation",
    "site:heightvariation",
    "site:groundtemperature:buildingsurface",
    "site:groundtemperature:fcfactormethod",
    "site:groundtemperature:shallow",
    "site:groundtemperature:deep",
    "site:groundtemperature:undisturbed:finitedifference",
    "site:groundtemperature:undisturbed:kusudaachenbach",
    "site:groundtemperature:undisturbed:xing",
    "site:grounddomain:slab",
    "site:grounddomain:basement",
    "site:groundreflectance",
    "site:groundreflectance:snowmodifier",
    "site:watermainstemperature",
    "site:precipitation",
    "site:solarandvisiblespectrum",
    "site:spectrumdata",
]

# Zone and space objects
_ZONE_OBJECTS = [
    "space",
    "spacelist",
    "zone",
    "zonelist",
    "zonegroup",
    "matrix:twodimension",
    "hybridmodel:zone",
]

# Schedule objects
_SCHEDULE_OBJECTS = [
    "scheduletypelimits",
    "schedule:day:hourly",
    "schedule:day:interval",
    "schedule:day:list",
    "schedule:week:daily",
    "schedule:week:compact",
    "schedule:year",
    "schedule:compact",
    "schedule:constant",
    "schedule:file:shading",
    "schedule:file",
]

# All remaining building objects
# Note: These objects cover materials, constructions, surfaces, loads, HVAC controls,
# generators, economics, etc. organized in EnergyPlus IDD order
_REMAINING_BUILDING_OBJECTS = [
    "material",
    "material:nomass",
    "material:infraredtransparent",
    "material:airgap",
    "material:roofvegetation",
    "roofirrigation",
    "windowmaterial:simpleglazingsystem",
    "windowmaterial:glazing",
    "windowmaterial:glazinggroup:thermochromic",
    "windowmaterial:glazing:refractionextinctionmethod",
    "windowmaterial:gas",
    "windowgap:supportpillar",
    "windowgap:deflectionstate",
    "windowmaterial:gasmixture",
    "windowmaterial:gap",
    "windowmaterial:shade",
    "windowmaterial:complexshade",
    "windowmaterial:blind",
    "windowmaterial:screen",
    "windowmaterial:shade:equivalentlayer",
    "windowmaterial:drape:equivalentlayer",
    "windowmaterial:blind:equivalentlayer",
    "windowmaterial:screen:equivalentlayer",
    "windowmaterial:glazing:equivalentlayer",
    "windowmaterial:gap:equivalentlayer",
    "materialproperty:moisturepenetrationdepth:settings",
    "materialproperty:phasechange",
    "materialproperty:phasechangehysteresis",
    "materialproperty:variablethermalconductivity",
    "materialproperty:variableabsorptance",
    "materialproperty:heatandmoisturetransfer:settings",
    "materialproperty:heatandmoisturetransfer:sorptionisotherm",
    "materialproperty:heatandmoisturetransfer:suction",
    "materialproperty:heatandmoisturetransfer:redistribution",
    "materialproperty:heatandmoisturetransfer:diffusion",
    "materialproperty:heatandmoisturetransfer:thermalconductivity",
    "materialproperty:glazingspectraldata",
    "construction",
    "construction:cfactorundergroundwall",
    "construction:ffactorgroundfloor",
    "constructionproperty:internalheatsource",
    "construction:airboundary",
    "windowthermalmodel:params",
    "windowscalculationengine",
    "construction:complexfenestrationstate",
    "construction:windowequivalentlayer",
    "construction:windowdatafile",
    "globalgeometryrules",
    "geometrytransform",
    "buildingsurface:detailed",
    "wall:detailed",
    "roofceiling:detailed",
    "floor:detailed",
    "wall:exterior",
    "wall:adiabatic",
    "wall:underground",
    "wall:interzone",
    "roof",
    "ceiling:adiabatic",
    "ceiling:interzone",
    "floor:groundcontact",
    "floor:adiabatic",
    "floor:interzone",
    "fenestrationsurface:detailed",
    "window",
    "door",
    "glazeddoor",
    "window:interzone",
    "door:interzone",
    "glazeddoor:interzone",
    "windowshadingcontrol",
    "windowproperty:frameanddivider",
    "windowproperty:airflowcontrol",
    "windowproperty:stormwindow",
    "internalmass",
    "shading:site",
    "shading:building",
    "shading:site:detailed",
    "shading:building:detailed",
    "shading:overhang",
    "shading:overhang:projection",
    "shading:fin",
    "shading:fin:projection",
    "shading:zone:detailed",
    "shadingproperty:reflectance",
    "surfaceproperty:heattransferalgorithm",
    "surfaceproperty:heattransferalgorithm:multiplesurface",
    "surfaceproperty:heattransferalgorithm:surfacelist",
    "surfaceproperty:heattransferalgorithm:construction",
    "surfaceproperty:heatbalancesourceterm",
    "surfacecontrol:movableinsulation",
    "surfaceproperty:othersidecoefficients",
    "surfaceproperty:othersideconditionsmodel",
    "surfaceproperty:underwater",
    "foundation:kiva",
    "foundation:kiva:settings",
    "surfaceproperty:exposedfoundationperimeter",
    "surfaceconvectionalgorithm:inside:adaptivemodelselections",
    "surfaceconvectionalgorithm:outside:adaptivemodelselections",
    "surfaceconvectionalgorithm:inside:usercurve",
    "surfaceconvectionalgorithm:outside:usercurve",
    "surfaceproperty:convectioncoefficients",
    "surfaceproperty:convectioncoefficients:multiplesurface",
    "surfaceproperties:vaporcoefficients",
    "surfaceproperty:exteriornaturalventedcavity",
    "surfaceproperty:solarincidentinside",
    "surfaceproperty:incidentsolarmultiplier",
    "surfaceproperty:localenvironment",
    "zoneproperty:localenvironment",
    "surfaceproperty:surroundingsurfaces",
    "surfaceproperty:groundsurfaces",
    "complexfenestrationproperty:solarabsorbedlayers",
    "zoneproperty:userviewfactors:bysurfacename",
    "groundheattransfer:control",
    "groundheattransfer:slab:materials",
    "groundheattransfer:slab:matlprops",
    "groundheattransfer:slab:boundconds",
    "groundheattransfer:slab:bldgprops",
    "groundheattransfer:slab:insulation",
    "groundheattransfer:slab:equivalentslab",
    "groundheattransfer:slab:autogrid",
    "groundheattransfer:slab:manualgrid",
    "groundheattransfer:slab:xface",
    "groundheattransfer:slab:yface",
    "groundheattransfer:slab:zface",
    "groundheattransfer:basement:simparameters",
    "groundheattransfer:basement:matlprops",
    "groundheattransfer:basement:insulation",
    "groundheattransfer:basement:surfaceprops",
    "groundheattransfer:basement:bldgdata",
    "groundheattransfer:basement:interior",
    "groundheattransfer:basement:combldg",
    "groundheattransfer:basement:equivautogrid",
    "groundheattransfer:basement:autogrid",
    "groundheattransfer:basement:manualgrid",
    "groundheattransfer:basement:xface",
    "groundheattransfer:basement:yface",
    "groundheattransfer:basement:zface",
    "roomairmodeltype",
    "roomair:temperaturepattern:userdefined",
    "roomair:temperaturepattern:constantgradient",
    "roomair:temperaturepattern:twogradient",
    "roomair:temperaturepattern:nondimensionalheight",
    "roomair:temperaturepattern:surfacemapping",
    "roomair:node",
    "roomairsettings:onenodedisplacementventilation",
    "roomairsettings:threenodedisplacementventilation",
    "roomairsettings:crossventilation",
    "roomairsettings:underfloorairdistributioninterior",
    "roomairsettings:underfloorairdistributionexterior",
    "roomair:node:airflownetwork",
    "roomair:node:airflownetwork:adjacentsurfacelist",
    "roomair:node:airflownetwork:internalgains",
    "roomair:node:airflownetwork:hvacequipment",
    "roomairsettings:airflownetwork",
    "people",
    "comfortviewfactorangles",
    "lights",
    "electricequipment",
    "gasequipment",
    "hotwaterequipment",
    "steamequipment",
    "otherequipment",
    "indoorlivingwall",
    "zonecontaminantsourceandsink:carbondioxide",
    "zonecontaminantsourceandsink:generic:constant",
    "surfacecontaminantsourceandsink:generic:pressuredriven",
    "zonecontaminantsourceandsink:generic:cutoffmodel",
    "zonecontaminantsourceandsink:generic:decaysource",
    "surfacecontaminantsourceandsink:generic:boundarylayerdiffusion",
    "surfacecontaminantsourceandsink:generic:depositionvelocitysink",
    "zonecontaminantsourceandsink:generic:depositionratesink",
    "daylighting:controls",
    "daylighting:referencepoint",
    "daylighting:delight:complexfenestration",
    "daylightingdevice:tubular",
    "daylightingdevice:shelf",
    "daylightingdevice:lightwell",
    "zoneinfiltration:designflowrate",
    "zoneinfiltration:effectiveleakagearea",
    "zoneinfiltration:flowcoefficient",
    "zoneventilation:designflowrate",
    "zoneventilation:windandstackopenarea",
    "zoneairbalance:outdoorair",
    "zonemixing",
    "zonecrossmixing",
    "zonerefrigerationdoormixing",
    "zoneearthtube",
    "zoneearthtube:parameters",
    "zonecooltower:shower",
    "zonethermalchimney",
    "airflownetwork:simulationcontrol",
    "airflownetwork:multizone:zone",
    "airflownetwork:multizone:surface",
    "airflownetwork:multizone:referencecrackconditions",
    "airflownetwork:multizone:surface:crack",
    "airflownetwork:multizone:surface:effectiveleakagearea",
    "airflownetwork:multizone:specifiedflowrate",
    "airflownetwork:multizone:component:detailedopening",
    "airflownetwork:multizone:component:simpleopening",
    "airflownetwork:multizone:component:horizontalopening",
    "airflownetwork:multizone:component:zoneexhaustfan",
    "airflownetwork:multizone:externalnode",
    "airflownetwork:multizone:windpressurecoefficientarray",
    "airflownetwork:multizone:windpressurecoefficientvalues",
    "airflownetwork:zonecontrol:pressurecontroller",
    "airflownetwork:distribution:node",
    "airflownetwork:distribution:component:leak",
    "airflownetwork:distribution:component:leakageratio",
    "airflownetwork:distribution:component:duct",
    "airflownetwork:distribution:component:fan",
    "airflownetwork:distribution:component:coil",
    "airflownetwork:distribution:component:heatexchanger",
    "airflownetwork:distribution:component:terminalunit",
    "airflownetwork:distribution:component:constantpressuredrop",
    "airflownetwork:distribution:component:outdoorairflow",
    "airflownetwork:distribution:component:reliefairflow",
    "airflownetwork:distribution:linkage",
    "airflownetwork:distribution:ductviewfactors",
    "airflownetwork:distribution:ductsizing",
    "airflownetwork:occupantventilationcontrol",
    "airflownetwork:intrazone:node",
    "airflownetwork:intrazone:linkage",
    "duct:loss:conduction",
    "duct:loss:leakage",
    "duct:loss:makeupair",
    "exterior:lights",
    "exterior:fuelequipment",
    "exterior:waterequipment",
    "designspecification:outdoorair",
    "designspecification:outdoorair:spacelist",
    "designspecification:zoneairdistribution",
    "sizing:parameters",
    "sizing:zone",
    "designspecification:zonehvac:sizing",
    "designspecification:airterminal:sizing",
    "zonecontrol:humidistat",
    "zonecontrol:thermostat",
    "zonecontrol:thermostat:operativetemperature",
    "zonecontrol:thermostat:thermalcomfort",
    "zonecontrol:thermostat:temperatureandhumidity",
    "thermostatsetpoint:singleheating",
    "thermostatsetpoint:singlecooling",
    "thermostatsetpoint:singleheatingorcooling",
    "thermostatsetpoint:dualsetpoint",
    "thermostatsetpoint:thermalcomfort:fanger:singleheating",
    "thermostatsetpoint:thermalcomfort:fanger:singlecooling",
    "thermostatsetpoint:thermalcomfort:fanger:singleheatingorcooling",
    "thermostatsetpoint:thermalcomfort:fanger:dualsetpoint",
    "zonecontrol:thermostat:stageddualsetpoint",
    "zonecontrol:contaminantcontroller",
    "refrigeration:case",
    "refrigeration:compressorrack",
    "refrigeration:caseandwalkinlist",
    "refrigeration:condenser:aircooled",
    "refrigeration:condenser:evaporativecooled",
    "refrigeration:condenser:watercooled",
    "refrigeration:condenser:cascade",
    "refrigeration:gascooler:aircooled",
    "refrigeration:transferloadlist",
    "refrigeration:subcooler",
    "refrigeration:compressor",
    "refrigeration:compressorlist",
    "refrigeration:system",
    "refrigeration:transcriticalsystem",
    "refrigeration:secondarysystem",
    "refrigeration:walkin",
    "refrigeration:airchiller",
    "zonehvac:refrigerationchillerset",
    "outdoorair:node",
    "demandmanagerassignmentlist",
    "demandmanager:exteriorlights",
    "demandmanager:lights",
    "demandmanager:electricequipment",
    "demandmanager:thermostats",
    "demandmanager:ventilation",
    "generator:internalcombustionengine",
    "generator:combustionturbine",
    "generator:microturbine",
    "generator:photovoltaic",
    "photovoltaicperformance:simple",
    "photovoltaicperformance:equivalentone-diode",
    "photovoltaicperformance:sandia",
    "generator:pvwatts",
    "electricloadcenter:inverter:pvwatts",
    "generator:fuelcell",
    "generator:fuelcell:powermodule",
    "generator:fuelcell:airsupply",
    "generator:fuelcell:watersupply",
    "generator:fuelcell:auxiliaryheater",
    "generator:fuelcell:exhaustgastowaterheatexchanger",
    "generator:fuelcell:electricalstorage",
    "generator:fuelcell:inverter",
    "generator:fuelcell:stackcooler",
    "generator:microchp",
    "generator:microchp:nonnormalizedparameters",
    "generator:fuelsupply",
    "generator:windturbine",
    #    "electricloadcenter:generators",
    #    "electricloadcenter:inverter:simple",
    #    "electricloadcenter:inverter:functionofpower",
    #    "electricloadcenter:inverter:lookuptable",
    #    "electricloadcenter:storage:simple",
    #    "electricloadcenter:storage:battery",
    #    "electricloadcenter:storage:liionnmcbattery",
    #    "electricloadcenter:transformer",
    #    "electricloadcenter:distribution",
    #    "electricloadcenter:storage:converter",
    "wateruse:equipment",
    "wateruse:storage",
    "wateruse:well",
    "wateruse:raincollector",
    "curve:linear",
    "curve:quadlinear",
    "curve:quintlinear",
    "curve:quadratic",
    "curve:cubic",
    "curve:quartic",
    "curve:exponent",
    "curve:bicubic",
    "curve:biquadratic",
    "curve:quadraticlinear",
    "curve:cubiclinear",
    "curve:triquadratic",
    "curve:functional:pressuredrop",
    "curve:fanpressurerise",
    "curve:exponentialskewnormal",
    "curve:sigmoid",
    "curve:exponentialdecay",
    "curve:doubleexponentialdecay",
    "curve:chillerpartloadwithlift",
    "table:independentvariable",
    "table:independentvariablelist",
    "table:lookup",
    "currencytype",
    "componentcost:adjustments",
    "componentcost:reference",
    "componentcost:lineitem",
    "utilitycost:tariff",
    "utilitycost:qualify",
    "utilitycost:charge:simple",
    "utilitycost:charge:block",
    "utilitycost:ratchet",
    "utilitycost:variable",
    "utilitycost:computation",
    "output:meter:meterfileonly",
    # These should be redefined xml outputs are generated. If using eso processor do not run simulaiton for sizing period.
    "output:table:summaryreports",
    "simulationcontrol",
    "outputcontrol:table:style",
]


sch_par = (
    # Schedules used in templates
    "schedule:compact,off,any number,through: 12/31,for: alldays,until: 24:00,0;"
    "schedule:compact,on,any number,through: 12/31,for: alldays,until: 24:00,1;"
    "schedule:compact,on 24/7,any number,through: 12/31,for: alldays,until: 24:00,1;"
    "schedule:compact,onsummerdesignday,any number,through: 12/31,for: summerdesignday,until: 24:00,1,for: allotherdays,until: 24:00,0;"
    "schedule:compact,onwinterdesignday,any number,through: 12/31,for: winterdesignday,until: 24:00,1,for: allotherdays,until: 24:00,0;"
    "schedule:compact,opaqueshade,any number,through: 12/31,for: alldays,until: 24:00,0;"
    "schedule:compact,dhw,fraction,through: 31 dec,for: weekdays summerdesignday,until: 07:00,0,until: 08:00,0.25,until: 09:00,0.5,until: 12:00,1,until: 14:00,0.75,until: 17:00,1,until: 18:00,0.5,until: 19:00,0.25,until: 24:00,0,for: weekends,until: 24:00,0,for: holidays,until: 24:00,0,for: winterdesignday allotherdays,until: 24:00,0;"
    "schedule:compact,equip,fraction,through: 12/31,for: weekdays summerdesignday,until: 05:00,0.05,until: 07:00,0.1,until: 08:00,0.3,until: 17:00,0.9,until: 18:00,0.5,until: 20:00,0.3,until: 22:00,0.2,until: 23:00,0.1,until: 24:00,0.05,for: saturday winterdesignday,until: 06:00,0.05,until: 08:00,0.1,until: 12:00,0.3,until: 17:00,0.15,until: 24:00,0.05,for: sunday holidays allotherdays,until: 24:00,0.05;"
    "schedule:compact,lt,fraction,through: 12/31,for: weekdays summerdesignday,until: 05:00,0.05,until: 07:00,0.1,until: 08:00,0.3,until: 17:00,0.9,until: 18:00,0.5,until: 20:00,0.3,until: 22:00,0.2,until: 23:00,0.1,until: 24:00,0.05,for: saturday winterdesignday,until: 06:00,0.05,until: 08:00,0.1,until: 12:00,0.3,until: 17:00,0.15,until: 24:00,0.05,for: sunday holidays allotherdays,until: 24:00,0.05;"
    "schedule:compact,occ,fraction,through: 12/31,for: weekdays summerdesignday,until: 06:00,0.0,until: 07:00,0.1,until: 08:00,0.2,until: 12:00,0.95,until: 13:00,0.5,until: 17:00,0.95,until: 18:00,0.3,until: 22:00,0.1,until: 24:00,0.0,for: saturday winterdesignday,until: 06:00,0.0,until: 08:00,0.1,until: 12:00,0.3,until: 17:00,0.1,until: 18:00,0.05,until: 24:00,0.0,for: sunday holidays allotherdays,until: 06:00,0.0,until: 18:00,0.0,until: 24:00,0.0;"
    "schedule:compact,fan,on/off,through: 12/31,for: weekdays summerdesignday,until: 06:00,0.0,until: 22:00,1.0,until: 24:00,0.0,for: saturday winterdesignday,until: 06:00,0.0,until: 18:00,1.0,until: 24:00,0.0,for: sunday holidays allotherdays,until: 24:00,0.0;"
    "schedule:compact,hot water flow set point temperature: always 80.0 c,any number,through: 12/31,for: alldays,until: 24:00,80;"
    "schedule:day:hourly,0,any number,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;"
    "schedule:day:hourly,50,any number,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50,50;"
    "schedule:day:hourly,off,fraction,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0;"
    "schedule:day:hourly,summer control type day sch,control type,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4;"
    "schedule:day:hourly,summer control type day sch - cool,control type,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2;"
    "schedule:day:hourly,winter control type day sch,control type,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4;"
    "schedule:day:hourly,winter control type day sch - heat,control type,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1;"
    "schedule:week:daily,off,off,off,off,off,off,off,off,off,off,off,off,off;"
    "schedule:week:daily,summer control type week sch,summer control type day sch,summer control type day sch,summer control type day sch,summer control type day sch,summer control type day sch,summer control type day sch,summer control type day sch,summer control type day sch,summer control type day sch,summer control type day sch,summer control type day sch,summer control type day sch;"
    "schedule:week:daily,summer control type week sch - cool,summer control type day sch - cool,summer control type day sch - cool,summer control type day sch - cool,summer control type day sch - cool,summer control type day sch - cool,summer control type day sch - cool,summer control type day sch - cool,summer control type day sch - cool,summer control type day sch - cool,summer control type day sch - cool,summer control type day sch - cool,summer control type day sch - cool;"
    "schedule:week:daily,winter control type week sch,winter control type day sch,winter control type day sch,winter control type day sch,winter control type day sch,winter control type day sch,winter control type day sch,winter control type day sch,winter control type day sch,winter control type day sch,winter control type day sch,winter control type day sch,winter control type day sch;"
    "schedule:week:daily,winter control type week sch - heat,winter control type day sch - heat,winter control type day sch - heat,winter control type day sch - heat,winter control type day sch - heat,winter control type day sch - heat,winter control type day sch - heat,winter control type day sch - heat,winter control type day sch - heat,winter control type day sch - heat,winter control type day sch - heat,winter control type day sch - heat,winter control type day sch - heat;"
    "scheduletypelimits,any number;"
    "scheduletypelimits,control type,0,4,discrete;"
    "scheduletypelimits,fraction,0.0,1.0,continuous;"
    "scheduletypelimits,on/off,0,1,discrete;"
    "scheduletypelimits,temperature,-60,200,continuous;"
    "thermostatsetpoint:dualsetpoint,dual sp,heating setpoint schedule,cooling setpoint schedule;"
    "schedule:compact,heating setpoint schedule,temperature,through: 12/31,for: weekdays summerdesignday,until: 06:00,  18.33,until: 22:00,  21.11,until: 24:00,  18.33,for: saturday winterdesignday,until: 06:00,  18.33,until: 18:00,  21.11,until: 24:00,  18.33,for: sunday holidays allotherdays,until: 24:00,  18.33;"
    "schedule:compact,cooling setpoint schedule,temperature,through: 12/31,for: weekdays summerdesignday,until: 06:00,  27.78,until: 22:00,  23.89,until: 24:00,  27.78,for: saturday winterdesignday,until: 06:00,  27.78,until: 18:00,  23.89,until: 24:00,  27.78,for: sunday holidays allotherdays,until: 24:00,  27.78;"
    "schedule:compact,control type schedule: always 4,any number,through: 12/31,for: alldays,until: 24:00,4;"
    "schedule:compact,min supply air flow fraction schedule: always 0.3,any number,through: 12/31,for: alldays,until: 24:00,0.3;"
    "schedule:compact,cooling set point temperature: always 14.0 c,any number,through: 12/31,for: alldays,until: 24:00,14;"
    "schedule:compact,chilled water flow set point temperature: always 6 c,any number,through: 12/31,for: alldays,until: 24:00,6;"
    "schedule:compact,condenser flow set point temperature: always 29.0 c,any number,through: 12/31,for: alldays,until: 24:00,29;"
    "schedule:compact,wlhp high,temperature,through: 12/31,for: alldays,until: 24:00,23.22;"
    "schedule:compact,wlhp low,temperature,through: 12/31,for: alldays,until: 24:00,15.56;"
    "Schedule:Compact,dhw setpoint,Temperature,Through: 12/31,For: AllDays,Until: 24:00,60.0;"
)


sysstatic = (
    # curves used in system templates.
    "table:independentvariable,airflowratio,linear,linear,0.0,10.0,,dimensionless,,,,0.75,1.0;"
    "table:independentvariablelist,effectiveness_independentvariablelist,airflowratio;"
    "table:lookup,seneffectivenesstable,effectiveness_independentvariablelist,divisoronly,0.7,0.0,10.0,dimensionless,,,,0.75,0.70;"
    "table:lookup,lateffectivenesstable,effectiveness_independentvariablelist,divisoronly,0.65,0.0,10.0,dimensionless,,,,0.70,0.65;"
    # heat pump water heater
    "curve:biquadratic,hpwhheatingcapftemp,0.369827,0.043341,-0.00023,0.000466,0.000026,-0.00027,0.0,40.0,20.0,90.0,,,temperature,temperature,dimensionless;"
    "curve:quadratic,hpwhplffplr,0.75,0.25,0.0,0.0,1.0;"
    "curve:biquadratic,hpwhheatingcopftemp,1.19713,0.077849,-0.0000016,-0.02675,0.000296,-0.00112,0.0,40.0,20.0,90.0,,,temperature,temperature,dimensionless;"
    # ptac curves
    "curve:biquadratic,ptachpaccoolcapft,0.942587793,0.009543347,0.000683770,-0.011042676,0.000005249,-0.000009720,12.77778,23.88889,18.3,46.11111;"
    "curve:quadratic,ptachpaccoolcapfff,0.8,0.2,0.0,0.5,1.5;"
    "curve:biquadratic,ptachpaceirft,0.342414409,0.034885008,-0.000623700,0.004977216,0.000437951,-0.000728028,12.77778,23.88889,18.3,46.11111;"
    "curve:quadratic,ptachpaceirfff,1.1552,-0.1808,0.0256,0.5,1.5;"
    "curve:quadratic,ptachpacplffplr,0.85,0.15,0.0,0.0,1.0;"
    # variable speed dx
    "curve:quadratic ,doas dx coil shr -ff,0.9317 ,-0.0077 ,0.0760 ,0.69,1.30;"
    "curve:biquadratic,doas dx coil shr -ft ,1.3294540786 ,-0.0990649255 ,0.0008310043 ,0.0652277735 ,-0.0000793358 ,-0.0005874422 ,24.44 ,26.67 ,29.44 ,46.1,0.6661 ,1.6009 , temperature ,temperature ,dimensionless;"
    "curve:cubic,packagedratedcooleirfflow,1.0079484,0.34544129,-.6922891,0.33889943,0.5,1.5,,,dimensionless,dimensionless;"
    "curve:quadratic,varspeedcyclingplffplr,0.85,0.15,0.0,0.0,1.0;"
    "curve:cubic,packagedratedcoolcapfflow,0.47278589,1.2433415,-1.0387055,0.32257813,0.5,1.5,,,dimensionless,dimensionless;"
    "curve:biquadratic,varspeedcoolcapft,0.476428e+00,0.401147e-01,0.226411e-03,-0.827136e-03,-0.732240e-05,-0.446278e-03,12.77778,23.88889,23.88889,46.11111,,,temperature,temperature,dimensionless;"
    "curve:biquadratic,varspeedcooleirft,0.632475e+00,-0.121321e-01,0.507773e-03,0.155377e-01,0.272840e-03,-0.679201e-03,12.77778,23.88889,23.88889,46.11111,,,temperature,temperature,dimensionless;"
    "curve:biquadratic,varspeedcoolcaplsft,0.476428e+00,0.401147e-01,0.226411e-03,-0.827136e-03,-0.732240e-05,-0.446278e-03,12.77778,23.88889,23.88889,46.11111,,,temperature,temperature,dimensionless;"
    "curve:biquadratic,varspeedcooleirlsft,0.774645e+00,-0.343731e-01,0.783173e-03,0.146596e-01,0.488851e-03,-0.752036e-03,12.77778,23.88889,23.88889,46.11111,,,temperature,temperature,dimensionless;"
    "curve:bicubic,noncondensingboilereff,1.111720116,0.078614078,-0.400425756,0.0,-0.000156783,0.009384599,0.234257955,1.32927e-06,-0.004446701,-1.22498e-05,0.1,1.0,20.0,80.0;"
    "curve:biquadratic,air cooled centcapft,0.257896,0.0389016,-0.00021708,0.0468684,-0.00094284,-0.00034344,5,10,24,35;"
    "curve:biquadratic,air cooled centeirft,0.933884,-0.058212,0.00450036,0.00243,0.000486,-0.001215,5,10,24,35;"
    "curve:biquadratic,doe-2 centrifugal/5.50cop capft,0.257183345,0.038794102,-0.00021648,0.046738887,-0.000940235,-0.000342491,5.0,10.0,24.0,35.0;"
    "curve:biquadratic,doe-2 centrifugal/5.50cop eirft,0.933678591,-0.058199196,0.00449937,0.002429466,0.000485893,-0.001214733,5.0,10.0,24.0,35.0;"
    "curve:biquadratic,dxclgcoilenergyinputratiofunctemperature,0.342362868,0.034879757,-0.000623606,0.004976467,0.000437885,-0.000727918,12.77778,23.88889,18.0,46.11111,,,temperature,temperature,dimensionless;"
    "curve:biquadratic,dxclgcoiltotalclgcapfunctemperature,0.942589311,0.009543362,0.000683771,-0.011042694,0.00000524901,-0.00000972002,12.77778,23.88889,18.0,46.11111,,,temperature,temperature,dimensionless;"
    "curve:cubic,capfcond,.245507,.023614,.0000278,.000013,7,25,,,temperature;"
    "curve:cubic,capfevap,.690571,.065571,-.00289,0,4,10,,,temperature;"
    "curve:cubic,constfgencorrtemp,1,0,0,0,20,100,,,temperature;"
    "curve:cubic,defaultfaneffratiocurve,0.33856828,1.72644131,-1.49280132,0.42776208,0.5,1.5,0.3,1.0;"
    "curve:cubic,electronicenthalpycurve,0.01342704,-0.00047892,0.000053352,-0.0000018103,16.6,29.13;"
    "curve:cubic,partloadcurveforgasheatingcoil,0.8,0.2,0.0,0.0,0,1;"
    "curve:cubic,steamfcondtemp,.712019,-.00478,.000864,-.000013,7,30,,,temperature,dimensionless;"
    "curve:cubic,steamusefplr,.18892,.968044,1.119202,-.5034,.15,1;"
    "curve:exponent,defaultfanpowerratiocurve,0,1,3,0,1.5,0.01,1.5;"
    "curve:quadratic,air cooled centeirfplr,0.222903,0.313387,0.46371,0,1;"
    "curve:quadratic,doe-2 centrifugal/5.50cop eirfplr,0.222903,0.313387,0.463710,0.0,1.0;"
    "curve:quadratic,dxclgcoilenergyinputratiofuncflowfraction,1.1552,-0.1808,0.0256,0.5,1.5;"
    "curve:quadratic,dxclgcoiltotalclgcapfuncflowfraction,0.8,0.2,0.0,0.5,1.5;"
    "curve:quadratic,dxcoilpartloadfractioncorrelation,0.85,0.15,0.0,0.0,1.0;"
    "table:lookup,coolcapmodfuncofsaflow,coolcapmodfuncofsaflow_independentvariablelist,,,0.8234,1.1256,dimensionless,,,,0.823403,1.0,1.1256;"
    "table:lookup,capmodfuncofwaterflow,capmodfuncofwaterflow_independentvariablelist,,,0.0,1.04,dimensionless,,,,0.0,0.001,0.71,0.85,0.92,0.97,1.0,1.04;"
    "table:lookup,heatcapmodfuncofsaflow,heatcapmodfuncofsaflow_independentvariablelist,,,0.8554,1.0778,dimensionless,,,,0.8554,1.0,1.0778;"
    "table:independentvariablelist,coolcapmodfuncofsaflow_independentvariablelist,coolcapmodfuncofsaflow_independentvariable1;"
    "table:independentvariablelist,capmodfuncofwaterflow_independentvariablelist,capmodfuncofwaterflow_independentvariable1;"
    "table:independentvariablelist,heatcapmodfuncofsaflow_independentvariablelist,heatcapmodfuncofsaflow_independentvariable1;"
    "table:independentvariable,capmodfuncofwaterflow_independentvariable1,cubic,constant,0.0,1.333333,,dimensionless,,,,0.0,0.05,0.33333,0.5,0.666667,0.833333,1.0,1.333333;"
    "table:independentvariable,heatcapmodfuncofsaflow_independentvariable1,cubic,constant,0.714,1.2857,,dimensionless,,,,0.714286,1.0,1.2857;"
    "table:independentvariable,coolcapmodfuncofsaflow_independentvariable1,cubic,constant,0.714,1.2857,,dimensionless,,,,0.714286,1.0,1.2857;"
    "curve:linear,capmodfuncoftempdiff,0,1,0,1.5,0.0,1.5;"
    "curve:cubic,vrftucoolcapft,0.504547273506488,0.0288891279198444,-0.000010819418650677,0.0000101359395177008,0.0,50.0,0.5,1.5,temperature,dimensionless;"
    "curve:quadratic,vrfaccoolcapfff,0.8,0.2,0.0,0.5,1.5,,,,;"
    "curve:cubic,vrftuheatcapft,-0.390708928227928,0.261815023760162,-0.0130431603151873,0.000178131745997821,0.0,50.0,0.5,1.5,temperature,dimensionless;"
    "curve:biquadratic,vrfcoolcapft,0.576882692,0.017447952,0.000583269,-1.76324e-06,-7.474e-09,-1.30413e-07,15,24,-5,23,,,temperature,temperature,dimensionless;"
    "curve:cubic,vrfcoolcapftboundary,25.73473775,-0.03150043,-0.01416595,0,11,30,,,temperature,;"
    "curve:biquadratic,vrfcoolcapfthi,0.6867358,0.0207631,0.0005447,-0.0016218,-4.259e-07,-0.0003392,15,24,16,43,,,temperature,temperature,dimensionless;"
    "curve:biquadratic,vrfcooleirft,0.989010541,-0.02347967,0.000199711,0.005968336,-1.0289e-07,-0.00015686,15,24,-5,23,,,temperature,temperature,dimensionless;"
    "curve:cubic,vrfcooleirftboundary,25.73473775,-0.03150043,-0.01416595,0,15,24,,,temperature,;"
    "curve:biquadratic,vrfcooleirfthi,0.14351470,0.01860035,-0.0003954,0.02485219,0.00016329,-0.0006244,15,24,16,43,,,temperature,temperature,dimensionless;"
    "curve:biquadratic,vrfheatcapft,1.014599599,-0.002506703,-0.000141599,0.026931595,1.83538e-06,-0.000358147,15,27,-20,15,,,temperature,temperature,dimensionless;"
    "curve:cubic,vrfheatcapftboundary,-7.6000882,3.05090016,-0.1162844,0.0,15,27,,,temperature,;"
    "curve:biquadratic,vrfheatcapfthi,1.161134821,0.027478868,-0.00168795,0.001783378,2.03208e-06,-6.8969e-05,15,27,-10,15,,,temperature,temperature,dimensionless;"
    "curve:biquadratic,vrfheateirft,0.87465501,-0.01319754,0.00110307,-0.0133118,0.00089017,-0.00012766,15,27,-20,12,,,temperature,temperature,dimensionless;"
    "curve:cubic,vrfheateirftboundary,-7.6000882,3.05090016,-0.1162844,0.0,15,27,-20,15,temperature,;"
    "curve:biquadratic,vrfheateirfthi,2.504005146,-0.05736767,4.07336e-05,-0.12959669,0.00135839,0.00317047,15,27,-10,15,,,temperature,temperature,dimensionless;"
    "curve:quadratic,vrfcplffplr,0.85,0.15,0.0,0.0,1.0,,,,;"
    "curve:linear,coolingcombratio,0.618055,0.381945,1.0,1.5,,,,;"
    "curve:cubic,coolingeirlowplr,0.4628123,-1.0402406,2.17490997,-0.5974817,0,1,,,temperature,capacity;"
    "curve:quadratic,coolingeirhiplr,1.0,0.0,0.0,1.0,1.5,,,,;"
    "curve:linear,heatingcombratio,0.96034,0.03966,1.0,1.5,,,,;"
    "curve:cubic,heatingeirlowplr,0.1400093,0.6415002,0.1339047,0.0845859,0,1,,,dimensionless,dimensionless;"
    "curve:quadratic,heatingeirhiplr,2.4294355,-2.235887,0.8064516,1.0,1.5,,,,;"
    "curve:biquadratic,vrf piping correction factor for length in heating mode,.989916,.001961,-.000036,0,0,0,7,106.5,1,1,,,distance,dimensionless,dimensionless;"
    "curve:biquadratic,vrf heat recovery cooling capacity modifier,.9,0,0,0,0,0,-100,100,-100,100,,,temperature,temperature,dimensionless;"
    "curve:biquadratic,vrf heat recovery cooling energy modifier,1.1,0,0,0,0,0,-100,100,-100,100,,,temperature,temperature,dimensionless;"
    "curve:biquadratic,vrf heat recovery heating capacity modifier,.9,0,0,0,0,0,-100,100,-100,100,,,temperature,temperature,dimensionless;"
    "curve:biquadratic,vrf heat recovery heating energy modifier,1.1,0,0,0,0,0,-100,100,-100,100,,,temperature,temperature,dimensionless;"
    "curve:biquadratic,hpaccoolcapft,0.942587793,0.009543347,0.000683770,-0.011042676,0.000005249,-0.000009720,12.77778,23.88889,18.0,46.11111,,,temperature,temperature,dimensionless;"
    "curve:biquadratic,hpaceirft,0.342414409,0.034885008,-0.000623700,0.004977216,0.000437951,-0.000728028,12.77778,23.88889,18.0,46.11111,,,temperature,temperature,dimensionless;"
    "curve:cubic,faneffratiocurve,0.33856828,1.72644131,-1.49280132,0.42776208,0.5,1.5,0.3,1.0;"
    "curve:cubic,hpacheatcapfff,0.84,0.16,0.0,0.0,0.5,1.5;"
    "curve:cubic,hpacheatcapft,0.758746,0.027626,0.000148716,0.0000034992,-20.0,20.0,,,temperature,dimensionless;"
    "curve:cubic,hpacheateirft,1.19248,-0.0300438,0.00103745,-0.000023328,-20.0,20.0,,,temperature,dimensionless;"
    "curve:quadratic,hpaccoolplffplr,0.85,0.15,0.0,0.0,1.0;"
    "curve:quadratic,hpaccoolcapfff,0.8,0.2,0.0,0.5,1.5;"
    "curve:quadratic,hpaceirfff,1.1552,-0.1808,0.0256,0.5,1.5;"
    "curve:quadratic,hpacheateirfff,1.3824,-0.4336,0.0512,0.0,1.0;"
    "curve:quadratic,hpacplffplr,0.85,0.15,0.0,0.0,1.0;"
    "curve:quadratic,windaccoolcapfff,0.8,0.2,0.0,0.5,1.5;"
    "curve:quadratic,windaceirfff,1.1552,-0.1808,0.0256,0.5,1.5;"
    "curve:quadratic,windacplffplr,0.85,0.15,0.0,0.0,1.0;"
    "curve:biquadratic,windaccoolcapft,0.942587793,0.009543347,0.000683770,-0.011042676,0.000005249,-0.000009720,12.77778,23.88889,18.0,46.11111,,,temperature,temperature,dimensionless;"
    "curve:biquadratic,windaceirft,0.342414409,0.034885008,-0.000623700,0.004977216,0.000437951,-0.000728028,12.77778,23.88889,18.0,46.11111,,,temperature,temperature,dimensionless;"
    # watertoairheatpump:equationfit
    "curve:quadratic,hpacheatplffplr,0.75,0.25,0.0,0.0,1.0;"
    "curve:quadlinear,heatpowcurve,-2.17352461285805,0.830808361346509,1.5682782658283,0.689709515714146,0.0,-100,100,-100,100,0,100,0,100,0,38;"
    "curve:quadlinear,heatcapcurve,-1.30782327125798,-2.37467612404102,4.00919247797279,0.615580752610271,0.0,-100,100,-100,100,0,100,0,100,0,38;"
    "curve:quadlinear,coolpowcurve,-3.25323327026219,-0.990977022339372,4.03828937789764,0.952179101682919,0.0,-100,100,-100,100,0,100,0,100,0,38;"
    "curve:quintlinear,coolsenscapcurve,-5.26562830117273,17.3118017582604,-11.4496890368762,-0.944804890543481,0.739606605780884,0.0,-100,100,-100,100,-100,100,0,100,0,100,0,38;"
    "curve:quadlinear,totcoolcapcurve,-9.32564313298629,11.088084240584,-1.75195196204063,0.760820340847872,0.0,-100,100,-100,100,0,100,0,100,0,38;"
    # gshp
    "curve:biquadratic,capcurvefunctemp,1.0,0.0,0.0,0.0,0.0,0.0,5.0,10.0,24.0,35.0,,,temperature,temperature,dimensionless;"
    "curve:biquadratic,eircurvefunctemp,1.0,0.0,0.0,0.0,0.0,0.0,5.0,10.0,24.0,35.0,,,temperature,temperature,dimensionless;"
    "curve:quadratic,eircurvefuncplr,1.0,0.0,0.0,0.0,1.0;"
    "curve:biquadratic,capcurvefunctemp2,1.0,0.0,0.0,0.0,0.0,0.0,5.0,10.0,24.0,35.0,,,temperature,temperature,dimensionless;"
    "curve:biquadratic,eircurvefunctemp2,1.0,0.0,0.0,0.0,0.0,0.0,5.0,10.0,24.0,35.0,,,temperature,temperature,dimensionless;"
    "curve:quadratic,eircurvefuncplr2,1.0,0.0,0.0,0.0,1.0;"
    # heatpump:airtowater
    "Curve:Biquadratic,CapCurveFuncTempHT2,0.885,-0.00040,0.00019,0.0202,-0.0096,0.000580,30,50,-7,20,0.5,1.3,Temperature,Temperature,Dimensionless;"
    "Curve:Biquadratic,EIRCurveFuncTempHT2,1.055,0.00035,-0.00027,-0.0108,0.0145,-0.000230,30,50,-7,20,0.7,1.5,Temperature,Temperature,Dimensionless;"
    "Curve:Quadratic,EIRCurveFuncPLR2,1.0,0.0,0.0,0.0,1.0;"
    "Curve:Biquadratic,CapCurveFuncTempHT,0.899,-0.00045,0.00021,0.0185,-0.0108,0.000617,30,50,-7,20,0.5,1.3,Temperature,Temperature,Dimensionless;"
    "Curve:Biquadratic,EIRCurveFuncTempHT,1.055,0.00035,-0.00027,-0.0108,0.0145,-0.000230,30,50,-7,20,0.7,1.5,Temperature,Temperature,Dimensionless;"
    "Curve:Quadratic,EIRCurveFuncPLR,1.0,0.0,0.0,0.0,1.0;"
)


# Combined list of all non-HVAC system related objects to copy when creating new systems
bldobj = (
    _SIMULATION_OBJECTS
    + _SITE_WEATHER_OBJECTS
    + _ZONE_OBJECTS
    + _SCHEDULE_OBJECTS
    + _REMAINING_BUILDING_OBJECTS
)

"""IDF parameter shortcuts and unit conversions.

This module provides the Eidx enum for convenient access to common IDF parameters
with automatic unit conversion from IP (Imperial) to SI units.
"""

from enum import Enum


class Eidx(Enum):
    """Enum-style shortcuts for common IDF fields with unit conversion.

    Each enum member stores:
    - cls: IDF object type name (lowercase, as in IDF file)
    - item: Field number (1-indexed, as shown in IDF file comments)
    - iptosi: Lambda function to convert IP (Imperial) units to SI units

    Methods:
        get(names): Returns index tuple (object, names, fieldno) for Idfpd access
        ip(value): Converts value from IP units to SI units

    Usage Examples:
        >>> from eppd import Idfpd
        >>> from eppd.core import Eidx
        >>> model = read_idf('baseline.idf')
        >>>
        >>> # Example 1: Set fan static pressure for specific fan
        >>> model[Eidx.fanstatic.get('AHU1 Supply Fan')] = Eidx.fanstatic.ip(3.5)
        >>> # Sets fan static to 3.5 inH2O (converted to Pa)
        >>>
        >>> # Example 2: Set all lights to 1.0 W/sqft
        >>> model[Eidx.lpd.get()] = Eidx.lpd.ip(1.0)
        >>> # Sets all lights field 5 to 1.0 W/sqft (converted to W/m2)
        >>>
        >>> # Example 3: Disable economizer for all OA controllers
        >>> model[Eidx.economizer.get()] = 'NoEconomizer'
        >>>
        >>> # Example 4: Get current value
        >>> current_static = model[Eidx.fanstatic.get('AHU1 Supply Fan')]
        >>>
        >>> # Example 5: Set outdoor air per person (cfm/person to m3/s-person)
        >>> model[Eidx.oaperperson.get()] = Eidx.oaperperson.ip(15)  # 15 cfm/person

    Access multiple objects with bracket notation:
        >>> # Get all VAV fan data
        >>> vav_data = model['fan:variablevolume', :, :]
        >>>
        >>> # Set fan static for all VAV fans using Eidx
        >>> model[Eidx.fanstatic.get()] = Eidx.fanstatic.ip(3.5)
    """

    def __init__(self, cls, item, iptosi):
        """Initialize enum member with object type, field number, and converter.

        Args:
            cls: IDF object type name (lowercase)
            item: Field number (1-indexed as in IDF files)
            iptosi: Lambda function to convert IP units to SI units
        """
        self.cls = cls
        self.item = item
        self.iptosi = iptosi

    def get(self, names=slice(None)):
        """Get index tuple for accessing this field in Idfpd.

        Returns a tuple that can be used directly with __getitem__ and __setitem__.
        Supports regex patterns (handled by Idfpd's indexing).

        Args:
            names: Object name(s) to target. Can be:
                   - str: specific name or regex pattern (e.g., 'AHU1', 'supply.*')
                   - list: multiple regex patterns (e.g., ['office.*', 'perim.*'])
                   - slice(None): all objects of this type (default)

        Returns:
            Tuple (object_type, names, fieldno) for use with model[...]

        Example:
            >>> from eppd import Idfpd
            >>> from eppd.core import Eidx
            >>> model = read_idf('baseline.idf')
            >>>
            >>> # Specific object
            >>> model[Eidx.fanstatic.get('AHU1 Supply Fan')] = Eidx.fanstatic.ip(3.5)
            >>>
            >>> # Regex pattern
            >>> model[Eidx.fanstatic.get('supply.*')] = Eidx.fanstatic.ip(3.5)
            >>>
            >>> # Multiple regex patterns
            >>> model[Eidx.lpd.get(['office.*', 'meeting.*'])] = Eidx.lpd.ip(1.0)
            >>>
            >>> # All objects of this type
            >>> model[Eidx.lpd.get()] = Eidx.lpd.ip(1.2)
        """
        return (self.cls, names, self.item)

    def ip(self, value):
        """Convert IP (Imperial) units to SI units.

        Args:
            value: Value in IP units (e.g., inH2O, W/sqft, cfm/person)

        Returns:
            float: Value converted to SI units (e.g., Pa, W/m2, m3/s-person)

        Example:
            >>> # Convert fan static pressure from inH2O to Pa
            >>> si_pressure = Eidx.fanstatic.ip(3.5)  # 3.5 inH2O -> ~872 Pa
            >>>
            >>> # Convert lighting power density from W/sqft to W/m2
            >>> si_lpd = Eidx.lpd.ip(1.2)  # 1.2 W/sqft -> ~12.9 W/m2
            >>>
            >>> # Convert outdoor air from cfm/person to m3/s-person
            >>> si_oa = Eidx.oaperperson.ip(15)  # 15 cfm/person -> ~0.0071 m3/s-person
        """
        return self.iptosi(value)

    # ==================== Building and Run Period ====================
    runperiod = ("runperiod", [1, 2, 4, 5], lambda x: x)
    """Run period: [begin month, begin day, end month, end day]"""

    blddir = ("building", 1, lambda x: x)
    """Building orientation (degrees from north, 0-360)"""

    sizingdb = ("sizingperiod:designday", 4, lambda x: (x - 32) * 5 / 9)
    """ sizing maximum drybulb temperature"""

    sizingrng = ("sizingperiod:designday", 5, lambda x: x * 5 / 9)
    """ sizing drybulb temperature range"""

    sizingwb = ("sizingperiod:designday", 9, lambda x: (x - 32) * 5 / 9)
    """ sizing wetbulb at max dry-bulb temperature"""

    # ==================== Internal Loads ====================
    lpd = ("lights", 5, lambda x: x / 0.09290304)
    """Lighting power density: W/sqft -> W/m2"""

    epd = ("electricequipment", 5, lambda x: x / 0.09290304)
    """Equipment power density: W/sqft -> W/m2"""

    # ==================== HVAC Equipment ====================
    heatrec = ("heatexchanger:airtoair:sensibleandlatent", 1, lambda x: x)
    """Heat recovery availability schedule name"""

    economizer = ("controller:outdoorair", 7, lambda x: x)
    """Economizer control type: NoEconomizer, FixedDryBulb, DifferentialEnthalpy"""

    dcvsch = ("controller:outdoorair", 16, lambda x: x)
    """DCV schedule: use people schedule to enable, fan schedule to disable"""

    maxsupplyT = ("setpointmanager:warmest", 4, lambda x: (x - 32) * 5 / 9)
    """Max supply temperature for setpoint manager type warmest"""

    # ==================== Fan Parameters ====================
    faneff = ("fan:variablevolume", 2, lambda x: x)
    """Fan total efficiency (0-1, dimensionless)"""

    fanstatic = ("fan:variablevolume", 3, lambda x: x / 0.00401463)
    """Fan static pressure: inH2O -> Pa"""

    # ==================== Outdoor Air Parameters ====================
    oamethod = ("designspecification:outdoorair", 1, lambda x: x)
    """OA method: Flow/Person, Flow/Area, Flow/Zone, AirChanges/Hour, Sum, Maximum"""

    oaperperson = ("designspecification:outdoorair", 2, lambda x: x / 2118.88000328931)
    """Outdoor air per person: cfm/person -> m3/s-person"""

    oapersqft = ("designspecification:outdoorair", 3, lambda x: x / 196.85)
    """Outdoor air per floor area: cfm/sqft -> m3/s-m2"""

    # ==================== Construction and Materials ====================
    nomass_rvalue = ("material:nomass", 2, lambda x: x / 5.678263)
    """Wall R-value: ft2-F-hr/Btu -> m2-K/W"""

    conductivity_material = ("material", 3, lambda x: x / 6.93481276005548)
    """material conductivity: W/m-K -> Btu-in/h-ft2-F"""

    insulation_thickness = ("material", 2, lambda x: x / 3.28083989501312 / 12)
    """Insulation Thickness: inch -> m"""

    # ==================== Window Properties ====================
    window_ufactor = ("windowmaterial:simpleglazingsystem", 1, lambda x: x / 5.678263)
    """Window U-factor: Btu/h-ft2-F -> W/m2-K"""

    window_shgc = ("windowmaterial:simpleglazingsystem", 2, lambda x: x)
    """Window SHGC (dimensionless, 0-1)"""

    # ==================== Infiltration ====================

    infil_method = ("zoneinfiltration:designflowrate", 3, lambda x: x)
    """Infiltration Design Flow Rate Calculation Method: Flow/Zone Flow/Area Flow/ExteriorArea Flow/ExteriorWallArea AirChanges/Hour"""

    infil_flowrate = ("zoneinfiltration:designflowrate", 6, lambda x: x / 196.85)
    """Infiltration flow per exterior surface area: cfm/sqft -> m3/s-m2"""

    # ==================== Building Info ====================

    znames = ("zone", 1, lambda x: x)
    """Zone names"""


__all__ = ["Eidx"]

# Unit conversion constants from EnergyPlus IDD file for reference.
#      $/(m3/s)               =>   $/(ft3/min)         0.000472000059660808
#      $/(W/K)                =>   $/(Btu/h-F)         0.52667614683731
#      $/kW                   =>   $/(kBtuh/h)         0.293083235638921
#      $/m2                   =>   $/ft2               0.0928939733269818
#      $/m3                   =>   $/ft3               0.0283127014102352
#      (kg/s)/W               =>   (lbm/sec)/(Btu/hr)  0.646078115385742
#      1/K                    =>   1/F                 0.555555555555556
#      1/m                    =>   1/ft                0.3048
#      A/K                    =>   A/F                 0.555555555555556
#      C                      =>   F                   1.8 (plus 32)
#      cm                     =>   in                  0.3937
#      cm2                    =>   inch2               0.15500031000062
#      deltaC                 =>   deltaF              1.8
#      deltaC/hr              =>   deltaF/hr           1.8
#      deltaJ/kg              =>   deltaBtu/lb         0.0004299
#      g/GJ                   =>   lb/MWh              0.00793664091373665
#      g/kg                   =>   grains/lb           7
#      g/MJ                   =>   lb/MWh              7.93664091373665
#      g/mol                  =>   lb/mol              0.0022046
#      g/m-s                  =>   lb/ft-s             0.000671968949659
#      g/m-s-K                =>   lb/ft-s-F           0.000373574867724868
#      GJ                     =>   ton-hrs             78.9889415481832
#      J                      =>   Wh                  0.000277777777777778
#      J/K                    =>   Btu/F               526.565
#      J/kg                   =>   Btu/lb              0.00042986 (plus 7.686)
#      J/kg-K                 =>   Btu/lb-F            0.000239005736137667
#      J/kg-K2                =>   Btu/lb-F2           0.000132889924714692
#      J/kg-K3                =>   Btu/lb-F3           7.38277359526066E-05
#      J/m2-K                 =>   Btu/ft2-F           4.89224766847393E-05
#      J/m3                   =>   Btu/ft3             2.68096514745308E-05
#      J/m3-K                 =>   Btu/ft3-F           1.49237004739337E-05
#      K                      =>   R                   1.8
#      K/m                    =>   F/ft                0.54861322767449
#      kg                     =>   lb                  2.2046
#      kg/J                   =>   lb/Btu              2325.83774250441
#      kg/kg-K                =>   lb/lb-F             0.555555555555556
#      kg/m                   =>   lb/ft               0.67196893069637
#      kg/m2                  =>   lb/ft2              0.204794053596664
#      kg/m3                  =>   lb/ft3              0.062428
#      kg/m-s                 =>   lb/ft-s             0.67196893069637
#      kg/m-s-K               =>   lb/ft-s-F           0.373316072609094
#      kg/m-s-K2              =>   lb/ft-s-F2          0.207397818116164
#      kg/Pa-s-m2             =>   lb/psi-s-ft2        1412.00523459398
#      kg/s                   =>   lb/s                2.20462247603796
#      kg/s2                  =>   lb/s2               2.2046
#      kg/s-m                 =>   lb/s-ft             0.67196893069637
#      kJ/kg                  =>   Btu/lb              0.429925
#      kPa                    =>   psi                 0.145038
#      L/day                  =>   pint/day            2.11337629827348
#      L/GJ                   =>   gal/kWh             0.000951022349025202
#      L/kWh                  =>   pint/kWh            2.11337629827348
#      L/MJ                   =>   gal/kWh             0.951022349025202
#      lux                    =>   foot-candles        0.092902267
#      m                      =>   ft                  3.28083989501312
#      m/hr                   =>   ft/hr               3.28083989501312
#      m/s                    =>   ft/min              196.850393700787
#      m/s                    =>   miles/hr            2.2369362920544
#      m/yr                   =>   inch/yr             39.3700787401575
#      m2                     =>   ft2                 10.7639104167097
#      m2/m                   =>   ft2/ft              3.28083989501312
#      m2/person              =>   ft2/person          10.764961
#      m2/s                   =>   ft2/s               10.7639104167097
#      m2-K/W                 =>   ft2-F-hr/Btu        5.678263
#      m3                     =>   ft3                 35.3146667214886
#      m3                     =>   gal                 264.172037284185
#      m3/GJ                  =>   ft3/MWh             127.13292
#      m3/hr                  =>   ft3/hr              35.3146667214886
#      m3/hr-m2               =>   ft3/hr-ft2          3.28083989501312
#      m3/hr-person           =>   ft3/hr-person       35.3146667214886
#      m3/kg                  =>   ft3/lb              16.018
#      m3/m2                  =>   ft3/ft2             3.28083989501312
#      m3/MJ                  =>   ft3/kWh             127.13292
#      m3/person              =>   ft3/person          35.3146667214886
#      m3/s                   =>   ft3/min             2118.88000328931
#      m3/s-m                 =>   ft3/min-ft          645.89
#      m3/s-m2                =>   ft3/min-ft2         196.85
#      m3/s-person            =>   ft3/min-person      2118.6438
#      m3/s-W                 =>   (ft3/min)/(Btu/h)   621.099127332943
#      N-m                    =>   lbf-in              8.85074900525547
#      N-s/m2                 =>   lbf-s/ft2           0.0208857913669065
#      Pa                     =>   psi                 0.000145037743897283
#      percent/K              =>   percent/F           0.555555555555556
#      person/m2              =>   person/ft2          0.0928939733269818
#      s/m                    =>   s/ft                0.3048
#      umol/m2-s              =>   umol/ft2-s          0.09290304
#      V/K                    =>   V/F                 0.555555555555556
#      W                      =>   Btu/h               3.4121412858518
#      W/((m3/s)-Pa)          =>   W/((gal/min)-ftH20) 0.188582274697355
#      W/((m3/s)-Pa)          =>   W/((ft3/min)-inH2O) 0.117556910599482
#      W/(m3/s)               =>   W/(ft3/min)         0.0004719475
#      W/K                    =>   Btu/h-F             1.89563404769544
#      W/m                    =>   Btu/h-ft            1.04072
#      W/m2                   =>   Btu/h-ft2           0.316957210776545
#      W/m2                   =>   W/ft2               0.09290304
#      W/m2-K                 =>   Btu/h-ft2-F         0.176110194261872
#      W/m2-K2                =>   Btu/h-ft2-F2        0.097826
#      W/m-K                  =>   Btu-in/h-ft2-F      6.93481276005548
#      W/m-K2                 =>   Btu/h-F2-ft         0.321418310071648
#      W/m-K3                 =>   Btu/h-F3-ft         0.178565727817582
#      W/person               =>   Btu/h-person        3.4121412858518
#
# Other conversions supported (needs the \ip-units code)
#
#      kPa                    =>   inHg                0.29523
#      m                      =>   in                  39.3700787401575
#      m3/hr                  =>   gal/hr              264.172037284185
#      m3/hr-m2               =>   gal/hr-ft2          24.5423853466941
#      m3/hr-person           =>   gal/hr-person       264.172037284185
#      m3/m2                  =>   gal/ft2             24.5423853466941
#      m3/person              =>   gal/person          264.172037284185
#      m3/s                   =>   gal/min             15850.3222370511
#      m3/s-m                 =>   gal/min-ft          4831.17821785317
#      m3/s-W                 =>   (gal/min)/(Btu/h)   4645.27137336702
#      Pa                     =>   ftH2O               0.00033455
#      Pa                     =>   inH2O               0.00401463
#      Pa                     =>   inHg                0.00029613
#      Pa                     =>   Pa                  1
#      W                      =>   W                   1
#      W/(m3/s)               =>   W/(gal/min)         0.0000630902
#      W/m2                   =>   W/m2                1
#      W/m-K                  =>   Btu/h-ft-F          0.577796066000163
#      W/person               =>   W/person            1

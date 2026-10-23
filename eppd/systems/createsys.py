import pandas as pd
from dataclasses import dataclass

from eppd.core.idfpd import Idfpd
from .centralplant import waterloop, sysname
from .airloop import airLoop
from .zonesys import dictbaseboard, dictzoneADU, ZNSYS_HW, ZNSYS_CHW, ZNSYS_HWBB
from .dhw import dhwloop
from .idfstatics import sysstatic, sch_par, bldobj


@dataclass(frozen=True)
class PlantConfig:
    hw: tuple[sysname, ...] = ()
    chw: tuple[sysname, ...] = ()
    whp: tuple[sysname, ...] = ()

    def __post_init__(self):

        # Validate WLHP is not combined with separate loops
        if self.whp and (self.hw or self.chw):
            raise ValueError(
                "WLHP system cannot be combined with separate hot_water or "
                "chilled_water loops. Use either wlhp OR (hot_water/chilled_water)."
            )

        # Validate GSHP equipment is paired correctly
        if ("gshphtg" in self.hw) != ("gshpclg" in self.chw):
            raise ValueError(
                "Ground-source heat pump heating (gshphtg) must be paired with "
                "ground-source heat pump cooling (gshpclg) "
            )
        if (
            self.chw
            and self.chw[0] == "watercooledchiller"
            and (not isinstance(self.chw, tuple))
        ):
            raise ValueError(
                "provide watercooled chiller and condenser source in tuple format"
            )

        # Validate whp


#        if not isinstance(self.whp, tuple):
#            raise TypeError("whp must be a tuple of Equipment")
#        for pair in self.whp:
#            if not isinstance(pair, tuple):
#                raise TypeError("Each whp entry must be a tuple")
#            elif pair[0] not in plantequip:
#                raise TypeError("Specified CHW equipment not available")
#            elif pair[1] is not None and pair[1] not in plantequip:
#                raise TypeError("Specified WHP equipment not available")


def createsys(
    sourceidf: Idfpd,
    sysdf: pd.DataFrame,
    cp: PlantConfig = PlantConfig,
    dhwtype: str = "naturalgas",
) -> Idfpd:
    """Create new HVAC system from configuration.

    Args:
        sourceidf: Source IDF model containing building geometry and loads
        sysdf: System configuration dataframe with columns:
            - index: zone names
            - 'sname': system name
            - 'airloop': air loop type (e.g., 'chw_hw_doas')
            - 'zonesys': zone system type (e.g., 'fcu')
            - 'fan': fan schedule name
        cp: Central plant configuration using PlantConfig dataclass, e.g.:
            PlantConfig(hw=(pltsys.boiler,), chw=(pltsys.aircooledchiller,))
        dhwtype: Domestic hot water system type

    Returns:
        New IDF model with HVAC systems added

    Raises:
        ValueError: If invalid loop types or system configurations provided

    Example:
        >>> sysdf = pd.DataFrame(index=['Zone1', 'Zone2'])
        >>> sysdf['sname'] = 'ahu1'
        >>> sysdf['airloop'] = 'chw_hw_doas'
        >>> sysdf['zonesys'] = 'fcu'
        >>> sysdf['fan'] = 'office_openoff_fan'
        >>> from .centralplant import pltsys
        >>> cp = PlantConfig(hw=(pltsys.boiler,), chw=(pltsys.aircooledchiller,))
        >>> newmodel = createsys(sourceidf, sysdf, cp)
    """
    # Input validation

    required_cols = {"sname", "airloop", "zonesys", "fan"}
    if missing_cols := required_cols - set(sysdf.columns):
        raise ValueError(f"Missing required columns in sysdf: {missing_cols}")

    # Validate airloop coil configurations
    from .airloop import dictcoil, get_coil_types

    for airloop_config in sysdf["airloop"].dropna().unique():
        parts = airloop_config.split("_")
        if len(parts) < 2:
            raise ValueError(
                f"Invalid airloop configuration '{airloop_config}'. "
                f"Expected format: 'coil1_coil2_systemtype' (e.g., 'chw_hw_doas')"
            )
        coils = parts[:-1]  # All but last element are coils
        system_type = parts[-1]  # Last element is system type

        for coil in coils:
            if coil not in dictcoil:
                available = ", ".join(sorted(get_coil_types().keys()))
                raise ValueError(
                    f"Unknown coil type '{coil}' in airloop config '{airloop_config}'. "
                    f"Available coil types: {available}"
                )

    # Validate zone system types
    from .zonesys import get_zone_systems, get_baseboard_types

    for zname, row in sysdf.iterrows():
        zsyslst = row.zonesys.split("_")
        zone_sys_type = zsyslst[0]

        if zone_sys_type not in dictzoneADU:
            available = ", ".join(sorted(get_zone_systems().keys()))
            raise ValueError(
                f"Unknown zone system type '{zone_sys_type}' for zone '{zname}'. "
                f"Available types: {available}"
            )

        # Validate baseboard type if present
        if len(zsyslst) > 1:
            baseboard_type = zsyslst[-1]
            if baseboard_type not in dictbaseboard:
                available = ", ".join(sorted(get_baseboard_types().keys()))
                raise ValueError(
                    f"Unknown baseboard type '{baseboard_type}' for zone '{zname}'. "
                    f"Available types: {available}"
                )

    idfstr = ""
    for ea in sysdf.groupby(["sname", "airloop"]):  # create air loop
        sname = ea[0][0]  # sname
        znames = ea[1].index.values  # zones in systype and sname
        coils = ea[0][1]
        fsch = ea[1]["fan"].iloc[0]
        idfstr += airLoop(sname, znames, coils, fsch)

    for zname, ea in sysdf.iterrows():  # create zone systems
        zsyslst = ea.zonesys.split("_")
        # Check if last element is a baseboard type
        zbb = zsyslst[-1] if zsyslst[-1] in dictbaseboard else None
        idfstr += dictzoneADU[zsyslst[0]][0](zname, zbb)

    # get systems and zones that have water c
    cstr = sysdf.airloop.fillna("").str
    clc = list(sysdf[cstr.contains("chw")].sname.unique())
    htc = list(sysdf[cstr.contains("hw|whp")].sname.unique())

    znhtc  = list(sysdf[sysdf.zonesys.str.contains(ZNSYS_HW)].index)
    znclc  = list(sysdf[sysdf.zonesys.str.contains(ZNSYS_CHW)].index)
    znhwbb = list(sysdf[sysdf.zonesys.str.contains(ZNSYS_HWBB)].index)

    if cp.hw:
        idfstr += waterloop("hw", cp.hw, htc=htc, znhtc=znhtc, znhwbb=znhwbb)

    if cp.chw:
        idfstr += waterloop("chw", cp.chw, clc=clc, znclc=znclc)

    if cp.whp:
        idfstr += waterloop("whp", cp.whp, htc=htc, clc=clc, znhtc=znhtc, znclc=znclc)

    idfstr += sysstatic + sch_par

    # Add DHW loop if water usage equipment is present
    water_use_equipment = list(sourceidf["wateruse:equipment", :, 1].index)
    if water_use_equipment:
        idfstr += dhwloop(water_use_equipment, dhwtype)

    # Get non-system related items present in source IDF
    objs = sourceidf.data.index.get_level_values(0).intersection(bldobj)


    # Create new building model
    newbld = Idfpd(sourceidf[objs])
    newbld.append_from_string(idfstr)
    newbld.drop_duplicates()

    return newbld

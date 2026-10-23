"""Post-processing of EnergyPlus simulation outputs.

This package provides parsers for various EnergyPlus output formats:
- XML summary reports
- ESO hourly output files

Example:
    Simple function-based API:
        >>> from eppd.postprocess import read_xml, read_eso
        >>> parser = read_xml('eplusout.xml')
        >>> hourly_data = read_eso('eplusout.eso')

    Class-based API:
        >>> from eppd.postprocess import Xmlpd, Esopd
        >>> xml_parser = Xmlpd('eplusout.xml')
        >>> eso_reader = Esopd('eplusout.eso')
"""

from .xmlpd import read_xml
from .esopd import read_eso,changepoint_fit

__all__ = [
    'read_xml',
    'read_eso',
    'changepoint_fit'
]

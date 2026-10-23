"""Core IDF file handling functionality.

This package provides the foundational classes for parsing, manipulating,
and writing EnergyPlus IDF (Input Data File) format.
"""

from .idfpd import Idfpd, read_idf
from .eidx import Eidx
from .outputs import Sobj, apnd

__all__ = ['read_idf', 'Eidx', 'Sobj', 'apnd']

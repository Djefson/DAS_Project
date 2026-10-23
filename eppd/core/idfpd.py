"""IDF data model.

This module provides the Idfpd class, which represents an in-memory
EnergyPlus IDF file as a pandas multi-index Series for easy manipulation.
"""

from pathlib import Path

import pandas as pd
import numpy as np

from ..logger import get_logger
from .parser import parse_idf_string

logger = get_logger(__name__)


class Idfpd:
    """Pandas-based representation of EnergyPlus IDF file.

    Stores IDF data as a pandas multi-index Series with levels:
        (object, name, fieldno) -> value

    Provides methods for querying and manipulating IDF objects.

    Example:
        >>> from eppd import Idfpd
        >>> idf = read_idf('baseline.idf')
        >>> zones = list(idf['zone', :, 1].index.get_level_values('name').unique())
        >>> idf['lights', :, 5] = 10.76  # Set all lights LPD
    """

    def __init__(self, data: pd.Series, source_file: Path | None = None):
        """Initialize IDF model with data.

        Args:
            data: Multi-index Series with IDF data (object, name, fieldno)
            source_file: Optional path to source file (for reference)
        """
        self.data = data
        self.source_file = source_file
        logger.debug(f"Initialized Idfpd with {len(data)} fields")

    def __getitem__(self, key: str | tuple) -> pd.Series | str | float:
        """Get IDF field value(s).

        Attempts to convert to numeric if possible. Supports regex pattern tuples
        for matching multiple object names.

        Args:
            key: Index key - can be:
                - str: object type only
                - [str,str]: multiple object types
                - (object, name): 2-tuple
                - (object, name, fieldno): 3-tuple
                - name can be a tuple of regex patterns: ('office.*', 'perim.*')
                - name can be a list for direct indexing: ['name1', 'name2']

        Returns:
            Series, string, or numeric value

        Example:
            >>> model['zone', 'Core', 1]  # Get first field of Core zone
            >>> model['lights', :, 5]  # Get field 5 of all lights
            >>> model['zone', ('office.*', 'perim.*'), 5]  # Regex tuple matching
            >>> model['zone', ['Core', 'North'], 5]  # Direct list indexing
        """
        # Handle tuple of regex patterns in name position
        if isinstance(key, tuple) and len(key) >= 2 and isinstance(key[1], tuple):
            object_type = key[0]
            patterns = key[1]
            fieldno = key[2] if len(key) == 3 else slice(None)

            # Get all names for this object type and match against regex patterns
            all_names = self.data[object_type, :, 1].index.get_level_values("name")
            matched_names = []
            for pattern in patterns:
                matched_names.extend(list(all_names[all_names.str.contains(pattern)]))
            if len(matched_names) > 0:
                key = (object_type, matched_names, fieldno)
            else:
                key = None
        # Standard pandas loc indexing (handles lists and strings directly)
        try:
            all_objects = self.data.loc[key]
        except KeyError:
            return pd.Series(dtype=object)
        try:
            # Try to convert to numeric
            return pd.to_numeric(all_objects)
        except (ValueError, TypeError):
            # Not numeric (schedule name, object reference, etc.)
            return all_objects

    def __setitem__(self, key: str | tuple, value) -> None:
        """Set IDF field value(s).

        Supports regex pattern tuples for matching multiple object names.

        Args:
            key: Index key - can be:
                - str: object type only
                - (object, name): 2-tuple
                - (object, name, fieldno): 3-tuple
                - name can be a tuple of regex patterns: ('office.*', 'perim.*')
                - name can be a list for direct indexing: ['name1', 'name2']
            value: New value(s) to assign

        Example:
            >>> model['lights', :, 5] = 10.76  # Set LPD for all lights
            >>> model['zone', 'Core', 1] = 'New Name'
            >>> model['zone', ('office.*', 'perim.*'), 5] = 100  # Regex tuple
            >>> model['zone', ['Core', 'North'], 5] = 100  # Direct list indexing
        """
        # Handle tuple of regex patterns in name position
        if isinstance(key, tuple) and len(key) >= 2 and isinstance(key[1], tuple):
            object_type = key[0]
            patterns = key[1]
            fieldno = key[2] if len(key) == 3 else slice(None)

            # Get all names for this object type and match against regex patterns
            all_names = self.data[object_type, :, 1].index.get_level_values("name")
            matched_names = []
            for pattern in patterns:
                matched_names.extend(list(all_names[all_names.str.contains(pattern)]))
            if len(matched_names) > 0:
                key = (object_type, matched_names, fieldno)

        try:
            # Standard pandas loc indexing (handles lists and strings directly)
            self.data.loc[key] = value
        except KeyError:
            pass

    def drop_objects(self, target: str | tuple | list[str | tuple]) -> None:
        """Remove objects by type or specific instances.

        Args:
            target: What to drop:
                - str: Drop all instances of this object type
                - tuple: Drop specific instance (object_type, name)
                - list of str: Drop multiple object types
                - list of tuple: Drop multiple specific instances

        Example:
            >>> # Drop all instances of an object type
            >>> model.drop_objects('output:variable')
            >>> model.drop_objects(['output:meter', 'output:table:monthly'])
            >>>
            >>> # Drop specific instances
            >>> model.drop_objects(('zone', 'unused'))
            >>> model.drop_objects([('lights', 'zone1'), ('lights', 'zone2')])
        """
        # Handle string or list of strings (object types)
        if isinstance(target, str):
            target = [target]

        if isinstance(target, list) and len(target) > 0 and isinstance(target[0], str):
            # Dropping object types
            existing_types = [
                obj_type
                for obj_type in target
                if obj_type in self.data.index.get_level_values("object")
            ]

            if not existing_types:
                logger.warning(f"None of the specified object types found: {target}")
                return

            to_drop = self.data.index.get_level_values("object").isin(existing_types)
            self.data = self.data[~to_drop]
            logger.debug(f"Dropped {len(existing_types)} object types")

        else:
            # Dropping specific instances (tuple or list of tuples)
            try:
                self.data = self.data.drop(target)
                logger.debug(f"Dropped objects: {target}")
            except KeyError as e:
                logger.warning(f"Could not drop objects {target}: {e}")

    def drop_duplicates(self, keep: str = "first") -> None:
        """Remove duplicate index entries.

        Args:
            keep: Which duplicate to keep ('first', 'last', False to drop all)

        Example:
            >>> model.drop_duplicates()
        """
        n_before = len(self.data)
        self.data = self.data[~self.data.index.duplicated(keep=keep)]
        n_dropped = n_before - len(self.data)

        if n_dropped > 0:
            logger.debug(f"Dropped {n_dropped} duplicate entries")

    def append_from_string(self, idf_string: str) -> None:
        """Parse an IDF string and append its objects to this model.

        Args:
            idf_string: Raw IDF content to parse and append

        Example:
            >>> extra = "Zone,Attic,0,0,0,1,1,1;"
            >>> model.append_from_string(extra)
        """
        data_to_append = parse_idf_string(idf_string)
        incoming_pairs = data_to_append.index.droplevel("fieldno").unique()
        existing_pairs = self.data.index.droplevel("fieldno")
        self.data = self.data[~existing_pairs.isin(incoming_pairs)]
        self.data = pd.concat([self.data, data_to_append])
        self.data = self.data.sort_index(level=0)
        logger.debug(f"Appended {len(data_to_append)} fields from string")

    def copy(self) -> "Idfpd":
        """Create a deep copy of this model.

        Returns:
            New Idfpd with copied data

        Example:
            >>> modified = model.copy()
            >>> modified['lights', :, 5] = 15.0
        """
        return Idfpd(self.data.copy(), source_file=self.source_file)

    def write_idf(self, filepath: str | Path, append_string: str = "") -> None:
        """Write model to IDF file.

        Args:
            filepath: Output file path
            append_string: Optional string to append at end of file

        Example:
            >>> model = read_idf('baseline.idf')
            >>> model['lights', :, 5] = 10.76
            >>> model.write_idf('modified.idf')
            >>>
            >>> # Append custom output requests
            >>> custom = "Output:Variable,*,Zone Mean Air Temperature,Hourly;"
            >>> model.write_idf('output.idf', append_string=custom)
        """
        from .writer import to_string

        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        logger.debug(f"Writing IDF to: {filepath}")

        # Convert model to IDF string
        idf_string = to_string(self)

        # Add optional append string
        if append_string:
            idf_string += "\n" + append_string

        # Write to file
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(idf_string)

            logger.debug(f"Successfully wrote IDF file: {filepath}")

        except Exception as e:
            logger.error(f"Failed to write IDF file {filepath}: {e}")
            raise

    def __len__(self) -> int:
        """Get number of fields in model."""
        return len(self.data)

    def __repr__(self) -> str:
        """String representation of model."""
        n_objects = len(self.get_objects())
        source = f" from {self.source_file.name}" if self.source_file else ""
        return f"Idfpd({len(self)} fields, {n_objects} object types{source})"

    def set_schedule(self, libsch: "Idfpd", sch: str) -> None:
        """Apply schedule set from library to model objects.

        Sets occupancy, lighting, equipment, thermostat, and fan schedules
        from a schedule library file. Schedule names should be lowercase.

        Args:
            libsch: Schedule library Idfpd (e.g., from 'sch.idf')
            sch: Schedule set name matching library template (e.g., 'office', 'school')

        Example:
            >>> model = read_idf('building.idf')
            >>> lib = read_idf('sch.idf')
            >>> model.set_schedule(lib, 'office')
        """
        if f"occ_{sch}" not in libsch.data.index.get_level_values("name"):
            logger.error(f"{sch} schedules not found in provided library idf file")
            return

        if "zonecontrol:thermostat" in self.data.index:
            self.data.loc["zonecontrol:thermostat", :, 4] = f"dual_{sch}"
        if "people" in self.data.index:
            self.data.loc["people", :, 2] = f"occ_{sch}"
        if "lights" in self.data.index:
            self.data.loc["lights", :, 2] = f"lt_{sch}"
        if "electricequipment" in self.data.index:
            self.data.loc["electricequipment", :, 2] = f"eq_{sch}"

        if "controller:outdoorair" in self.data.index:
            self.data.loc["controller:outdoorair", :, 16] = f"fan_{sch}"
        if "availabilitymanager:nightcycle" in self.data.index:
            self.data.loc["availabilitymanager:nightcycle", :, 2] = f"fan_{sch}"
        if "fan" in self.data.index:
            self.data.loc["fan", :, 1] = f"fan_{sch}"

        incoming_pairs = libsch.data.index.droplevel("fieldno").unique()
        existing_pairs = self.data.index.droplevel("fieldno")
        self.data = self.data[~existing_pairs.isin(incoming_pairs)]
        self.data = pd.concat([self.data, libsch.data])
        self.data = self.data.sort_index(level=0)

    def get_objects(self) -> list[str]:
        """Get list of all IDF object types in model.

        Returns
            Sorted list of unique object type names

        Example:
            >>> objects = model.get_objects()
            >>> print(objects)
            ['building', 'buildingsurface:detailed', 'lights', 'zone', ...]
        """
        return sorted(set(self.data.index.get_level_values("object")))


def read_idf(filepath: str | Path) -> Idfpd:
    """Read and parse an IDF file.

    Args:
        filepath: Path to IDF file

    Returns:
        Idfpd instance

    Example:
        >>> model = read_idf('baseline.idf')
        >>> print(model)

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file cannot be read or parsed
    """
    filepath = Path(filepath)

    if not filepath.exists():
        raise SystemExit(f"IDF file not found: {filepath}")

    logger.debug(f"Reading IDF file: {filepath.name}")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        raise ValueError(f"Failed to read IDF file {filepath}: {e}") from e

    data = parse_idf_string(content)
    return Idfpd(data, source_file=filepath)

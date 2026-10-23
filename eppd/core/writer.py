"""IDF file writer.

This module provides functionality to serialize Idfpd back to
EnergyPlus IDF file format.

Note: The preferred way to write IDF files is using the model's write_idf() method:
    >>> model = read_idf('baseline.idf')
    >>> model.write_idf('output.idf')

This module is used internally and is also available for advanced use cases.
"""

import io
import re

from ..logger import get_logger

logger = get_logger(__name__)


# Pre-compiled regex for replacing line endings
TERMINATOR_PATTERN = re.compile(r'[,\s]*\n')


def to_string(model: 'Idfpd') -> str:
    """Convert IDF model to string format.

    Args:
        model: Idfpd to serialize

    Returns:
        IDF format string

    Example:
        >>> from eppd.core.writer import to_string
        >>> idf_content = to_string(model)
    """
    # Make a copy and remove duplicates
    data = model.data.copy()
    data = data[~data.index.duplicated()]

    logger.debug(f"Serializing {len(data)} parameters")

    # Unstack to wide format (each row is one object)
    # This gives us: (class, name) rows with parameter columns
    try:
        wide = data.unstack()
    except Exception as e:
        logger.error(f"Failed to unstack data: {e}")
        raise

    # Convert to CSV format in memory
    output = io.StringIO()
    wide.to_csv(output, header=False, lineterminator='\n')
    output.seek(0)

    csv_content = output.read()

    # Replace "comma whitespace newline" with "semicolon newline"
    # This converts CSV format to IDF format
    idf_content = TERMINATOR_PATTERN.sub(';\n', csv_content)

    return idf_content

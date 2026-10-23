"""IDF file parser.

into a pandas multi-index Series data structure for manipulation.
"""

import re

import pandas as pd
from ..logger import get_logger

logger = get_logger(__name__)


# Pre-compiled regex patterns for performance
COMMENT_PATTERN = re.compile(r'!.*|\t')
WHITESPACE_PATTERN = re.compile(r'( *)(,|;)( *)')


def parse_idf_string(idf_string: str) -> pd.Series:
    """Parse IDF content string into pandas Series.

    Converts IDF format (semicolon-delimited object definitions) into
    a pandas multi-index Series for programmatic manipulation.

    All object types and names are converted to lowercase for consistent handling.

    The resulting structure has a three-level multi-index:
        Level 0 (object): IDF object type (e.g., 'zone', 'lights')
        Level 1 (name): Object instance name
        Level 2 (fieldno): Field index number (1-based)

    Args:
        idf_string: Raw IDF file content

    Returns:
        Multi-index Series with IDF data

    Raises:
        ValueError: If parsing fails

    Example:
        >>> idf_content = "Zone,Core Zone,0,0,0,1,1,1;"
        >>> data = parse_idf_string(idf_content)
        >>> print(data.loc['zone', 'Core Zone', 1])  # Get first parameter
    """
    try:
        # Remove comments (! to end of line) and tabs
        cleaned = COMMENT_PATTERN.sub('', idf_string)

        # Remove newlines (IDF is semicolon-delimited, not newline-delimited)
        cleaned = cleaned.replace('\n', '')

        # Normalize whitespace around delimiters: " , " -> ","
        cleaned = WHITESPACE_PATTERN.sub(r'\2', cleaned)

        # Convert to lowercase for consistent handling
        cleaned = cleaned.lower()

        # Strip leading/trailing whitespace
        cleaned = cleaned.strip()

        logger.debug(f"Cleaned IDF string: {len(cleaned)} characters")

        # Parse into table structure
        return _parse_to_table(cleaned)

    except Exception as e:
        raise ValueError(f"Failed to parse IDF content: {e}") from e


def _parse_to_table(idf_string: str) -> pd.Series:
    """Convert cleaned IDF string to multi-index Series.

    Args:
        idf_string: Cleaned IDF content (no comments, normalized whitespace)

    Returns:
        Multi-index Series with (object, name, fieldno) index
    """
    # Split on semicolons to get list of objects
    # Last item is empty string after final semicolon, so [:-1]
    objects = idf_string.split(';')[:-1]

    if not objects:
        logger.warning("No IDF objects found in file")
        return pd.Series(dtype=object)

    logger.debug(f"Found {len(objects)} IDF objects")

    # Create DataFrame with one object per row
    df = pd.DataFrame(objects, columns=['col'])

    # Split each object on commas to get fields
    # First field is object type, second is name, rest are fields
    params_df = df['col'].str.split(',', expand=True)

    # Use first two columns (object, name) as multi-index
    params_df = params_df.set_index([0, 1])

    # Renumber columns to start from 1 (field index in IDF convention)
    params_df.columns = params_df.columns - 1

    # Replace NaN in name column (index level 1) with empty string
    # Some IDF objects don't have names
    params_df[1] = params_df[1].fillna('')

    # Stack all fields into long format
    # This creates (object, name, field_number) -> value mapping
    stacked = params_df.stack().astype(object)

#    # Remove nan values
    stacked = stacked.dropna()

    # Sort by object for faster lookup
    stacked = stacked.sort_index(level=0)  


    # Set proper index names
    stacked.name = 'val'
    stacked.index = stacked.index.set_names(['object', 'name', 'fieldno'])

    logger.debug(
        f"Parsed {len(stacked.index.get_level_values(0).unique())} "
        f"unique object types"
    )

    return stacked

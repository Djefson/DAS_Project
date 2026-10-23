"""Configuration management for EPPD.

EPPD reads the EnergyPlus executable path from an ``eppd.toml`` file located
in the current working directory or in any of its parent directories (up to
4 levels up). The file is loaded lazily on first use, so ``import eppd``
succeeds even without a config file present.
"""

import tomllib
from pathlib import Path

_CONFIG_FILENAME = "eppd.toml"
_MAX_PARENT_LEVELS = 4
_TEMPLATE_URL = "https://github.com/eppdmodeler/eppd/blob/main/eppd/eppd.toml"


def _find_eppd_toml() -> Path | None:
    """Search cwd and up to _MAX_PARENT_LEVELS parent directories for eppd.toml."""
    cwd = Path.cwd()
    for directory in [cwd, *cwd.parents][: _MAX_PARENT_LEVELS + 1]:
        candidate = directory / _CONFIG_FILENAME
        if candidate.exists():
            return candidate
    return None


class EnergyPlusConfig:
    """EnergyPlus installation configuration.

    Reads ``eppd.toml`` from the current directory or up to 4 parent
    directories. To create an ``eppd.toml`` file, copy the template from:
    https://github.com/eppdmodeler/eppd/blob/main/eppd/eppd.toml

    The value of ``energyplus_location`` is the full path to the EnergyPlus
    executable (e.g. ``/usr/local/EnergyPlus-25-2-0/energyplus`` on Linux/macOS,
    ``C:/EnergyPlusV25-2-0/energyplus.exe`` on Windows). ``weatherfiles_folder``
    is optional.

    To override at runtime without a config file, assign directly:

        >>> from pathlib import Path
        >>> from eppd.config import energyplus_config
        >>> energyplus_config.energyplus_location = Path('/path/to/EnergyPlus-25-2-0/energyplus')
        >>> # Windows:
        >>> energyplus_config.energyplus_location = Path('C:/EnergyPlusV25-2-0/energyplus.exe')
        >>> # Can also use Path methods like expanduser():
        >>> energyplus_config.energyplus_location = Path('~/EnergyPlus-25-2-0/energyplus').expanduser()
    """

    def __init__(self):
        self._energyplus_location: Path | None = None
        self._weatherfiles_folder: Path | None = None
        self._loaded_from_file = False
        self._user_override = False

    def _maybe_load_from_file(self) -> None:
        if self._loaded_from_file or self._user_override:
            return

        config_path = _find_eppd_toml()
        if config_path is None:
            cwd = Path.cwd()
            raise FileNotFoundError(
                f"eppd.toml not found in {cwd} or up to {_MAX_PARENT_LEVELS} parent directories.\n\n"
                f"Create an eppd.toml file in your project directory by copying the template:\n"
                f"  {_TEMPLATE_URL}\n\n"
                f"Then edit it to set 'energyplus_location' to the full path of your "
                f"EnergyPlus executable."
            )

        try:
            with open(config_path, "rb") as f:
                toml_config = tomllib.load(f)
        except Exception as e:
            raise ValueError(f"Failed to parse {config_path}: {e}") from e

        if "energyplus" not in toml_config:
            raise ValueError(f"Missing [energyplus] section in {config_path}")

        ep_config = toml_config["energyplus"]
        energyplus_location = ep_config.get("energyplus_location")
        if not energyplus_location:
            raise ValueError(
                f"Missing 'energyplus_location' in [energyplus] section of {config_path}"
            )

        self._energyplus_location = Path(energyplus_location)
        weatherfiles_folder = ep_config.get("weatherfiles_folder")
        self._weatherfiles_folder = (
            Path(weatherfiles_folder) if weatherfiles_folder else None
        )
        self._loaded_from_file = True

    @property
    def energyplus_location(self) -> Path | None:
        self._maybe_load_from_file()
        return self._energyplus_location

    @energyplus_location.setter
    def energyplus_location(self, value):
        if isinstance(value, str):
            value = Path(value) if value else None
        self._energyplus_location = value
        self._user_override = True

    @property
    def weatherfiles_folder(self) -> Path | None:
        self._maybe_load_from_file()
        return self._weatherfiles_folder

    @weatherfiles_folder.setter
    def weatherfiles_folder(self, value):
        if isinstance(value, str):
            value = Path(value) if value else None
        self._weatherfiles_folder = value
        self._user_override = True


energyplus_config = EnergyPlusConfig()

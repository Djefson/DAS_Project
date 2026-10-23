"""Single simulation runner (low-level execution engine).

This module provides low-level functions for EnergyPlus execution.
For high-level simulation coordination, use batch or parametric modules.
"""

import shutil
import subprocess
from pathlib import Path

from ..config import energyplus_config
from ..logger import get_logger

logger = get_logger(__name__)


def _validate_energyplus_location() -> None:
    """Validate that energyplus_location points to a real EnergyPlus executable.

    Raises FileNotFoundError with a clear message if the path is missing,
    doesn't exist, or doesn't have Energy+.idd alongside it.
    """
    exe = energyplus_config.energyplus_location
    if exe is None:
        raise FileNotFoundError(
            "energyplus_config.energyplus_location is not set. "
            "Set it to the full path of the EnergyPlus executable "
            "( '/usr/local/EnergyPlus-26-1-0/energyplus' or "
            "'C:/EnergyPlusV25-2-0/energyplus.exe')."
        )
    if not exe.exists():
        raise FileNotFoundError(
            f"EnergyPlus executable not found: {exe}\n"
            f"Set energyplus_config.energyplus_location to the full path of the "
            f"EnergyPlus executable (include 'energyplus' or 'energyplus.exe')."
        )
    if not (exe.parent / "Energy+.idd").exists():
        raise FileNotFoundError(
            f"Energy+.idd not found next to {exe} — is this the EnergyPlus executable? "
            f"energyplus_location must point to the EnergyPlus binary itself, "
            f"not a wrapper or the install directory."
        )


def _setup_simulation_dir(
    output_dir: Path,
    idf_file: Path,
    weather_file: Path
) -> None:
    """Setup simulation directory with required files.

    Args:
        output_dir: Simulation output directory
        idf_file: Source IDF file
        weather_file: Weather file
    """
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Copy required files
    shutil.copyfile(
        energyplus_config.energyplus_location.parent / 'Energy+.idd',
        output_dir / 'Energy+.idd'
    )

    shutil.copyfile(idf_file, output_dir / 'in.idf')
    shutil.copyfile(weather_file, output_dir / 'in.epw')

    logger.debug(f"Setup simulation directory: {output_dir}")


def _run_energyplus(output_dir: Path, timeout: int) -> bool:
    """Execute EnergyPlus.

    Args:
        output_dir: Simulation directory
        timeout: Maximum run time

    Returns:
        True if simulation succeeded, False otherwise
    """
    result = subprocess.run(
        str(energyplus_config.energyplus_location),
        cwd=str(output_dir),
        capture_output=True,
        timeout=timeout,
        text=True
    )

    return result.returncode == 0


def _collect_outputs(output_dir: Path) -> None:
    """Collect simulation output files.

    Copies important outputs from simulation directory to parent directory
    with friendly names for easy access.

    Args:
        output_dir: Simulation directory
    """
    # Copy important outputs to easily accessible names
    output_mapping = {
        'eplustbl.htm': f'{output_dir.name}.html',
        'eplustbl.xml': f'{output_dir.name}.xml',
        'eplusout.eso': f'{output_dir.name}.eso',
        'eplusout.err': f'{output_dir.name}.err',
    }

    for source, dest in output_mapping.items():
        source_path = output_dir / source
        if source_path.exists():
            dest_path = output_dir.parent / dest
            shutil.copyfile(source_path, dest_path)

    logger.debug(f"Collected outputs from: {output_dir}")


def _cleanup(output_dir: Path) -> None:
    """Remove temporary simulation directory.

    Args:
        output_dir: Directory to remove
    """
    try:
        shutil.rmtree(output_dir)
        logger.debug(f"Removed temp directory: {output_dir}")
    except Exception as e:
        logger.warning(f"Failed to remove temp directory {output_dir}: {e}")

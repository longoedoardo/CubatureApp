from pathlib import Path
import sys


def resource_path(*parts: str) -> Path:
    """Return the path to a bundled application resource."""
    if getattr(sys, "frozen", False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parents[2]

    return base_path.joinpath(*parts)
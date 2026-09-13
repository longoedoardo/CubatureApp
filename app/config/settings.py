"""
Configurazione persistente dell'applicazione.

Salva/legge un piccolo file JSON in una cartella di configurazione utente,
contenente principalmente il percorso della directory dei sorgenti Fortran.
Questo e' l'unico posto in cui la GUI "sa" dove trovare il Fortran: il resto
del codice riceve semplicemente un Path gia' risolto.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

APP_NAME = "OptimalPolyCuba3D"

# Cartella di configurazione utente (indipendente dalla cartella del progetto,
# cosi' funziona anche se l'app viene spostata/eseguita da un altro percorso).
CONFIG_DIR = Path.home() / f".{APP_NAME}"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Percorso di default proposto al primo avvio: fortran/src dentro il progetto.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FORTRAN_SRC_DIR = PROJECT_ROOT / "fortran" / "src"
DEFAULT_BUILD_DIR = CONFIG_DIR / "build"


@dataclass
class Settings:
    fortran_source_dir: str = str(DEFAULT_FORTRAN_SRC_DIR)
    build_dir: str = str(DEFAULT_BUILD_DIR)
    last_vertex_file: str = ""
    last_face_file: str = ""
    last_integrand: str = "x^2 + y^2 + z^2"
    last_degree: int = 4

    def fortran_source_path(self) -> Path:
        return Path(self.fortran_source_dir)

    def build_path(self) -> Path:
        return Path(self.build_dir)

    def is_fortran_source_configured(self) -> bool:
        p = self.fortran_source_path()
        required = ["TypesDef.f90", "OptimalPolyCuba3D.f90", "PolyhedronMesh.f90"]
        return p.is_dir() and all((p / f).is_file() for f in required)


def load_settings() -> Settings:
    if CONFIG_FILE.is_file():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            return Settings(**{**asdict(Settings()), **data})
        except (json.JSONDecodeError, TypeError):
            pass
    return Settings()


def save_settings(settings: Settings) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(asdict(settings), indent=2), encoding="utf-8")

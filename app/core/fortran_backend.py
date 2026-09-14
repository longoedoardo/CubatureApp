"""
FortranBackend: unico punto del progetto che sa come parlare col Fortran.

Strategia per la v1 (vedi punto 17 della specifica): eseguibile compilato
on-demand + scambio dati tramite file temporanei di testo. L'interfaccia
pubblica (ensure_ready / run) e' pero' pensata per restare identica se in
futuro si passasse a una shared library (es. tramite f2py o iso_c_binding +
ctypes): CubatureEngine non dipende da COME il backend calcola il risultato,
solo dal fatto che riceve (nodes, weights).

Il driver Fortran (driverCLI.f90) e' l'unico file che questo progetto
aggiunge al codice Fortran esistente: legge una mesh .dat con MeshReader,
chiama OptimalPolyCuba3D senza modificarne la logica, e scrive nodi/pesi
su due file di testo.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np

REQUIRED_MODULE_SOURCES = [
    "TypesDef.f90",
    "PrepCheap.f90",
    "PolyhedronMesh.f90",
    "triangleQuadratureGJ.f90",
    "CubaCheap.f90",
    "OptimalPolyCuba3D.f90",
]
DRIVER_SOURCE = "driverCLI.f90"
DRIVER_EXE_NAME = "driverCLI"

# Cartelle dove homebrew/gli installer manuali mettono gfortran su macOS,
# quando l'app viene aperta dal Finder e quindi non eredita il PATH della
# shell dell'utente (shutil.which da solo non basterebbe).
_EXTRA_COMPILER_DIRS = ("/opt/homebrew/bin", "/usr/local/bin")


def find_compiler(name: str) -> str | None:
    """Cerca un compilatore nel PATH e, in fallback, nelle cartelle note.

    Usata sia dal backend (per compilare) sia dalla GUI (per mostrare un
    messaggio chiaro prima ancora di avviare il calcolo), cosi' la logica
    di ricerca vive in un solo posto.
    """
    found = shutil.which(name)
    if found:
        return found
    for directory in _EXTRA_COMPILER_DIRS:
        candidate = Path(directory) / name
        if candidate.is_file():
            return str(candidate)
    return None


class FortranSourceError(Exception):
    """La directory dei sorgenti Fortran non e' configurata correttamente."""


class FortranCompilationError(Exception):
    """Compilazione del backend Fortran fallita."""

    def __init__(self, message: str, stderr: str = ""):
        super().__init__(message)
        self.stderr = stderr


class FortranRuntimeError(Exception):
    """Il driver Fortran e' terminato con un errore, o l'output non e' valido."""

    def __init__(self, message: str, stdout: str = "", stderr: str = ""):
        super().__init__(message)
        self.stdout = stdout
        self.stderr = stderr


@dataclass
class FortranBackend:
    source_dir: Path
    build_dir: Path
    compiler: str = "gfortran"

    # ------------------------------------------------------------------
    # Compilazione
    # ------------------------------------------------------------------
    def _driver_source_path(self) -> Path:
        # Il driver puo' vivere nella cartella sorgenti dell'utente oppure,
        # se non presente li', in quella del progetto (fortran/src): questo
        # permette all'utente di puntare la GUI direttamente alla propria
        # cartella Fortran3D/src senza doverci copiare dentro driverCLI.f90.
        candidate = self.source_dir / DRIVER_SOURCE
        if candidate.is_file():
            return candidate
        fallback = Path(__file__).resolve().parents[2] / "fortran" / "src" / DRIVER_SOURCE
        if fallback.is_file():
            return fallback
        raise FortranSourceError(
            f"Non trovo '{DRIVER_SOURCE}' ne' in {self.source_dir} ne' nella cartella "
            "predefinita del progetto (fortran/src). E' il file che collega Python "
            "al numerical core: va aggiunto una sola volta."
        )

    def check_sources(self) -> None:
        missing = [f for f in REQUIRED_MODULE_SOURCES if not (self.source_dir / f).is_file()]
        if missing:
            raise FortranSourceError(
                "Mancano i seguenti file nella directory dei sorgenti Fortran:\n"
                + "\n".join(f"  - {f}" for f in missing)
                + f"\n\nDirectory configurata: {self.source_dir}"
            )

    def _executable_path(self) -> Path:
        return self.build_dir / DRIVER_EXE_NAME

    def _bundled_executable_path(self) -> Path | None:
        bundle_root = getattr(sys, "_MEIPASS", None)
        if not bundle_root:
            return None
        executable_name = DRIVER_EXE_NAME + (".exe" if sys.platform == "win32" else "")
        candidate = Path(bundle_root) / "app" / "assets" / executable_name
        return candidate if candidate.is_file() else None

    def _needs_rebuild(self) -> bool:
        exe = self._executable_path()
        if not exe.is_file():
            return True
        exe_mtime = exe.stat().st_mtime
        sources = [self.source_dir / f for f in REQUIRED_MODULE_SOURCES]
        sources.append(self._driver_source_path())
        return any(src.stat().st_mtime > exe_mtime for src in sources)

    def ensure_ready(self, force: bool = False) -> Path:
        """Garantisce che l'eseguibile del driver esista e sia aggiornato.

        Ritorna il path all'eseguibile. Solleva FortranSourceError /
        FortranCompilationError in caso di problemi.
        """
        bundled_executable = self._bundled_executable_path()
        if not force and bundled_executable is not None:
            return bundled_executable

        self.check_sources()

        compiler_path = find_compiler(self.compiler)
        if compiler_path is None:
            raise FortranCompilationError(
                f"Compilatore Fortran '{self.compiler}' non trovato nel PATH. "
                "Su macOS installalo con 'brew install gcc' e riapri l'app."
            )

        if not force and not self._needs_rebuild():
            return self._executable_path()

        self.build_dir.mkdir(parents=True, exist_ok=True)
        mod_dir = self.build_dir / "mod"
        mod_dir.mkdir(parents=True, exist_ok=True)

        sources = [str(self.source_dir / f) for f in REQUIRED_MODULE_SOURCES]
        sources.append(str(self._driver_source_path()))

        exe_path = self._executable_path()
        cmd = [
            compiler_path,
            "-O2",
            "-ffree-line-length-none",
            "-J",
            str(mod_dir),
            *sources,
            "-o",
            str(exe_path),
        ]

        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0 or not exe_path.is_file():
            raise FortranCompilationError(
                "Compilazione del numerical core Fortran fallita.", stderr=proc.stderr
            )
        return exe_path

    # ------------------------------------------------------------------
    # Esecuzione
    # ------------------------------------------------------------------
    def run(self, vertex_file: str | Path, face_file: str | Path, degree: int) -> tuple[np.ndarray, np.ndarray]:
        """Esegue il driver e ritorna (nodes[N,3], weights[N])."""
        exe = self.ensure_ready()

        with tempfile.TemporaryDirectory(prefix="optimalpolycuba3d_") as tmp:
            tmp_path = Path(tmp)
            nodes_file = tmp_path / "nodes.dat"
            weights_file = tmp_path / "weights.dat"

            cmd = [
                str(exe),
                str(vertex_file),
                str(face_file),
                str(degree),
                str(nodes_file),
                str(weights_file),
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

            if proc.returncode != 0:
                raise FortranRuntimeError(
                    "Il numerical core Fortran e' terminato con un errore.",
                    stdout=proc.stdout,
                    stderr=proc.stderr,
                )

            if not nodes_file.is_file() or not weights_file.is_file():
                raise FortranRuntimeError(
                    "Il numerical core non ha prodotto i file di output attesi.",
                    stdout=proc.stdout,
                    stderr=proc.stderr,
                )

            nodes = _read_output_matrix(nodes_file, n_cols=3)
            weights = _read_output_matrix(weights_file, n_cols=1).reshape(-1)

        if nodes.shape[0] == 0 or weights.shape[0] == 0:
            raise FortranRuntimeError("Output vuoto dal numerical core Fortran.")
        if nodes.shape[0] != weights.shape[0]:
            raise FortranRuntimeError(
                f"Numero di nodi ({nodes.shape[0]}) e pesi ({weights.shape[0]}) non coincide."
            )
        if not np.all(np.isfinite(nodes)) or not np.all(np.isfinite(weights)):
            raise FortranRuntimeError(
                "Il numerical core ha prodotto valori non finiti (NaN/Inf) nei nodi o nei pesi."
            )

        return nodes, weights


def _read_output_matrix(path: Path, n_cols: int) -> np.ndarray:
    with open(path, "r", encoding="utf-8") as f:
        count = int(f.readline().split()[0])
        data = np.loadtxt(f, dtype=np.float64, ndmin=2)
    if data.shape[0] != count:
        raise FortranRuntimeError(
            f"Il file {path.name} dichiara {count} righe ma ne contiene {data.shape[0]}."
        )
    return data.reshape(count, n_cols)

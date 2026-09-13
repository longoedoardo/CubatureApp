"""
I/O per i file .dat di mesh (stesso formato usato dal codice Fortran).

Formato vertex file:
    N
    x1 y1 z1
    ...
    xN yN zN

Formato face file (indici 1-based, come Fortran/MATLAB):
    M
    i1 j1 k1
    ...
    iM jM kM

Non viene mai scritto/modificato il file originale dell'utente: questo
modulo legge soltanto (a parte le utility di export usate internamente
per i file temporanei passati al driver Fortran, che sono file diversi
in una cartella temporanea).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


class MeshFileError(Exception):
    """Errore nel formato o nel contenuto di un file di mesh."""


@dataclass
class MeshData:
    vertices: np.ndarray  # (N, 3) float64
    faces_1based: np.ndarray  # (M, 3) int64, indici 1-based ORIGINALI (Fortran)
    vertex_file: str
    face_file: str

    @property
    def n_vertices(self) -> int:
        return self.vertices.shape[0]

    @property
    def n_faces(self) -> int:
        return self.faces_1based.shape[0]

    def faces_0based(self) -> np.ndarray:
        """Indici 0-based, utili solo per librerie di visualizzazione (PyVista)."""
        return self.faces_1based - 1


def _read_dat_matrix(path: Path, n_cols: int, kind: str) -> np.ndarray:
    if not path.is_file():
        raise MeshFileError(f"Il file non esiste:\n{path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            first_line = f.readline()
            if not first_line.strip():
                raise MeshFileError(f"File {kind} vuoto o senza intestazione:\n{path}")
            try:
                count = int(first_line.split()[0])
            except (ValueError, IndexError) as exc:
                raise MeshFileError(
                    f"La prima riga del file {kind} deve contenere il numero di righe.\n"
                    f"File: {path}"
                ) from exc

            rows = []
            for line_no, line in enumerate(f, start=2):
                stripped = line.strip()
                if not stripped:
                    continue
                parts = stripped.split()
                if len(parts) < n_cols:
                    raise MeshFileError(
                        f"Formato non valido nel file {kind} (riga {line_no}):\n"
                        f"attese {n_cols} colonne, trovate {len(parts)}.\nFile: {path}"
                    )
                rows.append(parts[:n_cols])
    except UnicodeDecodeError as exc:
        raise MeshFileError(f"Il file {kind} non sembra un file di testo valido:\n{path}") from exc

    if len(rows) != count:
        raise MeshFileError(
            f"Il file {kind} dichiara {count} righe ma ne contiene {len(rows)}.\nFile: {path}"
        )
    return np.array(rows)


def read_vertex_file(path: Path) -> np.ndarray:
    raw = _read_dat_matrix(path, 3, "vertici")
    try:
        vertices = raw.astype(np.float64)
    except ValueError as exc:
        raise MeshFileError(f"Coordinate non numeriche nel file vertici:\n{path}") from exc
    return vertices


def read_face_file(path: Path) -> np.ndarray:
    raw = _read_dat_matrix(path, 3, "facce")
    try:
        faces = raw.astype(np.int64)
    except ValueError as exc:
        raise MeshFileError(f"Indici non interi nel file facce:\n{path}") from exc
    return faces


def load_mesh(vertex_file: str | Path, face_file: str | Path) -> MeshData:
    vpath = Path(vertex_file)
    fpath = Path(face_file)
    vertices = read_vertex_file(vpath)
    faces = read_face_file(fpath)
    return MeshData(
        vertices=vertices,
        faces_1based=faces,
        vertex_file=str(vpath),
        face_file=str(fpath),
    )

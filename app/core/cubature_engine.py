"""
CubatureEngine: unico punto che la GUI chiama per "far girare tutto".

GUI -> CubatureEngine -> FortranBackend -> Fortran

La GUI non conosce ne' i dettagli della mesh, ne' del parsing della
funzione, ne' di come viene invocato il Fortran: riceve solo un
CubatureResult (o un'eccezione con un messaggio gia' presentabile).
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from app.core.fortran_backend import (
    FortranBackend,
    FortranCompilationError,
    FortranRuntimeError,
    FortranSourceError,
)
from app.function_parser.parser import FunctionParseError, parse_function
from app.geometry.mesh_io import MeshData, MeshFileError, load_mesh
from app.geometry.mesh_validation import ValidationResult, validate_mesh


class CubatureError(Exception):
    """Errore applicativo generico, con messaggio gia' pronto per l'utente."""


@dataclass
class CubatureResult:
    nodes: np.ndarray  # (N, 3)
    weights: np.ndarray  # (N,)
    function_values: np.ndarray  # (N,)
    integral: float
    degree: int
    n_vertices: int
    n_faces: int
    computation_time_s: float
    mesh: MeshData
    validation: ValidationResult
    integrand_text: str


def validate_inputs(vertex_file: str, face_file: str, degree: int) -> MeshData:
    """Carica i file mesh senza applicare controlli topologici o geometrici."""
    if not vertex_file:
        raise CubatureError("Nessun file dei vertici selezionato.")
    if not face_file:
        raise CubatureError("Nessun file delle facce selezionato.")
    if degree < 0:
        raise CubatureError("Il grado di esattezza deve essere >= 0.")

    try:
        mesh = load_mesh(vertex_file, face_file)
    except MeshFileError as exc:
        raise CubatureError(str(exc)) from exc

    return mesh


def compute_cubature(
    vertex_file: str,
    face_file: str,
    degree: int,
    integrand_text: str,
    fortran_source_dir: str | Path,
    build_dir: str | Path,
) -> CubatureResult:
    """Esegue l'intera pipeline: validazione -> Fortran -> valutazione funzione."""
    mesh = validate_inputs(vertex_file, face_file, degree)
    validation = validate_mesh(mesh, check_topology=False)

    try:
        parsed = parse_function(integrand_text)
    except FunctionParseError as exc:
        raise CubatureError(f"Invalid function.\n\n{exc}") from exc

    backend = FortranBackend(source_dir=Path(fortran_source_dir), build_dir=Path(build_dir))

    t0 = time.perf_counter()
    try:
        nodes, weights = backend.run(mesh.vertex_file, mesh.face_file, degree)
    except FortranSourceError as exc:
        raise CubatureError(f"Fortran source not configured correctly.\n\n{exc}") from exc
    except FortranCompilationError as exc:
        detail = f"\n\n{exc.stderr}" if exc.stderr else ""
        raise CubatureError(f"Fortran compilation error.{detail}") from exc
    except FortranRuntimeError as exc:
        detail_parts = []
        if exc.stdout:
            detail_parts.append(exc.stdout.strip())
        if exc.stderr:
            detail_parts.append(exc.stderr.strip())
        detail = ("\n\n" + "\n".join(detail_parts)) if detail_parts else ""
        raise CubatureError(f"Fortran runtime error.{detail}") from exc
    elapsed = time.perf_counter() - t0

    function_values = parsed.evaluate(nodes)
    integral = float(np.dot(weights, function_values))

    return CubatureResult(
        nodes=nodes,
        weights=weights,
        function_values=function_values,
        integral=integral,
        degree=degree,
        n_vertices=mesh.n_vertices,
        n_faces=mesh.n_faces,
        computation_time_s=elapsed,
        mesh=mesh,
        validation=validation,
        integrand_text=integrand_text,
    )

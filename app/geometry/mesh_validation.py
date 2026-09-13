"""
Validazione della mesh caricata.

Distingue tra:
  - errori (bloccanti: la mesh non puo' essere usata)
  - warning (non bloccanti: la mesh viene comunque mostrata/usata, ma
    l'utente viene avvisato di possibili problemi)

I controlli topologici (superficie chiusa, orientazione, vertici isolati)
sono volutamente semplici: non serve un motore topologico completo per
una prima versione, bastano euristiche basate sugli edge.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

import numpy as np

from .mesh_io import MeshData


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    bbox_min: np.ndarray | None = None
    bbox_max: np.ndarray | None = None

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0

    def summary_text(self) -> str:
        lines = []
        if self.errors:
            lines.append("Errori:")
            lines.extend(f"  - {e}" for e in self.errors)
        if self.warnings:
            lines.append("Avvisi:")
            lines.extend(f"  - {w}" for w in self.warnings)
        return "\n".join(lines) if lines else "Mesh valida."


def validate_mesh(mesh: MeshData, check_topology: bool = True) -> ValidationResult:
    """Controlla una mesh; la topologia può essere esclusa per una verifica rapida."""
    res = ValidationResult()
    vertices = mesh.vertices
    faces = mesh.faces_1based
    n_vertices = mesh.n_vertices
    n_faces = mesh.n_faces

    # --- controlli di base -------------------------------------------------
    if n_vertices == 0:
        res.errors.append("Il file dei vertici non contiene alcun vertice.")
    if n_faces == 0:
        res.errors.append("Il file delle facce non contiene alcuna faccia.")

    if vertices.ndim != 2 or vertices.shape[1] != 3:
        res.errors.append("I vertici devono essere una matrice N x 3.")
    if faces.ndim != 2 or faces.shape[1] != 3:
        res.errors.append("Le facce devono essere una matrice M x 3 (triangoli).")

    if not np.all(np.isfinite(vertices)):
        res.errors.append("Il file dei vertici contiene valori NaN o Inf.")

    if res.errors:
        # Senza dati numerici validi non ha senso continuare oltre.
        return res

    # --- indici di faccia validi -------------------------------------------
    min_idx = int(faces.min())
    max_idx = int(faces.max())
    if min_idx < 1:
        res.errors.append(f"Trovato indice di vertice non valido ({min_idx}); gli indici devono essere >= 1.")
    if max_idx > n_vertices:
        bad_face_rows = np.where(faces.max(axis=1) > n_vertices)[0]
        first_bad = bad_face_rows[0] + 1  # 1-based per l'utente
        bad_vertex = int(faces[bad_face_rows[0]].max())
        res.errors.append(
            f"La faccia {first_bad} referenzia il vertice {bad_vertex}, "
            f"ma la mesh contiene solo {n_vertices} vertici."
        )

    if res.errors:
        return res

    if not check_topology:
        res.bbox_min = vertices.min(axis=0)
        res.bbox_max = vertices.max(axis=0)
        return res

    # --- degenerazioni -------------------------------------------------
    degenerate = np.any(
        (faces[:, 0] == faces[:, 1]) | (faces[:, 1] == faces[:, 2]) | (faces[:, 0] == faces[:, 2])
    )
    if degenerate:
        n_deg = int(
            np.sum(
                (faces[:, 0] == faces[:, 1]) | (faces[:, 1] == faces[:, 2]) | (faces[:, 0] == faces[:, 2])
            )
        )
        res.warnings.append(f"{n_deg} faccia/e degenere/i (due vertici coincidenti).")

    # --- facce duplicate (stesso set di 3 vertici, ordine qualsiasi) --------
    face_sets = [tuple(sorted(row)) for row in faces]
    dup_count = len(face_sets) - len(set(face_sets))
    if dup_count > 0:
        res.warnings.append(f"{dup_count} faccia/e duplicata/e.")

    # --- vertici isolati -----------------------------------------------
    used_vertices = np.unique(faces) - 1  # a 0-based per confronto con arange
    all_vertices = np.arange(n_vertices)
    isolated = np.setdiff1d(all_vertices, used_vertices)
    if isolated.size > 0:
        res.warnings.append(f"{isolated.size} vertice/i isolato/i (non referenziato/i da alcuna faccia).")

    # --- superficie chiusa + orientazione (euristica sugli edge) --------
    # Per una mesh chiusa e coerentemente orientata, ogni edge orientato
    # (i -> j) deve comparire esattamente una volta, e il suo opposto
    # (j -> i) esattamente un'altra volta (una per ciascuna delle due
    # facce che condividono quell'edge).
    edges = []
    for tri in faces:
        i, j, k = tri
        edges.append((i, j))
        edges.append((j, k))
        edges.append((k, i))
    edge_counts = Counter(edges)

    non_manifold_or_open = 0
    inconsistent_orientation = 0
    for (a, b), cnt in edge_counts.items():
        if a > b:
            continue  # conto ogni coppia di edge opposti una sola volta
        forward = edge_counts.get((a, b), 0)
        backward = edge_counts.get((b, a), 0)
        if forward + backward != 2:
            non_manifold_or_open += 1
        elif forward != 1 or backward != 1:
            inconsistent_orientation += 1

    if non_manifold_or_open > 0:
        res.warnings.append(
            f"La superficie non sembra chiusa/manifold: {non_manifold_or_open} edge non "
            "condivisi esattamente da due facce (mesh aperta o non manifold)."
        )
    if inconsistent_orientation > 0:
        res.warnings.append(
            f"{inconsistent_orientation} edge con orientazione delle facce incoerente "
            "(le normali potrebbero non essere tutte uscenti)."
        )

    # --- bounding box --------------------------------------------------
    res.bbox_min = vertices.min(axis=0)
    res.bbox_max = vertices.max(axis=0)

    return res

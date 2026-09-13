"""
Widget di visualizzazione 3D (mesh + punti di quadratura) basato su
PyVista, incorporato in Qt tramite pyvistaqt.QtInteractor.

Espone un'API minimale che la GUI usa senza dover conoscere i dettagli
di VTK/PyVista:

    viewer.show_mesh(vertices, faces_0based)
    viewer.show_quadrature_points(nodes, weights)
    viewer.set_mesh_visible(bool)
    viewer.set_wireframe(bool)
    viewer.set_points_visible(bool)
    viewer.set_point_scale(float)
    viewer.reset_camera()
"""

from __future__ import annotations

import numpy as np
import pyvista as pv
from pyvistaqt import QtInteractor
from PySide6.QtWidgets import QVBoxLayout, QWidget

# Palette neutra/scientifica
MESH_COLOR = "#c7ced6"
MESH_EDGE_COLOR = "#5b6572"
BACKGROUND_TOP = "#f7f8fa"
BACKGROUND_BOTTOM = "#e7eaee"
POINT_CMAP = "cividis"
MESH_ALPHA = 0.65


class Viewer3D(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.plotter = QtInteractor(self)
        layout.addWidget(self.plotter.interactor)

        self.plotter.set_background(BACKGROUND_TOP, top=BACKGROUND_BOTTOM)

        self._mesh_actor = None
        self._points_actor = None
        self._point_scale = 1.0
        self._last_weights: np.ndarray | None = None
        self._last_nodes: np.ndarray | None = None

        self._show_mesh = True
        self._wireframe = False
        self._show_points = True

    # ------------------------------------------------------------------
    def show_mesh(self, vertices: np.ndarray, faces_0based: np.ndarray) -> None:
        self.clear_quadrature_points()
        n_faces = faces_0based.shape[0]
        # Formato "faces" di PyVista: [3, i0, j0, k0, 3, i1, j1, k1, ...]
        faces_pv = np.hstack(
            [np.full((n_faces, 1), 3, dtype=np.int64), faces_0based.astype(np.int64)]
        ).ravel()

        poly = pv.PolyData(vertices.astype(np.float64), faces_pv)

        if self._mesh_actor is not None:
            self.plotter.remove_actor(self._mesh_actor)

        style = "wireframe" if self._wireframe else "surface"
        self._mesh_actor = self.plotter.add_mesh(
            poly,
            color=MESH_COLOR,
            show_edges=True,
            edge_color=MESH_EDGE_COLOR,
            line_width=1.0,
            style=style,
            smooth_shading=not self._wireframe,
            opacity=MESH_ALPHA,
            name="mesh",
        )
        self._mesh_actor.SetVisibility(self._show_mesh or self._wireframe)
        self.plotter.reset_camera()
        self.plotter.view_isometric()

    def show_quadrature_points(self, nodes: np.ndarray, weights: np.ndarray) -> None:
        self._last_nodes = nodes
        self._last_weights = weights

        if self._points_actor is not None:
            self.plotter.remove_actor(self._points_actor)
            self._points_actor = None

        if nodes.shape[0] == 0:
            return

        cloud = pv.PolyData(nodes.astype(np.float64))
        abs_w = np.abs(weights)
        cloud["abs_weight"] = abs_w

        self._points_actor = self.plotter.add_mesh(
            cloud,
            scalars="abs_weight",
            cmap=POINT_CMAP,
            name="quadrature_points",
            render_points_as_spheres=True,
            point_size=self._point_size(),
            show_scalar_bar=True,
            scalar_bar_args={
                "title": "",
                "vertical": True,
                "position_x": 0.92,
                "position_y": 0.26,
                "width": 0.06,
                "height": 0.48,
                "n_labels": 4,
                "title_font_size": 16,
                "label_font_size": 11,
                "color": "#2b2f36",
                "font_family": "arial",
                "outline": False,
                "fmt": "%.2e",
            },
        )
        self._points_actor.SetVisibility(self._show_points)

    def _point_size(self) -> float:
        bounds = self.plotter.renderer.ComputeVisiblePropBounds() if self.plotter.renderer.actors else None
        if bounds:
            diag = np.linalg.norm([bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4]])
        else:
            diag = 1.0
        return max(4.0, min(18.0, max(diag, 1e-6) * 5.0 * self._point_scale))

    # ------------------------------------------------------------------
    def set_mesh_visible(self, visible: bool) -> None:
        self._show_mesh = visible
        if self._mesh_actor is not None:
            self._mesh_actor.SetVisibility(visible or self._wireframe)
            self.plotter.render()

    def set_wireframe(self, wireframe: bool) -> None:
        self._wireframe = wireframe
        if self._mesh_actor is not None:
            self._mesh_actor.GetProperty().SetRepresentationToWireframe() if wireframe \
                else self._mesh_actor.GetProperty().SetRepresentationToSurface()
            self._mesh_actor.SetVisibility(wireframe or self._show_mesh)
            self.plotter.render()

    def set_points_visible(self, visible: bool) -> None:
        self._show_points = visible
        if self._points_actor is not None:
            self._points_actor.SetVisibility(visible)
            self.plotter.render()

    def set_point_scale(self, scale: float) -> None:
        self._point_scale = scale
        if self._points_actor is not None:
            self._points_actor.GetProperty().SetPointSize(self._point_size())
            self.plotter.render()

    def clear_quadrature_points(self) -> None:
        self._last_nodes = None
        self._last_weights = None
        if self._points_actor is not None:
            self.plotter.remove_actor(self._points_actor)
            self._points_actor = None
        self.plotter.render()

    def set_axes_visible(self, visible: bool) -> None:
        if visible:
            self.plotter.show_axes()
        else:
            self.plotter.hide_axes()

    def reset_camera(self) -> None:
        self.plotter.reset_camera()
        self.plotter.view_isometric()

    def clear(self) -> None:
        self.plotter.clear()
        self._mesh_actor = None
        self._points_actor = None
        self._last_nodes = None
        self._last_weights = None

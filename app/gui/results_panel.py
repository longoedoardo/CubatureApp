from __future__ import annotations

import numpy as np

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QGridLayout, QLabel, QWidget


def _card_shadow() -> QGraphicsDropShadowEffect:
    effect = QGraphicsDropShadowEffect()
    effect.setBlurRadius(22)
    effect.setOffset(0, -2)
    effect.setColor(QColor(13, 30, 46, 22))
    return effect


def _divider() -> QFrame:
    line = QFrame()
    line.setObjectName("MetricDivider")
    line.setFrameShape(QFrame.VLine)
    return line


def _metric(label_text: str) -> tuple[QWidget, QLabel]:
    container = QWidget()
    container.setProperty("role", "metricContainer")
    layout = QGridLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(2)

    value_label = QLabel("—")
    value_label.setProperty("role", "metricValue")

    caption = QLabel(label_text)
    caption.setProperty("role", "metricLabel")

    layout.addWidget(value_label, 0, 0)
    layout.addWidget(caption, 1, 0)
    return container, value_label


class ResultsPanel(QFrame):
    """Barra dei risultati in basso, sempre visibile."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("ResultsBar")
        self.setFixedHeight(86)
        self.setMinimumWidth(1420)
        self.setGraphicsEffect(_card_shadow())

        layout = QGridLayout(self)
        layout.setContentsMargins(14, 4, 14, 4)
        layout.setHorizontalSpacing(10)

        title = QLabel("RESULTS")
        title.setObjectName("ResultsTitle")
        layout.addWidget(title, 0, 0, 1, 21)

        metrics = [
            ("Integral", "integral_value"),
            ("Absolute error", "error_value"),
            ("Quadrature points", "points_value"),
            ("Degree", "degree_value"),
            ("Mesh vertices", "vertices_value"),
            ("Mesh triangles", "faces_value"),
            ("Computation time", "time_value"),
            ("Volume", "volume_value"),
            ("Negative weights", "negative_weights_value"),
            ("Positive weights", "positive_weights_value"),
        ]

        col = 0
        for i, (caption, attr_name) in enumerate(metrics):
            w, value_label = _metric(caption)
            layout.addWidget(w, 1, col)
            setattr(self, attr_name, value_label)
            col += 1
            if i < len(metrics) - 1:
                layout.addWidget(_divider(), 1, col)
                col += 1

        layout.setColumnStretch(col, 1)

        self.clear()

    def clear(self) -> None:
        for lbl in (
            self.integral_value,
            self.error_value,
            self.points_value,
            self.degree_value,
            self.vertices_value,
            self.faces_value,
            self.time_value,
            self.volume_value,
            self.negative_weights_value,
            self.positive_weights_value,
        ):
            lbl.setText("—")

    def update_results(
        self,
        integral: float,
        n_points: int,
        degree: int,
        n_vertices: int,
        n_faces: int,
        computation_time_s: float,
        weights: np.ndarray,
        exact_value: float | None = None,
    ) -> None:
        self.integral_value.setText(f"{integral:.12g}")
        self.points_value.setText(str(n_points))
        self.degree_value.setText(str(degree))
        self.vertices_value.setText(str(n_vertices))
        self.faces_value.setText(str(n_faces))
        self.time_value.setText(f"{computation_time_s * 1000:.1f} ms")
        self.volume_value.setText(f"{float(np.sum(weights)):.12g}")
        self.negative_weights_value.setText(str(int(np.count_nonzero(weights < 0))))
        self.positive_weights_value.setText(str(int(np.count_nonzero(weights > 0))))

        if exact_value is None:
            self.error_value.setText("N/A")
        else:
            absolute_error = abs(integral - exact_value)
            self.error_value.setText(
                "<10^-15" if absolute_error < 1e-14 else f"{absolute_error:.3e}"
            )

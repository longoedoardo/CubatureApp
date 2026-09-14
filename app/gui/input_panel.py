from __future__ import annotations

from PySide6.QtCore import Qt, QLocale, Signal
from PySide6.QtGui import QColor, QDoubleValidator
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QGraphicsDropShadowEffect,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


def _card_shadow(blur: int = 18, y_offset: int = 3, alpha: int = 28) -> QGraphicsDropShadowEffect:
    effect = QGraphicsDropShadowEffect()
    effect.setBlurRadius(blur)
    effect.setOffset(0, y_offset)
    effect.setColor(QColor(13, 30, 46, alpha))
    return effect


class InputPanel(QWidget):
    """Pannello sinistro: input mesh/funzione/grado + controlli di visualizzazione."""

    compute_requested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setFixedWidth(340)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(12, 12, 12, 12)

        layout.addWidget(self._build_mesh_group())
        layout.addWidget(self._build_function_group())
        layout.addWidget(self._build_view_group())

        self.compute_button = QPushButton("COMPUTE CUBATURE")
        self.compute_button.setObjectName("ComputeButton")
        self.compute_button.setToolTip("Compute the integral on the current mesh")
        self.compute_button.clicked.connect(self.compute_requested.emit)
        self.compute_button.setGraphicsEffect(_card_shadow(blur=20, y_offset=4, alpha=60))
        layout.addWidget(self.compute_button)

        self.status_label = QLabel("")
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        layout.addStretch(1)

    # ------------------------------------------------------------------
    def _build_mesh_group(self) -> QGroupBox:
        box = QGroupBox("Mesh input")
        box.setGraphicsEffect(_card_shadow())
        v = QVBoxLayout(box)
        v.setSpacing(9)

        row1 = QHBoxLayout()
        self.vertex_edit = QLineEdit()
        self.vertex_edit.setPlaceholderText("Vertex file (.dat)")
        self.vertex_edit.setClearButtonEnabled(True)
        btn1 = QPushButton("Browse…")
        btn1.setObjectName("SecondaryButton")
        btn1.setToolTip("Select the vertex file")
        btn1.clicked.connect(self._browse_vertex_file)
        row1.addWidget(self.vertex_edit)
        row1.addWidget(btn1)
        v.addLayout(row1)

        row2 = QHBoxLayout()
        self.face_edit = QLineEdit()
        self.face_edit.setPlaceholderText("Face file (.dat)")
        self.face_edit.setClearButtonEnabled(True)
        btn2 = QPushButton("Browse…")
        btn2.setObjectName("SecondaryButton")
        btn2.setToolTip("Select the triangular face file")
        btn2.clicked.connect(self._browse_face_file)
        row2.addWidget(self.face_edit)
        row2.addWidget(btn2)
        v.addLayout(row2)

        self.clear_mesh_button = QPushButton("Clear")
        self.clear_mesh_button.setObjectName("SecondaryButton")
        self.clear_mesh_button.setToolTip("Clear the selected mesh files")
        self.clear_mesh_button.clicked.connect(self._clear_mesh)
        v.addWidget(self.clear_mesh_button)

        return box

    def _build_function_group(self) -> QGroupBox:
        box = QGroupBox("Integrand")
        box.setGraphicsEffect(_card_shadow())
        v = QVBoxLayout(box)
        v.setSpacing(9)

        function_label = QLabel("f(x, y, z)")
        function_label.setObjectName("FunctionMathLabel")
        function_label.setToolTip(
            r"Enter the function using LaTeX notation (e.g. x^{2}+y^{2}, "
            r"\sin(x)\cos(y), e^{-(x^2+y^2+z^2)})."
        )
        v.addWidget(function_label)

        self.function_edit = QLineEdit()
        self.function_edit.setPlaceholderText("Function f(x, y, z)")
        self.function_edit.setClearButtonEnabled(True)
        self.function_edit.setToolTip(
            "Enter a function in x, y and z using LaTeX notation."
        )
        v.addWidget(self.function_edit)

        deg_row = QHBoxLayout()
        deg_row.setSpacing(8)
        deg_row.addWidget(QLabel("Algebraic Degree of Exactness (ADE):"))
        self.degree_spin = QSpinBox()
        self.degree_spin.setRange(0, 20)
        self.degree_spin.setValue(4)
        self.degree_spin.setToolTip("Enter the exactness precision (ADE) of the cubature rule.")
        deg_row.addWidget(self.degree_spin)
        v.addLayout(deg_row)

        exact_row = QHBoxLayout()
        exact_row.setSpacing(8)
        exact_row.addWidget(QLabel("Expected Result:"))
        self.exact_value_edit = QLineEdit()
        self.exact_value_edit.setPlaceholderText("Expected result (optional)")
        self.exact_value_edit.setClearButtonEnabled(True)
        # The validator must use a fixed locale ("."  as decimal point),
        # otherwise on systems whose locale uses "," (e.g. Italian) the
        # field would accept "0,2963" while Python's float() below only
        # understands "0.2963": a perfectly correct value typed by the
        # user would be flagged as invalid. get_exact_value() below adds
        # a second layer of tolerance for the same reason.
        exact_value_validator = QDoubleValidator()
        exact_value_validator.setLocale(QLocale(QLocale.C))
        exact_value_validator.setNotation(QDoubleValidator.ScientificNotation)
        self.exact_value_edit.setValidator(exact_value_validator)
        self.exact_value_edit.setToolTip(
            "Enter the expected result to calculate the absolute error automatically."
        )
        exact_row.addWidget(self.exact_value_edit)
        v.addLayout(exact_row)

        return box

    def _build_view_group(self) -> QGroupBox:
        box = QGroupBox("View")
        box.setGraphicsEffect(_card_shadow())
        v = QVBoxLayout(box)
        v.setSpacing(10)

        self.chk_show_mesh = QCheckBox("Mesh")
        self.chk_show_mesh.setChecked(True)
        v.addWidget(self.chk_show_mesh)

        self.chk_wireframe = QCheckBox("Wireframe")
        v.addWidget(self.chk_wireframe)

        self.chk_show_axes = QCheckBox("Axes")
        self.chk_show_axes.setChecked(True)
        v.addWidget(self.chk_show_axes)

        self.chk_show_points = QCheckBox("Quadrature Points")
        self.chk_show_points.setChecked(True)
        v.addWidget(self.chk_show_points)

        size_row = QHBoxLayout()
        size_row.addWidget(QLabel("Point size"))
        self.point_size_slider = QSlider(Qt.Horizontal)
        self.point_size_slider.setRange(1, 50)
        self.point_size_slider.setValue(10)
        size_row.addWidget(self.point_size_slider)
        v.addLayout(size_row)

        reset_btn = QPushButton("Reset camera")
        reset_btn.setObjectName("SecondaryButton")
        reset_btn.setToolTip("Return the camera to the isometric view")
        self.reset_camera_button = reset_btn
        v.addWidget(reset_btn)

        return box

    # ------------------------------------------------------------------
    def _browse_vertex_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select vertex file", "", "Data files (*.dat);;All files (*)")
        if path:
            self.vertex_edit.setText(path)

    def _browse_face_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select face file", "", "Data files (*.dat);;All files (*)")
        if path:
            self.face_edit.setText(path)

    def _clear_mesh(self) -> None:
        self.vertex_edit.clear()
        self.face_edit.clear()

    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    def get_exact_value(self) -> tuple[float | None, bool]:
        """Ritorna (valore, valido). valore=None e valido=True se il campo e' vuoto
        (nessun valore esatto fornito, non e' un errore). valido=False se il
        testo inserito non e' un numero interpretabile.

        Il testo puo' arrivare con la virgola come separatore decimale
        (tastiera/locale italiani, testo incollato da altre applicazioni):
        la normalizziamo qui, in un unico punto, cosi' un valore atteso
        corretto non viene mai scartato solo per la punteggiatura usata.
        """
        text = self.exact_value_edit.text().strip()
        if not text:
            return None, True
        if "," in text and "." not in text:
            text = text.replace(",", ".")
        try:
            return float(text), True
        except ValueError:
            return None, False

    def set_busy(self, busy: bool) -> None:
        self.compute_button.setEnabled(not busy)
        self.compute_button.setText("Computing cubature…" if busy else "COMPUTE CUBATURE")

    def set_status(self, text: str, role: str = "") -> None:
        indicator = {
            "statusOk": "●",
            "statusError": "●",
            "statusBusy": "●",
        }.get(role, "●")
        self.status_label.setText(f"{indicator} {text}" if text else "")
        self.status_label.setProperty("role", role)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

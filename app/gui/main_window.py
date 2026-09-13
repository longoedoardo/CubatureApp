from __future__ import annotations

import traceback
import shutil
from pathlib import Path

from PySide6.QtCore import QObject, QThread, QTimer, Signal
from PySide6.QtGui import QKeySequence, QPixmap, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt

from app.config.settings import Settings, load_settings, save_settings
from app.core.cubature_engine import CubatureError, CubatureResult, compute_cubature
from app.core.fortran_backend import FortranBackend, FortranSourceError
from app.geometry.mesh_io import MeshFileError, load_mesh
from app.geometry.mesh_validation import validate_mesh
from app.gui.export_dialog import ExportDialog
from app.gui.input_panel import InputPanel
from app.gui.results_panel import ResultsPanel
from app.report_pdf import write_pdf_report
from app.visualization.viewer3d import Viewer3D


class ComputeWorker(QObject):
    """Esegue compute_cubature in un thread separato (vedi punto 22 della specifica)."""

    finished = Signal(object)  # CubatureResult
    failed = Signal(str)

    def __init__(self, vertex_file, face_file, degree, integrand_text, fortran_source_dir, build_dir):
        super().__init__()
        self._args = (vertex_file, face_file, degree, integrand_text, fortran_source_dir, build_dir)

    def run(self) -> None:
        try:
            result = compute_cubature(*self._args)
        except CubatureError as exc:
            self.failed.emit(str(exc))
        except Exception:  # pragma: no cover - rete di sicurezza contro eccezioni impreviste
            self.failed.emit("Unexpected internal error:\n\n" + traceback.format_exc())
        else:
            self.finished.emit(result)


class HeaderBar(QWidget):
    open_settings_requested = Signal()
    export_requested = Signal()
    pdf_export_requested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("HeaderBar")
        self.setFixedHeight(64)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 8, 20, 8)

        brand_box = QHBoxLayout()
        brand_box.setSpacing(10)
        icon_label = QLabel()
        icon_label.setObjectName("HeaderIcon")
        icon_path = Path(__file__).resolve().parents[1] / "assets" / "cubature_icon.svg"
        icon_label.setPixmap(QPixmap(str(icon_path)).scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        brand_box.addWidget(icon_label)

        text_box = QVBoxLayout()
        text_box.setSpacing(2)
        title = QLabel("OptimalPolyCuba3D")
        title.setObjectName("HeaderTitle")
        subtitle = QLabel("Numerical Cubature on Polyhedral Domains")
        subtitle.setObjectName("HeaderSubtitle")
        text_box.addWidget(title)
        text_box.addWidget(subtitle)
        brand_box.addLayout(text_box)
        layout.addLayout(brand_box)
        layout.addStretch(1)

        self.backend_badge = QLabel("Fortran backend: —")
        self.backend_badge.setObjectName("HeaderBadge")
        self.backend_badge.hide()

        settings_btn = QPushButton("Fortran source…")
        settings_btn.setObjectName("HeaderButton")
        settings_btn.setToolTip("Configure the Fortran source directory")
        settings_btn.clicked.connect(self.open_settings_requested.emit)
        layout.addWidget(settings_btn)

        self.export_button = QPushButton("Export CSV…")
        self.export_button.setObjectName("HeaderButton")
        self.export_button.setEnabled(False)
        self.export_button.setToolTip("Export the latest cubature result")
        self.export_button.clicked.connect(self.export_requested.emit)
        layout.addWidget(self.export_button)

        self.pdf_button = QPushButton("Export PDF…")
        self.pdf_button.setObjectName("HeaderButton")
        self.pdf_button.setEnabled(False)
        self.pdf_button.setToolTip("Export a technical PDF report")
        self.pdf_button.clicked.connect(self.pdf_export_requested.emit)
        layout.addWidget(self.pdf_button)

    def set_backend_status(self, ready: bool) -> None:
        self.backend_badge.setText("Fortran backend: ready" if ready else "Fortran backend: not configured")
        self.backend_badge.setProperty("state", "ready" if ready else "missing")
        self.backend_badge.style().unpolish(self.backend_badge)
        self.backend_badge.style().polish(self.backend_badge)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OptimalPolyCuba3D")
        available = QApplication.primaryScreen().availableGeometry()
        window_width = min(1180, available.width() - 40)
        window_height = min(720, available.height() - 80)
        self.resize(max(980, window_width), max(620, window_height))

        self.settings: Settings = load_settings()
        self._pending_exact_value: float | None = None
        self._last_exact_value: float | None = None
        self._last_result: CubatureResult | None = None
        self._thread: QThread | None = None
        self._worker: ComputeWorker | None = None
        self._preview_cache_key: tuple[object, ...] | None = None
        self._preview_cache: tuple[object, object] | None = None
        self._preview_timer = QTimer(self)
        self._preview_timer.setSingleShot(True)
        self._preview_timer.setInterval(250)
        self._preview_timer.timeout.connect(self._preview_mesh_now)

        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.header = HeaderBar()
        self.header.open_settings_requested.connect(self._choose_fortran_source_dir)
        self.header.export_requested.connect(self._open_export_dialog)
        self.header.pdf_export_requested.connect(self._export_pdf_report)
        root_layout.addWidget(self.header)

        # The left controls scroll vertically; the 3D view keeps the remaining space.
        splitter = QSplitter(Qt.Horizontal)
        self.input_panel = InputPanel()
        self.viewer = Viewer3D()

        input_scroll = QScrollArea()
        input_scroll.setObjectName("InputScrollArea")
        input_scroll.setWidgetResizable(False)
        input_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        input_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        input_scroll.setFrameShape(QScrollArea.NoFrame)
        input_scroll.setWidget(self.input_panel)
        splitter.addWidget(input_scroll)
        splitter.addWidget(self.viewer)
        splitter.setSizes([360, 920])
        splitter.setStretchFactor(1, 1)
        root_layout.addWidget(splitter, stretch=1)

        # Results stay in one horizontal strip. On narrow windows only this strip scrolls.
        self.results_panel = ResultsPanel()
        self.results_scroll = QScrollArea()
        self.results_scroll.setObjectName("ResultsScrollArea")
        self.results_scroll.setWidgetResizable(False)
        self.results_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.results_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.results_scroll.setFixedHeight(self.results_panel.height() + 14)
        self.results_scroll.setFrameShape(QScrollArea.NoFrame)
        self.results_scroll.setWidget(self.results_panel)
        root_layout.addWidget(self.results_scroll)

        # --- collegamenti -------------------------------------------------
        self.input_panel.compute_requested.connect(self._on_compute_clicked)
        self.input_panel.function_edit.returnPressed.connect(self._on_compute_clicked)
        self._compute_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        self._compute_shortcut.activated.connect(self._on_compute_clicked)
        self.input_panel.vertex_edit.setText(self.settings.last_vertex_file)
        self.input_panel.face_edit.setText(self.settings.last_face_file)
        self.input_panel.function_edit.setText(self.settings.last_integrand)
        self.input_panel.degree_spin.setValue(self.settings.last_degree)

        self.input_panel.vertex_edit.textChanged.connect(self._on_geometry_changed)
        self.input_panel.face_edit.textChanged.connect(self._on_geometry_changed)
        self.input_panel.clear_mesh_button.clicked.connect(self._clear_preview_cache)

        self.input_panel.chk_show_mesh.toggled.connect(self._on_mesh_toggled)
        self.input_panel.chk_wireframe.toggled.connect(self._on_wireframe_toggled)
        self.input_panel.chk_show_axes.toggled.connect(self.viewer.set_axes_visible)
        self.input_panel.chk_show_points.toggled.connect(self.viewer.set_points_visible)
        self.input_panel.point_size_slider.valueChanged.connect(
            lambda v: self.viewer.set_point_scale(v / 10.0)
        )
        self.input_panel.reset_camera_button.clicked.connect(self.viewer.reset_camera)

        self.viewer.set_axes_visible(True)

        if not self.settings.is_fortran_source_configured():
            self._prompt_fortran_source_on_first_launch()
        else:
            self._preview_mesh_now()

        self._update_backend_badge()

    # ------------------------------------------------------------------
    # Configurazione sorgenti Fortran
    # ------------------------------------------------------------------
    def _prompt_fortran_source_on_first_launch(self) -> None:
        QMessageBox.information(
            self,
            "Fortran source directory",
            "No valid Fortran source directory is configured yet.\n\n"
            "In the next window, choose the folder containing:\n"
            "  TypesDef.f90, PrepCheap.f90, PolyhedronMesh.f90,\n"
            "  triangleQuadratureGJ.f90, CubaCheap.f90, OptimalPolyCuba3D.f90\n\n"
            f"Suggested default path: {self.settings.fortran_source_dir}",
        )
        self._choose_fortran_source_dir()

    def _choose_fortran_source_dir(self) -> None:
        directory = QFileDialog.getExistingDirectory(
            self, "Select Fortran source directory", self.settings.fortran_source_dir
        )
        if not directory:
            return
        self.settings.fortran_source_dir = directory
        save_settings(self.settings)

        try:
            FortranBackend(
                source_dir=self.settings.fortran_source_path(),
                build_dir=self.settings.build_path(),
            ).check_sources()
        except FortranSourceError as exc:
            self.input_panel.set_status(
                "Fortran source error: " + str(exc), "statusError"
            )
            QMessageBox.warning(self, "Fortran source directory", str(exc))
            self._update_backend_badge()
            return

        self.input_panel.set_status("Fortran source directory configured successfully.", "statusOk")
        self._update_backend_badge()

    def _update_backend_badge(self) -> None:
        self.header.set_backend_status(self.settings.is_fortran_source_configured())
        if not self.settings.is_fortran_source_configured():
            self.input_panel.set_status(
                "Fortran backend is not configured correctly.", "statusError"
            )

    def _on_wireframe_toggled(self, enabled: bool) -> None:
        if enabled:
            self.input_panel.chk_show_mesh.blockSignals(True)
            self.input_panel.chk_show_mesh.setChecked(False)
            self.input_panel.chk_show_mesh.blockSignals(False)
            self.viewer.set_wireframe(True)
            self.viewer.set_mesh_visible(False)
            return

        self.input_panel.chk_show_mesh.blockSignals(True)
        self.input_panel.chk_show_mesh.setChecked(True)
        self.input_panel.chk_show_mesh.blockSignals(False)
        self.viewer.set_wireframe(False)
        self.viewer.set_mesh_visible(True)

    def _on_mesh_toggled(self, enabled: bool) -> None:
        if enabled and self.input_panel.chk_wireframe.isChecked():
            self.input_panel.chk_wireframe.blockSignals(True)
            self.input_panel.chk_wireframe.setChecked(False)
            self.input_panel.chk_wireframe.blockSignals(False)
            self.viewer.set_wireframe(False)
        self.viewer.set_mesh_visible(enabled)

    def _validate_compute_inputs(
        self, vertex_file: str, face_file: str, integrand_text: str
    ) -> str | None:
        if not vertex_file or not face_file or not integrand_text:
            missing = []
            if not vertex_file:
                missing.append("vertex file")
            if not face_file:
                missing.append("face file")
            if not integrand_text:
                missing.append("integrand")
            return "Complete these fields: " + ", ".join(missing) + "."
        vertex_path = Path(vertex_file)
        face_path = Path(face_file)
        if vertex_path.suffix.lower() != ".dat" or face_path.suffix.lower() != ".dat":
            return "Vertex and face files must use the .dat extension."
        if not vertex_path.is_file() or not face_path.is_file():
            return "The selected vertex and face files must exist."
        if vertex_path.resolve() == face_path.resolve():
            return "Vertex and face files must be different files."
        if not self.settings.is_fortran_source_configured():
            return "The Fortran source directory is incomplete or unavailable."
        if shutil.which("gfortran") is None and not any(
            Path(path).is_file() for path in ("/opt/homebrew/bin/gfortran", "/usr/local/bin/gfortran")
        ):
            return "The gfortran compiler is not available."
        return None

    # ------------------------------------------------------------------
    # Anteprima mesh (Phase 2, indipendente dal calcolo)
    # ------------------------------------------------------------------
    def _schedule_mesh_preview(self) -> None:
        """Attende la fine della digitazione prima di leggere la mesh."""
        self._preview_timer.start()

    def _on_geometry_changed(self) -> None:
        self._clear_preview_cache()
        self.viewer.clear_quadrature_points()
        self.results_panel.clear()
        self._schedule_mesh_preview()

    def _clear_preview_cache(self) -> None:
        self._preview_timer.stop()
        self._preview_cache_key = None
        self._preview_cache = None

    def _preview_mesh_now(self) -> None:
        vfile = self.input_panel.vertex_edit.text().strip()
        ffile = self.input_panel.face_edit.text().strip()
        if not vfile or not ffile:
            return

        def file_signature(path: str) -> tuple[str, int, int] | tuple[str, None, None]:
            try:
                stat = Path(path).stat()
            except OSError:
                return path, None, None
            return path, stat.st_mtime_ns, stat.st_size

        cache_key = (*file_signature(vfile), *file_signature(ffile))
        if cache_key == self._preview_cache_key and self._preview_cache is not None:
            mesh, validation = self._preview_cache
        else:
            try:
                mesh = load_mesh(vfile, ffile)
            except MeshFileError:
                return  # l'utente sta ancora scrivendo il percorso: non disturbare

            validation = validate_mesh(mesh, check_topology=False)
            self._preview_cache_key = cache_key
            self._preview_cache = (mesh, validation)

        if not validation.ok:
            self.input_panel.set_status(
                "Mesh check: " + validation.summary_text(), "statusError"
            )
            return

        self.viewer.show_mesh(mesh.vertices, mesh.faces_0based())
        self.input_panel.set_status(
            f"Mesh ready: {mesh.n_vertices} vertices, {mesh.n_faces} faces.", "statusOk"
        )

    # ------------------------------------------------------------------
    # Calcolo cubatura
    # ------------------------------------------------------------------
    def _on_compute_clicked(self) -> None:
        if self._thread is not None:
            return  # calcolo gia' in corso

        vertex_file = self.input_panel.vertex_edit.text().strip()
        face_file = self.input_panel.face_edit.text().strip()
        integrand_text = self.input_panel.function_edit.text().strip()
        degree = self.input_panel.degree_spin.value()

        exact_value, exact_value_valid = self.input_panel.get_exact_value()
        if not exact_value_valid:
            self.input_panel.set_status(
                "Expected result is invalid: enter a number (e.g. 8, 0.2963, -1.5e-3) or leave the field empty.",
                "statusError",
            )
            return

        input_error = self._validate_compute_inputs(vertex_file, face_file, integrand_text)
        if input_error:
            self.input_panel.set_status(input_error, "statusError")
            return

        self.settings.last_vertex_file = vertex_file
        self.settings.last_face_file = face_file
        self.settings.last_integrand = integrand_text
        self.settings.last_degree = degree
        save_settings(self.settings)

        self._pending_exact_value = exact_value
        self._last_exact_value = exact_value

        self.input_panel.set_busy(True)
        self.header.export_button.setEnabled(False)
        self.header.pdf_button.setEnabled(False)
        self.results_panel.clear()
        self.input_panel.set_status("Computation in progress…", "statusBusy")

        self._thread = QThread(self)
        self._worker = ComputeWorker(
            vertex_file,
            face_file,
            degree,
            integrand_text,
            self.settings.fortran_source_dir,
            self.settings.build_dir,
        )
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_compute_finished)
        self._worker.failed.connect(self._on_compute_failed)
        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._thread.finished.connect(self._cleanup_thread)
        self._thread.start()

    def _cleanup_thread(self) -> None:
        self.input_panel.set_busy(False)
        thread = self._thread
        worker = self._worker
        self._thread = None
        self._worker = None
        self._pending_exact_value = None
        if worker is not None:
            worker.deleteLater()
        if thread is not None:
            thread.deleteLater()

    def _on_compute_finished(self, result: CubatureResult) -> None:
        self._last_result = result
        self.input_panel.set_busy(False)
        self.header.export_button.setEnabled(True)
        self.header.pdf_button.setEnabled(True)
        self._clear_preview_cache()
        self.viewer.show_mesh(result.mesh.vertices, result.mesh.faces_0based())
        self.viewer.show_quadrature_points(result.nodes, result.weights)
        self.results_panel.update_results(
            integral=result.integral,
            n_points=result.nodes.shape[0],
            degree=result.degree,
            n_vertices=result.n_vertices,
            n_faces=result.n_faces,
            computation_time_s=result.computation_time_s,
            weights=result.weights,
            exact_value=self._pending_exact_value,
        )
        self.input_panel.set_status("Computation complete.", "statusOk")

    def _on_compute_failed(self, message: str) -> None:
        self._last_result = None
        self._last_exact_value = None
        self.header.export_button.setEnabled(False)
        self.header.pdf_button.setEnabled(False)
        self.header.export_button.setEnabled(False)
        self.input_panel.set_busy(False)
        self._clear_preview_cache()
        self.input_panel.set_status(message, "statusError")
        QMessageBox.critical(self, "Compute cubature", message)

    def _open_export_dialog(self) -> None:
        if self._last_result is None:
            return
        ExportDialog(
            self._last_result,
            exact_value=self._last_exact_value,
            parent=self,
        ).exec()

    def _export_pdf_report(self) -> None:
        if self._last_result is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export PDF report",
            "cubature_report.pdf",
            "PDF files (*.pdf);;All files (*)",
        )
        if not path:
            return
        try:
            write_pdf_report(self._last_result, path, self._last_exact_value)
        except (OSError, ValueError, RuntimeError) as exc:
            QMessageBox.critical(self, "Export PDF report", f"Could not write the PDF report:\n{exc}")
            return
        self.input_panel.set_status("PDF report exported.", "statusOk")

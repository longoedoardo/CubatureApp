from __future__ import annotations

import csv
from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)


class ExportDialog(QDialog):
    """Selects the data sections and writes them to one readable CSV file."""

    def __init__(self, result, exact_value=None, parent=None):
        super().__init__(parent)
        self.result = result
        self.exact_value = exact_value
        self.setWindowTitle("Export results")
        self.setMinimumWidth(360)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Choose the sections to include in the CSV file:"))

        self.summary_check = QCheckBox("Summary results")
        self.summary_check.setChecked(True)
        self.nodes_check = QCheckBox("Quadrature nodes and weights")
        self.nodes_check.setChecked(True)
        self.mesh_check = QCheckBox("Mesh information")
        self.mesh_check.setChecked(True)
        layout.addWidget(self.summary_check)
        layout.addWidget(self.nodes_check)
        layout.addWidget(self.mesh_check)

        self.choose_button = QPushButton("Export CSV…")
        self.choose_button.clicked.connect(self._choose_path)
        layout.addWidget(self.choose_button)

        buttons = QDialogButtonBox(QDialogButtonBox.Cancel)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _choose_path(self) -> None:
        if not any((self.summary_check.isChecked(), self.nodes_check.isChecked(), self.mesh_check.isChecked())):
            QMessageBox.warning(self, "Export results", "Select at least one section.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export CSV",
            "cubature_results.csv",
            "CSV files (*.csv);;All files (*)",
        )
        if not path:
            return

        try:
            self._write_csv(Path(path))
        except OSError as exc:
            QMessageBox.critical(self, "Export results", f"Could not write the CSV file:\n{exc}")
            return

        QMessageBox.information(self, "Export results", f"CSV exported to:\n{path}")
        self.accept()

    def _write_csv(self, path: Path) -> None:
        result = self.result
        with path.open("w", newline="", encoding="utf-8-sig") as stream:
            writer = csv.writer(stream)

            if self.summary_check.isChecked():
                writer.writerow(["SUMMARY RESULTS"])
                writer.writerow(["Metric", "Value"])
                writer.writerow(["Integral", f"{result.integral:.12g}"])
                writer.writerow(["Algebraic degree", result.degree])
                writer.writerow(["Quadrature points", len(result.weights)])
                writer.writerow(["Computation time (ms)", f"{result.computation_time_s * 1000:.3f}"])
                writer.writerow(["Volume", f"{float(result.weights.sum()):.12g}"])
                writer.writerow(["Negative weights", int((result.weights < 0).sum())])
                writer.writerow(["Positive weights", int((result.weights > 0).sum())])
                if self.exact_value is not None:
                    error = abs(result.integral - self.exact_value)
                    writer.writerow(["Absolute error", f"{error:.12g}"])
                writer.writerow([])

            if self.mesh_check.isChecked():
                writer.writerow(["MESH INFORMATION"])
                writer.writerow(["Item", "Value"])
                writer.writerow(["Vertex file", result.mesh.vertex_file])
                writer.writerow(["Face file", result.mesh.face_file])
                writer.writerow(["Vertices", result.n_vertices])
                writer.writerow(["Faces", result.n_faces])
                writer.writerow([])

            if self.nodes_check.isChecked():
                writer.writerow(["QUADRATURE NODES AND WEIGHTS"])
                writer.writerow(["Index", "X", "Y", "Z", "Weight"])
                for index, (node, weight) in enumerate(zip(result.nodes, result.weights), start=1):
                    writer.writerow([index, f"{node[0]:.16g}", f"{node[1]:.16g}", f"{node[2]:.16g}", f"{weight:.16g}"])

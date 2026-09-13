"""
Tema visivo dell'applicazione.

Palette "scientific workstation": grigio-blu neutro di fondo, primario blu
petrolio profondo (non il solito blu-Bootstrap), accento ambra riservato
SOLO alle azioni davvero primarie (Compute), tipografia con gerarchia
chiara (titoli/etichette/valori), card con bordo sottile per dare
profondità senza sembrare "flat design" generico.
"""

# ---------------------------------------------------------------------------
# Palette (unica fonte di verità: se cambi un colore qui, cambia ovunque)
# ---------------------------------------------------------------------------
COLOR_BG = "#eef1f5"
COLOR_BG_ALT = "#e4e8ee"
COLOR_SURFACE = "#ffffff"
COLOR_SURFACE_ALT = "#f6f8fa"
COLOR_BORDER = "#dde2e9"
COLOR_BORDER_STRONG = "#c7ced9"

COLOR_TEXT = "#111111"
COLOR_TEXT_MUTED = "#111111"
COLOR_TEXT_FAINT = "#111111"

COLOR_PRIMARY = "#0b3d5c"        # blu petrolio profondo (header, brand)
COLOR_PRIMARY_DARK = "#082c43"
COLOR_ACCENT = "#e08e2c"         # ambra: riservato al pulsante Compute
COLOR_ACCENT_DARK = "#c67a1e"
COLOR_BUTTON_BG = "#bfe9ff"
COLOR_BUTTON_BG_HOVER = "#a9def8"
COLOR_BUTTON_TEXT = "#073b5c"

COLOR_TEAL = "#0f766e"           # azioni secondarie / evidenze di stato
COLOR_TEAL_SOFT = "#e6f3f1"

COLOR_SUCCESS = "#1c8a4b"
COLOR_SUCCESS_SOFT = "#e6f6ec"
COLOR_ERROR = "#c23b3b"
COLOR_ERROR_SOFT = "#fdecec"
COLOR_BUSY = "#0b6ea8"
COLOR_BUSY_SOFT = "#e7f1fa"

RADIUS = "10px"
RADIUS_SM = "6px"

STYLESHEET = f"""
* {{
    outline: none;
}}

QWidget {{
    background-color: transparent;
    color: {COLOR_TEXT};
    font-family: "Inter", "SF Pro Text", "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}}

QMainWindow {{
    background-color: {COLOR_BG};
}}

QToolTip {{
    background-color: {COLOR_SURFACE};
    color: {COLOR_TEXT};
    border: 1px solid {COLOR_PRIMARY};
    border-radius: 4px;
    padding: 6px 8px;
    font-size: 12px;
}}

/* Header */
#HeaderBar {{
    background-color: {COLOR_SURFACE};
    border-bottom: 1px solid {COLOR_BORDER};
}}

#HeaderTitle {{
    color: {COLOR_TEXT};
    font-size: 19px;
    font-weight: 700;
    letter-spacing: 0.2px;
}}

#HeaderIcon {{
    background-color: transparent;
}}

#HeaderSubtitle {{
    color: {COLOR_TEXT};
    font-size: 11.5px;
    font-weight: 500;
    letter-spacing: 0.3px;
}}

#HeaderBadge {{
    color: {COLOR_TEXT};
    background-color: {COLOR_SURFACE_ALT};
    border: 1px solid {COLOR_BORDER_STRONG};
    border-radius: 10px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 700;
}}

#HeaderBadge[state="ready"] {{
    color: {COLOR_TEXT};
    background-color: {COLOR_SUCCESS_SOFT};
    border-color: #bfe4cd;
}}

#HeaderBadge[state="missing"] {{
    color: {COLOR_TEXT};
    background-color: {COLOR_ERROR_SOFT};
    border-color: #f3c3c3;
}}

QPushButton#HeaderButton {{
    color: {COLOR_BUTTON_TEXT};
    background-color: {COLOR_BUTTON_BG};
    border: 1px solid #8cc9e8;
    border-radius: {RADIUS_SM};
    padding: 7px 14px;
    font-weight: 600;
}}

QPushButton#HeaderButton:hover {{
    background-color: {COLOR_BUTTON_BG_HOVER};
    border-color: {COLOR_PRIMARY};
}}

QPushButton#HeaderButton:pressed {{
    background-color: #8fcce9;
}}

/* Card (QGroupBox) */
QGroupBox {{
    background-color: transparent;
    border: 1px solid {COLOR_BORDER};
    border-radius: {RADIUS};
    margin-top: 20px;
    padding: 15px 13px 13px 13px;
    font-weight: 700;
    font-size: 12px;
    color: {COLOR_TEXT_MUTED};
    letter-spacing: 0.4px;
    text-transform: uppercase;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    top: 5px;
    padding: 0 6px;
    color: {COLOR_TEXT};
    background-color: transparent;
}}

QLabel {{
    background-color: transparent;
    color: {COLOR_TEXT};
    font-weight: 500;
    text-transform: none;
    letter-spacing: normal;
}}

QLabel#FunctionMathLabel {{
    color: {COLOR_PRIMARY};
    font-family: "Cambria Math", "STIX Two Math", Georgia, serif;
    font-size: 17px;
    font-style: italic;
    font-weight: 600;
    padding: 1px 0;
}}

QLabel[role="hint"] {{
    color: {COLOR_TEXT_FAINT};
    font-size: 11px;
    font-weight: 400;
}}

QLabel[role="info"] {{
    color: {COLOR_TEXT};
    background-color: {COLOR_TEAL_SOFT};
    border-left: 3px solid {COLOR_TEAL};
    border-radius: 4px;
    padding: 7px 10px;
    font-size: 11.5px;
    font-weight: 500;
    font-style: normal;
    text-transform: none;
    letter-spacing: normal;
}}

/* Campi di input */
QLineEdit, QSpinBox {{
    background-color: transparent;
    border: 1px solid {COLOR_BORDER_STRONG};
    border-radius: {RADIUS_SM};
    padding: 7px 9px;
    color: {COLOR_TEXT};
    selection-background-color: {COLOR_TEAL};
    selection-color: {COLOR_TEXT};
}}

QLineEdit:hover, QSpinBox:hover {{
    border-color: {COLOR_TEAL};
}}

QLineEdit:focus, QSpinBox:focus {{
    border: 1.5px solid {COLOR_TEAL};
    background-color: transparent;
}}

QSpinBox::up-button, QSpinBox::down-button {{
    width: 16px;
    border: none;
    background: transparent;
}}

/* Pulsanti */
QPushButton {{
    background-color: {COLOR_BUTTON_BG};
    border: 1px solid #8cc9e8;
    border-radius: {RADIUS_SM};
    padding: 7px 13px;
    min-height: 18px;
    font-weight: 600;
    color: {COLOR_BUTTON_TEXT};
}}

QPushButton:hover {{
    background-color: {COLOR_BUTTON_BG_HOVER};
    border-color: {COLOR_PRIMARY};
}}

QPushButton:pressed {{
    background-color: #8fcce9;
}}

QPushButton#SecondaryButton {{
    color: {COLOR_BUTTON_TEXT};
    background-color: {COLOR_BUTTON_BG};
    border: 1px solid #8cc9e8;
    padding: 6px 11px;
}}

QPushButton#SecondaryButton:hover {{
    background-color: {COLOR_BUTTON_BG_HOVER};
    border-color: {COLOR_PRIMARY};
}}

QPushButton#SecondaryButton:pressed {{
    background-color: #8fcce9;
}}

/* Pulsante primario: unico elemento con l'accento ambra, per farlo
   risaltare senza ambiguita' su cosa fare per lanciare il calcolo. */
QPushButton#ComputeButton {{
    background-color: {COLOR_BUTTON_BG};
    border: 1px solid #8cc9e8;
    color: {COLOR_BUTTON_TEXT};
    font-weight: 800;
    font-size: 14px;
    letter-spacing: 0.3px;
    padding: 13px 16px;
    border-radius: {RADIUS};
}}

QPushButton#ComputeButton:hover {{
    background-color: {COLOR_BUTTON_BG_HOVER};
}}

QPushButton#ComputeButton:pressed {{
    background-color: #8fcce9;
}}

QPushButton#ComputeButton:disabled {{
    background-color: #d4eaf4;
    border-color: #a7cadb;
    color: #6b8796;
}}

/* Checkbox / Slider */
QCheckBox {{
    spacing: 9px;
    font-weight: 500;
    background-color: transparent;
}}

QCheckBox::indicator {{
    width: 17px;
    height: 17px;
}}

QCheckBox::indicator:unchecked {{
    background: {COLOR_SURFACE};
    border: 1.5px solid {COLOR_BORDER_STRONG};
    border-radius: 5px;
}}

QCheckBox::indicator:unchecked:hover {{
    border-color: #69bde5;
}}

QCheckBox::indicator:checked {{
    background: {COLOR_BUTTON_BG};
    border: 1.5px solid #69bde5;
    border-radius: 5px;
}}

QSlider {{
    min-height: 22px;
    background-color: transparent;
}}

QSlider::groove:horizontal {{
    height: 4px;
    background: {COLOR_BORDER_STRONG};
    border-radius: 2px;
}}

QSlider::sub-page:horizontal {{
    background: #69bde5;
    border-radius: 2px;
}}

QSlider::handle:horizontal {{
    width: 15px;
    height: 15px;
    margin: -6px 0;
    background: {COLOR_SURFACE};
    border: 2.5px solid #69bde5;
    border-radius: 8px;
}}

QSlider::handle:horizontal:hover {{
    border-color: #2b9fd0;
}}

/* Barra risultati */
QFrame#ResultsBar {{
    background-color: transparent;
    border-top: none;
}}

QScrollArea#InputScrollArea, QScrollArea#ResultsScrollArea {{
    background-color: transparent;
    border: none;
}}

QWidget[role="metricContainer"] {{
    background-color: transparent;
}}

QLabel#ResultsTitle {{
    color: {COLOR_TEXT};
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.4px;
}}

QFrame#MetricDivider {{
    background-color: {COLOR_BORDER};
    max-width: 1px;
    min-width: 1px;
}}

QLabel[role="metricValue"] {{
    font-size: 15px;
    font-weight: 800;
    color: {COLOR_TEXT};
    font-family: "SF Mono", "JetBrains Mono", "Consolas", monospace;
}}

QLabel[role="metricLabel"] {{
    font-size: 9px;
    font-weight: 700;
    color: {COLOR_TEXT};
    letter-spacing: 0.6px;
    text-transform: uppercase;
}}

/* Stato / messaggi */
QLabel#StatusLabel {{
    padding: 3px 2px;
    background-color: transparent;
    border: none;
    color: {COLOR_TEXT};
    font-weight: 500;
}}

QLabel#StatusLabel[role="statusOk"] {{
    background-color: transparent;
    border: none;
    color: {COLOR_SUCCESS};
    font-weight: 700;
}}

QLabel#StatusLabel[role="statusError"] {{
    background-color: transparent;
    border: none;
    color: {COLOR_ERROR};
    font-weight: 700;
}}

QLabel#StatusLabel[role="statusBusy"] {{
    background-color: transparent;
    border: none;
    color: {COLOR_BUSY};
    font-weight: 700;
}}

/* Varie */
QSplitter::handle {{
    background-color: {COLOR_BG_ALT};
}}

QSplitter::handle:hover {{
    background-color: {COLOR_BORDER_STRONG};
}}

QScrollBar:vertical {{
    background: #e7eaee;
    width: 9px;
    margin: 1px;
}}

QScrollBar::handle:vertical {{
    background: #aeb8c4;
    border-radius: 4px;
    min-height: 24px;
}}

QScrollBar::handle:vertical:hover {{
    background: #7f8d9b;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background: #e7eaee;
    height: 9px;
    margin: 1px;
}}

QScrollBar::handle:horizontal {{
    background: #aeb8c4;
    border-radius: 4px;
    min-width: 28px;
}}

QScrollBar::handle:horizontal:hover {{
    background: #7f8d9b;
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

QMessageBox {{
    background-color: {COLOR_SURFACE};
}}
"""

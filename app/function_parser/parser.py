"""
Parsing sicuro di f(x, y, z) inserita dall'utente.

Non viene MAI usato eval() sull'input utente. Il parsing passa attraverso
sympy.parsing.sympy_parser.parse_expr con:
  - un dizionario di simboli/funzioni consentiti esplicitamente (whitelist),
  - transformations limitate (nessuna auto-esecuzione di codice arbitrario),
  - lambdify verso NumPy per la valutazione vettorizzata sui nodi di quadratura.

Sintassi accettata: notazione "matematica" con '^' per la potenza, e un
piccolo preprocessing per accettare comandi LaTeX molto comuni (\\sin, \\cos,
\\exp, ...).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
import sympy
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    standard_transformations,
    parse_expr,
)

x, y, z = sympy.symbols("x y z", real=True)

# Whitelist esplicita di nomi consentiti nell'espressione. Nessun altro
# simbolo/nome verra' risolto (sympy_parser con local_dict + global_dict
# vuoto evita che vengano risolti builtin arbitrari).
_ALLOWED_LOCALS: dict[str, object] = {
    "x": x,
    "y": y,
    "z": z,
    "pi": sympy.pi,
    "e": sympy.E,
    "sin": sympy.sin,
    "cos": sympy.cos,
    "tan": sympy.tan,
    "asin": sympy.asin,
    "acos": sympy.acos,
    "atan": sympy.atan,
    "sinh": sympy.sinh,
    "cosh": sympy.cosh,
    "tanh": sympy.tanh,
    "exp": sympy.exp,
    "log": sympy.log,
    "ln": sympy.log,
    "sqrt": sympy.sqrt,
    "Abs": sympy.Abs,
    "abs": sympy.Abs,
}

_TRANSFORMATIONS = standard_transformations + (convert_xor, implicit_multiplication_application)

# Alcuni comandi LaTeX molto comuni scritti "a mano" (\sin, \cos, \exp, \sqrt, \pi)
_LATEX_REPLACEMENTS = {
    r"\sin": "sin",
    r"\cos": "cos",
    r"\tan": "tan",
    r"\exp": "exp",
    r"\sqrt": "sqrt",
    r"\ln": "ln",
    r"\log": "log",
    r"\pi": "pi",
    r"\cdot": "*",
    r"\left": "",
    r"\right": "",
}


class FunctionParseError(Exception):
    """L'espressione inserita non e' una funzione valida di x, y, z."""


def _preprocess(text: str) -> str:
    cleaned = text.strip()
    for latex_cmd, replacement in _LATEX_REPLACEMENTS.items():
        cleaned = cleaned.replace(latex_cmd, replacement)
    # '^' -> potenza (gestito anche da convert_xor, ma normalizziamo comunque)
    return cleaned


@dataclass
class ParsedFunction:
    expression_text: str
    sympy_expr: sympy.Expr
    numeric_func: Callable[[np.ndarray, np.ndarray, np.ndarray], np.ndarray]

    def evaluate(self, nodes: np.ndarray) -> np.ndarray:
        """nodes: array (N, 3) -> valori f(x_i, y_i, z_i), array (N,)."""
        xs, ys, zs = nodes[:, 0], nodes[:, 1], nodes[:, 2]
        values = self.numeric_func(xs, ys, zs)
        values = np.asarray(values, dtype=np.float64)
        if values.shape != (nodes.shape[0],):
            # Espressione costante (es. "1"): numeric_func puo' restituire uno
            # scalare; lo estendiamo a tutti i nodi.
            values = np.full(nodes.shape[0], float(values), dtype=np.float64)
        return values


def parse_function(text: str) -> ParsedFunction:
    if not text or not text.strip():
        raise FunctionParseError("Il campo della funzione integranda e' vuoto.")

    cleaned = _preprocess(text)

    # Rifiuta esplicitamente caratteri sospetti (doppio underscore, import, ecc.)
    # anche se sympy_parser con dizionari vuoti e' gia' di per se' al sicuro:
    # e' una difesa in profondita' a costo quasi nullo.
    forbidden_patterns = ["__", "import", "os.", "sys.", "eval", "exec", "open("]
    lowered = cleaned.lower()
    for pat in forbidden_patterns:
        if pat in lowered:
            raise FunctionParseError(f"Espressione non consentita (contiene '{pat}').")

    try:
        # global_dict=None fa si' che sympy usi il proprio namespace interno
        # minimale (necessario per token come Integer/Symbol generati dalle
        # transformations), SENZA alcun accesso ai builtin di Python
        # (sympy imposta comunque __builtins__: {} internamente). Il
        # controllo sui free_symbols subito sotto e' la vera whitelist:
        # qualunque nome non in {x, y, z} + funzioni note viene rifiutato.
        expr = parse_expr(
            cleaned,
            local_dict=_ALLOWED_LOCALS,
            global_dict=None,
            transformations=_TRANSFORMATIONS,
            evaluate=True,
        )
    except (sympy.SympifyError, SyntaxError, TypeError, AttributeError) as exc:
        raise FunctionParseError(f"Espressione non valida: {text}") from exc

    free_symbols = expr.free_symbols
    allowed_symbols = {x, y, z}
    extra = free_symbols - allowed_symbols
    if extra:
        names = ", ".join(sorted(str(s) for s in extra))
        raise FunctionParseError(
            f"La funzione contiene simboli non riconosciuti: {names}. "
            "Sono ammesse solo le variabili x, y, z."
        )

    try:
        numeric_func = sympy.lambdify((x, y, z), expr, modules=["numpy"])
    except Exception as exc:  # pragma: no cover - lambdify puo' fallire in vari modi
        raise FunctionParseError(f"Impossibile valutare numericamente l'espressione: {text}") from exc

    return ParsedFunction(expression_text=text, sympy_expr=expr, numeric_func=numeric_func)

#!/bin/zsh

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

export PYTHONPYCACHEPREFIX="$PROJECT_ROOT/.cache/pyc"

cd "$PROJECT_ROOT"

python3 -m app
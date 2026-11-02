#!/usr/bin/env bash
# Starts the Streamlit app on THIS computer only (for checking your work).
# It installs nothing, and never runs git or publishes anything.
# Usage:  bash run_app.sh      (stop it with Ctrl+C)

set -e

# Always work from the folder this script lives in.
cd "$(dirname "$0")"

# Prerequisite: the app file must be here.
if [ ! -f streamlit_app.py ]; then
  echo "Error: streamlit_app.py not found in $(pwd). Run this script from the project folder." >&2
  exit 1
fi

# Use the project's environment: .venv/bin/python (Mac/Linux/WSL) or .venv/Scripts/python.exe (Windows),
# falling back to the active python.
if [ -x .venv/bin/python ]; then
  PY=.venv/bin/python
elif [ -x .venv/Scripts/python.exe ]; then
  PY=.venv/Scripts/python.exe
elif command -v python >/dev/null 2>&1; then
  PY=python
  echo "Note: no .venv found, using the active python."
else
  echo "Error: no Python found. Create the environment first (uv venv, then uv pip install -r requirements.txt)." >&2
  exit 1
fi

# Prerequisite: streamlit must be installed in that Python.
if ! "$PY" -c "import streamlit" >/dev/null 2>&1; then
  echo "Error: streamlit is not installed for $PY." >&2
  echo "Fix: uv pip install --python $PY -r requirements.txt" >&2
  exit 1
fi

PORT=8501
echo "Starting the app. Open this address in your browser: http://localhost:$PORT"
echo "Press Ctrl+C to stop it."
exec "$PY" -m streamlit run streamlit_app.py --server.port "$PORT" --server.headless true

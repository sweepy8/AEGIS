#!/bin/bash
# aegis_launcher.sh

VENV_PATH="venv/bin/activate"
PROGRAM_NAME="aegis_launcher.sh"
SCRIPT_NAME="aegis.py"

echo "[INIT] ${PROGRAM_NAME}: Activating python virtual environment..."
source "${VENV_PATH}"

echo "[INIT] ${PROGRAM_NAME}: Launching main script (${SCRIPT_NAME})..."
python3 -u "${SCRIPT_NAME}"

echo "[EXIT] ${PROGRAM_NAME}: Deactivating python virtual environment..."
deactivate
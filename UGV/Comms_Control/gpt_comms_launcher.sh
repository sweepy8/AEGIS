#!/bin/bash
# comms_launcher_v3.sh
# A robust script that finds the repo root to activate the correct venv.

# This line finds the directory the script itself is in.
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# This assumes the script is in AEGIS/UGV/Comms_Control
# and navigates up to the repository's root directory.
REPO_ROOT="${SCRIPT_DIR}/../../"

# --- Configuration using paths relative to the repo root ---
DRIVER_DIR="${REPO_ROOT}/UGV/Comms_Control"
PYTHON_SCRIPT="UART_comms_driver.py"
VENV_PATH="${REPO_ROOT}/venv/bin/activate"
CONTROLLER_DEVICE="/dev/input/js0"

# --- Main Loop ---
while true; do
    echo "gpt_comms_launcher.sh: Waiting for controller device at ${CONTROLLER_DEVICE}..."

    while [ ! -c "${CONTROLLER_DEVICE}" ]; do
        sleep 1
    done

    echo "gpt_comms_launcher.sh: Controller detected! Launching comms driver..."

    # Activate the virtual environment FROM THE ROOT
    source "${VENV_PATH}"

    # Change to the script's directory before running it
    cd "${DRIVER_DIR}"
    python3 -u "${PYTHON_SCRIPT}"
    
    # Deactivate the virtual environment when the script exits
    deactivate

    echo "gpt_comms_launcher.sh: Driver has stopped. Returning to wait loop."
    sleep 1
done
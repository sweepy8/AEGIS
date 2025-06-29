#!/bin/bash
# aegis_launcher.sh

CONTROLLER_DEVICE="/dev/input/js0"
VENV_PATH="venv/bin/activate"
PROGRAM_NAME="aegis_launcher.sh"
SCRIPT_NAME="aegis.py"

while true; do
    echo "${PROGRAM_NAME}: Waiting for controller device at ${CONTROLLER_DEVICE}..."

    # While no character device is located at the controller device path
    while [ ! -c "${CONTROLLER_DEVICE}" ]; do
        sleep 1
    done

    echo "${PROGRAM_NAME}: Controller detected! Launching comms driver..."

    source "${VENV_PATH}"
    python3 -u "${SCRIPT_NAME}"
    # Deactivate the virtual environment when the script exits
    deactivate

    echo "${PROGRAM_NAME}: Driver has stopped. Returning to wait loop."
    sleep 1
done
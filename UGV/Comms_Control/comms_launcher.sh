#!/bin/bash
# comms_launcher.sh
# Check for a connected XBOX controller every second
# Once found, run the UART_comms_driver.py file

echo "Waiting for XBOX controller..."
# Wait forever for the controller
while true; do
	if grep -q "Microsoft Xbox Controller" /proc/bus/input/devices; then
		echo "Controller detected! Launching comms driver..."
		break
	fi
	sleep 1
done

# Once the controller is found, run the comms driver
cd /
cd /home/aegis/Documents/AEGIS_local_repo/AEGIS/UGV/Comms_Control
. venv/bin/activate
python3 UART_comms_driver.py
cd /

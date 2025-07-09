# Main program for AEGIS rover software.

# Runs the following subsystems:
#   - UART Piloting  (Raspberry Pi Tx --> Arduino Rx)
#   - UART Telemetry (Raspberry Pi Rx <-- Arduino Tx)
#   - LiDAR Scanning
#   - Flask webserver to stream trip info / live feed
# There are four available processes for the four-core Pi 5.

from multiprocessing import Process
from time import sleep

from ugv import rpi_UART
from stream import web_viewer

from ugv.camera import UGV_Cam

ser = rpi_UART.open_serial_connection()

control_p = Process(target=rpi_UART.control_UGV, args=[ser], daemon=True)
telemetry_p = Process(target=rpi_UART.listen_to_UGV, args=[ser], daemon=True)
web_p = Process(target=web_viewer.run_stream, daemon=True)

print("aegis.py: Starting UART subprocesses...")
control_p.start()
telemetry_p.start()

print("aegis.py: Starting web subprocess...")
web_p.start()

# Test sequence goes here
print("Running test sequence (PLACEHOLDER)...")
sleep(1)

print("aegis.py: Entering infinite pass loop...")
while True: pass



'''
I need to import the ugv and stream files without calling their functions, but I need to provide multiple functions in the stream file with the camera object. So,
I can't pass the camera object to the subprocesses, I must pass the camera object to the stream file before creating the subprocess


'''
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

uart_p = Process(target=rpi_UART.run_comms, daemon=True)
web_p = Process(target=web_viewer.run_stream, daemon=True)

print("[INIT] aegis.py: Starting UART subprocess...")
uart_p.start()

print("[INIT] aegis.py: Starting web subprocess...")
web_p.start()

# Test sequence goes here
#print("[INIT] aegis.py: Running test sequence (PLACEHOLDER)...")
#sleep(1)

print("[RUNTIME] aegis.py: Entering infinite pass loop...")

while True:
    pass
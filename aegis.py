# Main program for AEGIS rover software.

# Runs the following subsystems:
#   - UART Piloting  (Raspberry Pi Tx --> Arduino Rx)
#   - UART Telemetry (Raspberry Pi Rx <-- Arduino Tx)
#   - LiDAR Scanning   TODO, NOT CURRENTLY IMPLEMENTED
# There are four available processes for the four-core Pi 5.

from multiprocessing import Process

from ugv import UART

uart_p = Process(target=UART.run_comms)

print("[INIT] aegis.py: Starting UART subprocess...")
uart_p.start()

print("[RUNTIME] aegis.py: Entering infinite pass loop...")

while True:
    pass
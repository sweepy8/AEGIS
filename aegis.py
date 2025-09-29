# Main program for AEGIS rover software.

# Runs the following:
#   - UART process:
#       - UART Piloting  (Raspberry Pi Tx --> Arduino Rx)
#       - UART Telemetry (Raspberry Pi Rx <-- Arduino Tx)
#       - LiDAR Scanning
#       - Camera Capture
#   - Website process:
#       - Flask App
# There are four available single-core processes for the four-core Pi 5.

from multiprocessing import Process

from rover import UART
from stream import web_viewer as site

from utils.led_utils import *
set_pixel(RPI_ADDR, PX_WHITE)

# UART.run_comms()

uart_p = Process(target=UART.run_comms)
site_p = Process(target=site.app.run)

print("[INI] aegis.py: Starting UART subprocess...")
uart_p.start()
print("[INI] aegis.py: Starting website subprocess...")
site_p.start()

print("[INI] aegis.py: Joining subprocesses...")
uart_p.join()
site_p.join()
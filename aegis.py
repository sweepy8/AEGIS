# Main program for AEGIS rover software.

# Runs the following:
#   - UART process:
#       - UART Piloting  (Raspberry Pi Tx --> Arduino Rx)
#       - UART Telemetry (Raspberry Pi Rx <-- Arduino Tx)
#       - LiDAR Scanning
#   - Website process:
#       - Flask App
# There are four available processes for the four-core Pi 5.

from multiprocessing import Process

from rover import UART
#from stream import web_viewer as site

uart_p = Process(target=UART.run_comms, daemon=True)
#site_p = Process(target=site.app.run, daemon=True)

print("[INIT] aegis.py: Starting UART subprocess...")
uart_p.start()
#print("[INIT] aegis.py: Starting website subprocess...")
#site_p.start()

print("[INIT] aegis.py: Joining subprocesses...")
uart_p.join()
#https://drive.google.com/open?id=1TUVprfRzkkHPPvPksthNq0Caji99S2wj1HYw8TPtyhM&usp=drive_copysite_p.join()
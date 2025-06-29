from threading import Thread
from ugv import rpi_UART
from stream import web_viewer

controller_thread = Thread(target=rpi_UART.main, daemon=True)
web_thread = Thread(target=web_viewer.run_stream, daemon=True)

print("aegis.py: Starting UART thread...")
controller_thread.start()
print("aegis.py: Starting webserver thread...")
web_thread.start()
print("aegis.py: Joining threads into main program...")
controller_thread.join()
web_thread.join()
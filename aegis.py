from threading import Thread
from UGV.Comms_Control import UART_comms_driver as comms_driver
from stream import web_viewer as web_app

print("Creating UART communication thread:")
controller_thread = Thread(target=comms_driver.main, daemon=True)
print("Creating webserver thread")
web_thread = Thread(target=web_app.main, daemon=True)

print("Starting UART communication thread:")
controller_thread.start()
print("Starting webserver thread")
web_thread.start()

controller_thread.join()
web_thread.join()
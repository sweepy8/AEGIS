# Raspberry Pi to Arduino Communication Driver
# AEGIS Senior Design, Created on 5/23/2025
# Designed for Arduino MEGA and R.Pi 5
# Uses RP1 chip's uart2 on GPIO4/5 (pins 7/29 (TX/RX))



# PROBLEMS:
# I think that the use of asyncio is a problem in controller.py. I think it prevents
# reception of data unless a nonzero event is detected by the controller.
# This would be fixed by splitting the controller and the reception into two additional threads.
# Then, aegis.py would spin together web_viewer, rpi_UART, and controller, which makes sense.

from time import sleep, time
from serial import Serial
from threading import Thread

from ugv import controller

LISTEN_TO_UGV = 1
INPUT_BUFFER_SECONDS = 0.1
STICK_MOVE_THRESHOLD = 0.05         # Fixes stick drift lol

def generate_command(op : str, **kwargs) -> list[int]:

    # See table in docs for 3-byte command structure
    command = [-1, -1, -1]
    

    if op == "TURN":
        command[0] = 128	#1000_0000, opcode 10
        
        for key, val in kwargs.items():
            if key == "turn_dir" and val == "RIGHT":
                command[0] += 1
            elif key == "turn_dir" and val == "LEFT":
                pass    # add zero to command[0]? This is only here for readability

        command[1] = 255	# Max speed turn on shoulder buttons
        command[2] = 1
            
    if op == "MOVE":
        command[0] = 192	#1100_0000, opcode 11
        
        for key, val in kwargs.items():
            if key == "joy_pos":
                command[0] += (val < 0)	            # Sets direction (bit 0) to sign of joystick position
                command[1] = int(abs(val) * 255)

        command[2] = 1
    
    return command


def open_serial_connection() -> Serial:
    
    s = Serial()		# Create serial connection
    s.port = '/dev/ttyAMA2'	# UART port on GPIO 4 and 5
    s.baudrate = 115200		# 9600 bps Baud
    s.bytesize = 8			# 8 bits per byte
    s.parity = 'N'			# No parity bit
    #s.stopbits = 0			# One stop bit per byte
    s.timeout = 0			# Non-blocking mode (return immediately)

    # Open configured serial connection
    s.open()
    print(f"rpi_UART.py: Opening serial port at {s.name}...")

    # Allow connection to form
    sleep(0.05)   
    return s

    
def read_data(serial_conn : Serial) -> bytearray :
    if serial_conn.is_open:
        if bytes := serial_conn.in_waiting > 0:
            data = serial_conn.read(bytes)
            return data
        else:
            pass
    else:
        #print("Serial connection is not open!")
        return bytearray([0])


def main():
    
    xb_listener_thread = Thread(target=controller.listen, daemon=True)

    serial_conn = open_serial_connection()
    xb_listener_thread.start()

    time_since_last_command = time()

    while True:

        if LISTEN_TO_UGV:
            ugv_data = read_data(serial_conn)
            if ugv_data is not None:
                for b in ugv_data:
                    print(chr(b), end='')
                    if chr(b) == '\n':
                        print("rpi_UART.py: UGV says ", end='')
        
        
        current_time = time()

        if (current_time - time_since_last_command) > INPUT_BUFFER_SECONDS:

            if (controller.input_states['BTN_A'] == 1):# and (previous_input_states['BTN_A'] == 0):
                serial_conn.write(bytearray([1,1,1]))
            
            if (abs(controller.input_states['ABS_Y']) > STICK_MOVE_THRESHOLD):
                move_command = generate_command("MOVE", joy_pos=controller.input_states['ABS_Y'])
                serial_conn.write(move_command)

            if (controller.input_states['BTN_TL'] == 1):
                serial_conn.write(generate_command("TURN", turn_dir="LEFT"))

            if (controller.input_states['BTN_TR'] == 1):
                serial_conn.write(generate_command("TURN", turn_dir="RIGHT"))

            time_since_last_command = current_time

if __name__ == "__main__":
    main()
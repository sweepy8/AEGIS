# Raspberry Pi to Arduino Communication Driver
# AEGIS Senior Design, 5/23/2025
# Designed for Arduino MEGA and R.Pi 5
# Uses RP1 chip's uart2 on GPIO4/5 (pins 7/29 (TX/RX))

import serial
import time
import xbox_controller_driver as xb	#XboxController(), .read()

LISTEN_TO_UGV = 1

def generate_command(op : str, **kwargs) -> list[int]:

    command = [-1, -1, -1]
    
    if op == "SEND_DATA":
        command[0] = 0		#0000_0000, opcode 00
        
        for key, val in kwargs.items():
            if key == "data":
                pass				#THIS IS WHERE DATA TABLE WOULD BE
                                    # Something like "command[0] += val", map val str to int?
            else:
                print(f"Invalid argument! \"{key}\" with value \"{val}\"")
    
    if op == "TURN":
        command[0] = 128	#1000_0000, opcode 10
        
        for key, val in kwargs.items():
            if key == "turn_dir":
                if val == "LEFT":
                    pass
                elif val == "RIGHT":
                    command[0] += 1
                else:
                    print(f"Invalid direction \"{val}\"!")
            else:
                print(f"Invalid argument! \"{key}\" with value \"{val}\"")
                
        command[1] = 255	# Max speed turn on shoulder buttons
        command[2] = 1
            
    if op == "MOVE":
        command[0] = 192	#1100_0000, opcode 11
        
        for key, val in kwargs.items():
            if key == "joy_pos":
                command[0] += (val < 0)	#Sets direction (bit 0) to sign of joystick position
                command[1] = abs(val) % 256	# Sets byte 2 to speed [0,255]
            else:
                print(f"Invalid argument! \"{key}\" with value \"{val}\"")

        command[2] = 1		# Set duration. 50ms increments
    
    return command


def open_serial_connection() -> serial.Serial:
    
    s = serial.Serial()		# Create serial connection
    s.port = '/dev/ttyAMA2'	# UART port on GPIO 4 and 5
    s.baudrate = 115200		# 9600 bps Baud
    s.bytesize = 8			# 8 bits per byte
    s.parity = 'N'			# No parity bit
    #s.stopbits = 0			# One stop bit per byte
    s.timeout = 0			# Non-blocking mode (return immediately)

    # Open configured serial connection
    s.open()
    print(f"Opening serial port: {s.name}...")

    # Allow connection to form
    time.sleep(0.05)   
    return s

    
def read_data(serial_conn : serial.Serial) -> bytearray :
    if serial_conn.is_open:
        if bytes := serial_conn.in_waiting > 0:
            data = serial_conn.read(bytes)
            return data
        else:
            pass
    else:
        print("Serial connection is not open!")
        return bytearray([0])



def main():
    
    serial_conn = open_serial_connection()
    xbone = xb.XboxController()
    NUM_INPUTS = 7			    # Update this if more inputs are tracked by .read()
    PRESS_DELAY = 0.500			# Delay between repeated presses in seconds
    JOY_DELAY = 0.100       	# Delay between joystick value reads in seconds

    # Looping test using xbox controller
    activation_time = [0 for i in range(NUM_INPUTS)]
    last_move_time = time.time()

    while True:

        if LISTEN_TO_UGV:
            ugv_data = read_data(serial_conn)
            if ugv_data is not None:
                for b in ugv_data:
                    print(chr(b), end='')
                    if chr(b) == '\n':
                        print("UGV says: ", end='')

        xb_data = xbone.read()

        # A BUTTON MAPPING
        if (xb_data[0]) & (activation_time[0] == 0):	# A button is pressed
            serial_conn.write(bytearray([1,1,1]))
            activation_time[0] = time.time()
        elif ((time.time() - activation_time[0]) > PRESS_DELAY) & (xb_data[0] == 0):	#A button is released
            activation_time[0] = 0
            
        # B BUTTON MAPPING
        if (xb_data[1]) & (activation_time[1] == 0):	# B button is pressed
            serial_conn.write(bytearray([2,2,2]))
            activation_time[1] = time.time()
        elif ((time.time() - activation_time[1]) > PRESS_DELAY) & (xb_data[1] == 0):	#B button is released
            activation_time[1] = 0
        
        # Y BUTTON MAPPING
        if (xb_data[2]) & (activation_time[2] == 0):	# Y button is pressed
            serial_conn.write(bytearray([3,3,3]))
            activation_time[2] = time.time()
        elif ((time.time() - activation_time[2]) > PRESS_DELAY) & (xb_data[2] == 0):	#Y button is released
            activation_time[2] = 0
            
        # X BUTTON MAPPING
        if (xb_data[3]) & (activation_time[3] == 0):	# X button is pressed
            serial_conn.write(bytearray([4,4,4]))
            activation_time[3] = time.time()
        elif ((time.time() - activation_time[3]) > PRESS_DELAY) & (xb_data[3] == 0):	#X button is released
            activation_time[3] = 0
        
        # LEFT JOYSTICK Y AXIS MAPPING
        if (xb_data[4]) & (last_move_time == 0):	# Left joystick is moved along Y axis
            serial_conn.write(generate_command("MOVE", joy_pos=xb_data[4]))
            last_move_time = time.time()
        elif ((time.time() - last_move_time) > JOY_DELAY):	# Preset time has passed, new sample can be taken
            last_move_time = 0
        
        # LEFT BUMPER MAPPING
        if (xb_data[5]) & (last_move_time == 0):	# Left shoulder button is pressed
            serial_conn.write(generate_command("TURN", turn_dir="LEFT"))
            last_move_time = time.time()
        elif ((time.time() - last_move_time) > JOY_DELAY):	# Preset time has passed, new sample can be taken
            last_move_time = 0

        # RIGHT BUMPER MAPPING
        if (xb_data[6]) & (last_move_time == 0):	# Right shoulder button is pressed
            serial_conn.write(generate_command("TURN", turn_dir="RIGHT"))
            last_move_time = time.time()
        elif ((time.time() - last_move_time) > JOY_DELAY):	# Preset time has passed, new sample can be taken
            last_move_time = 0


if __name__ == "__main__":
    main()

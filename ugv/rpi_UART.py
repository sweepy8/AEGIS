# Raspberry Pi to Arduino Communication Driver
# AEGIS Senior Design, Created on 5/23/2025
# Designed for Arduino MEGA and R.Pi 5
# Uses RP1 chip's uart2 on GPIO4/5 (pins 7/29 (TX/RX))


from time import sleep, time
from serial import Serial
from threading import Thread

from ugv import controller

from ugv.camera import UGV_Cam

#from lidar.motor import Motor as Lidar_Motor

UART_BAUDRATE = 115200
INPUT_BUFFER_SECONDS = 0.1
STICK_MOVE_THRESHOLD = 0.05         # Fixes stick drift lol

def generate_command(op : str, **kwargs) -> list[int]:

    # See table in docs for 3-byte command structure
    command = [-1, -1, -1]
    
    if op == "TURN":
        command[0] = 2 * (2**6)	    #1000_0000, opcode 10
        
        for key, val in kwargs.items():
            if key == "turn_dir" and val == "RIGHT":
                command[0] += 1
            elif key == "turn_dir" and val == "LEFT":
                command[0] += 0    # This is only here for readability

        command[1] = 240	# Speed of spin turn on shoulder buttons, [0,255]
        command[2] = 1      # Duration of spin turn on shoulder buttons
            
    if op == "MOVE":
        command[0] = 3 * (2**6)	    #1100_0000, opcode 11
        
        for key, val in kwargs.items():
            if key == "joy_pos":
                command[0] += (val < 0)	# Sets direction (bit 0) to sign of joystick pos
                command[1] = int(abs(val) * 255)    # Speed, [0,255]

        command[2] = 1
    
    return command

def open_serial_connection() -> Serial:
    
    s = Serial()		    # Create serial connection
    s.port = '/dev/ttyAMA2'	# UART port on GPIO 4 and 5
    s.baudrate = 115200		# 9600 bps Baud
    s.bytesize = 8			# 8 bits per byte
    s.parity = 'N'			# No parity bit
    #s.stopbits = 0			# One stop bit per byte
    s.timeout = 0			# Non-blocking mode (return immediately)

    # Open configured serial connection
    print(f"rpi_UART.py: Opening UGV serial via {s.name}...")
    s.open()

    # Allow connection to form
    sleep(0.05)
    print(f"rpi_UART.py: UGV serial port opened.")
    return s

def read_data(serial_conn : Serial) -> bytes | None:
    if serial_conn.is_open:
        if bytes_waiting := serial_conn.in_waiting > 0:
            data = serial_conn.read(bytes_waiting)
            return data
        else:
            return None
    else:
        raise RuntimeError("Attempted to read from closed serial port!")
    
def listen_to_UGV(serial_conn : Serial) -> str | None:
    while True:
        sleep(1/UART_BAUDRATE)
        ugv_data = read_data(serial_conn)
        if ugv_data is not None:
            for b in ugv_data:
                print(chr(b), end='')
                if chr(b) == '\n':
                    print("rpi_UART.py: [UGV]>>", end='')


def control_UGV(serial_conn : Serial) -> None:

    xb_listener_thread = Thread(target=controller.listen, daemon=True)
    xb_listener_thread.start()
    time_since_last_command = time()

    while True:
    
        current_time = time()

        if (current_time - time_since_last_command) > INPUT_BUFFER_SECONDS:

            # START + A: start recording
            if controller.input_states['BTN_START'] and controller.input_states['BTN_A'] and not UGV_Cam.is_recording:
                video_filename = UGV_Cam.my_start_recording()
                print(f"rpi_UART.py: Recording video to '{video_filename}'...")

            # START + B: stop recording
            if controller.input_states['BTN_START'] and controller.input_states['BTN_B'] and UGV_Cam.is_recording:
                UGV_Cam.my_stop_recording()
                print(f"Recording saved at {video_filename}")

            # RIGHT TRIGGER: move forward
            if (controller.input_states['BTN_RZ'] and not controller.input_states['BTN_Z']):
                move_command = generate_command("MOVE", joy_pos=controller.input_states['BTN_RZ'])
                serial_conn.write(move_command)

            # LEFT TRIGGER: move backward
            if (controller.input_states['BTN_Z'] and not controller.input_states['BTN_RZ']):
                move_command = generate_command("MOVE", joy_pos=controller.input_states['BTN_Z'] * -1)
                serial_conn.write(move_command)

            # LEFT BUMPER: spin turn left
            if (controller.input_states['BTN_TL']):
                move_command = generate_command("TURN", turn_dir="LEFT")
                serial_conn.write(move_command)

            # RIGHT BUMPER: spin turn right
            if (controller.input_states['BTN_TR']):
                move_command = generate_command("TURN", turn_dir="RIGHT")
                serial_conn.write(move_command)

            # RIGHT JOYSTICK: move (currently unmapped, gotta think about the formula)
            if controller.input_states['ABS_RY'] > STICK_MOVE_THRESHOLD or controller.input_states['ABS_RX'] > STICK_MOVE_THRESHOLD:
                pass

            time_since_last_command = current_time
    

def run_comms() -> None:
    
    serial_conn = open_serial_connection()
    
    controller_thread = Thread(target=control_UGV, args=[serial_conn], daemon=True)
    telemetry_thread = Thread(target=listen_to_UGV, args=[serial_conn], daemon=True)

    controller_thread.start()
    telemetry_thread.start()

    while True:
        pass


if __name__ == "__main__":
    run_comms()
# Raspberry Pi to Arduino Communication Driver
# AEGIS Senior Design, Created on 5/23/2025
# Designed for Arduino MEGA 2560 rev3 and R.Pi 5
# Uses RP1 chip's uart2 on GPIO4/5 (pins 7/29 (TX/RX))

from serial import Serial
from threading import Thread
import os
import time

from utils import serial_utils      # UGV_BAUDRATE
from utils import file_utils        # make_telemetry_JSON(), update_telemetry_JSON(), TRIPS_FOLDER
from rover import controller
from rover import camera            # UGV_cam
from lidar import scan

INPUT_BUFFER_SECONDS = 0.1
STICK_MOVE_THRESHOLD = 0.05         # Fixes stick drift

def generate_command(op : str, **kwargs) -> list[int]:
    '''
    Generates instructions to be sent to the Arduino MEGA in accordance with a 
    three-byte command structure. See documentation for more details.\n
    This can probably be seriously reduced, maybe down to a single byte, but why
    fix what isn't broken? See definition of 'technical debt' for more details.

    Args:
        op (str): The category of command to transmit. Currently either "TURN"
            or "MOVE".
        **kwargs: A series of key-value pairs that depend on the op selected.
            Currently TURN uses 'turn_dir' = 0 or 1, and MOVE uses 'joy_pos' = 
            [-1, 1].
    Returns:
        command (list[int]): A three-byte command to be sent to the Arduino.
    '''

    # See table in docs for 3-byte command structure
    command = [-1, -1, -1]
    
    if op == "TURN":
        command[0] = 2 * (2**6)	    #1000_0000, opcode 10
        
        for key, val in kwargs.items():
            if key == "turn_dir" and val == "RIGHT":
                command[0] += 1
            elif key == "turn_dir" and val == "LEFT":
                command[0] += 0    # This is only here for readability

        command[1] = 255	# Speed of spin turn on shoulder buttons, [0,255]
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
    '''
    Configures and opens a serial connection on UART2 (ttyAMA2) (GPIO 4/5).

    Returns:
        s (Serial): The configured and open serial port.
    '''
    
    s = Serial()		    # Create serial connection
    s.port = '/dev/ttyAMA2'	# UART port on GPIO 4 and 5
    s.baudrate = serial_utils.UGV_BAUDRATE
    s.bytesize = 8			# 8 bits per byte
    s.parity = 'N'			# No parity bit
    s.stopbits = 0			# No stop bit per byte
    s.timeout = None		# Wait forever if necessary
    s.exclusive = True      # Restrict cross-module access

    # Open configured serial connection
    print(f"[INIT] UART.py: Opening UGV serial via {s.name}...")
    s.open()

    # Allow connection to form
    time.sleep(0.05)
    print(f"[INIT] UART.py: UGV serial port opened.")
    return s

def read_data(serial_conn : Serial) -> bytes | None:
    '''
    Reads in as many bytes as are available from the Arduino via the serial
    connection.

    Args:
        serial_conn (Serial): The serial connection between the Arduino and the
            Raspberry Pi.
    Returns:
        data (bytes | None): Either the bytes waiting to be read from the buffer
            or None if the buffer is empty.
    Raises:
        RuntimeError: If the read_data function was called on a closed serial 
            port.
    '''

    if serial_conn.is_open:
        if bytes_waiting := serial_conn.in_waiting > 0:
            data = serial_conn.read(bytes_waiting)
        else:
            data = None
        return data
    else:
        raise RuntimeError("Attempted to read from closed serial port!")
    
def listen_to_UGV(serial_conn: Serial, start_time: str, dump_folder: str) -> None:
    '''
    Captures telemetry data from the Arduino and writes it to the trip's 
    telemetry JSON file. If the data is malformed, skips the frame.

    Args:
        serial_conn (Serial): The serial connection between the Arduino and the
            Raspberry Pi.
        start_time (str): The timestamp representing the start of the current 
            trip.
        dump_folder (str): The path to the telemetry JSON file's folder.
    '''

    filename = f"tel_{start_time}.json"

    while True:

        ugv_data: bytes = serial_conn.read_until(expected=b'\n')

        try:
            tel_dict = process_telemetry(ugv_data)

            filename: str = file_utils.update_telemetry_JSON(
                dump_folder, filename, telemetry=tel_dict)

        except RuntimeError:
            print("[ERROR] UART.py: INVALID ARDUINO TELEMETRY (BADLEN)\n")
   
def process_telemetry(data: bytes) -> dict:
    '''
    Converts the bytestream from the Arduino into key-value pairs inside of a 
    telemetry dictionary.

    Args:
        t_str (bytes): The unprocessed telemetry byte array from the Arduino.
    Returns:
        telemetry (dict): The dictionary of telemetry key-value pairs.
    Raises:
        RuntimeError: If the Arduino's byte array does not contain the correct
            number of elements.
    '''

    try:
        t_str: str = data.decode('utf-8')

    except UnicodeDecodeError as e:
        print("[ERROR] UART.py: UTF8 DECODE ERROR, SOLVE THIS!\n")
        print(e)
        t_str: str = ''

    ard_vals: list[str] = t_str.split('|')
    del ard_vals[-1]    # Pesky CRLF ending
    
    val_prefixes: list[str] = [
        "TIME=", 
        "LFV=", "LFA=", "LFR=", "LMV=", "LMA=", "LMR=", "LRV=", "LRA=", "LRR=",
        "RFV=", "RFA=", "RFR=", "RMV=", "RMA=", "RMR=", "RRV=", "RRA=", "RRR=",
        "USLI=", "USLF=", "USCT=", "USRT=", "USRR=",
        "GR=", "GP=", "GY=", "AX=", "AY=", "AZ=",
        "TEMP=", "RHUM=", "LVIS=", "LINF="
        #"BV=", "BA="
    ]

    if len(ard_vals) != len(val_prefixes):
        raise RuntimeError

    ard_up_s = float(ard_vals[ 0].replace(val_prefixes[ 0], ''))

    mot_lf_v = float(ard_vals[ 1].replace(val_prefixes[ 1], ''))
    mot_lf_a = float(ard_vals[ 2].replace(val_prefixes[ 2], ''))
    mot_lf_r = float(ard_vals[ 3].replace(val_prefixes[ 3], ''))
    mot_lm_v = float(ard_vals[ 4].replace(val_prefixes[ 4], ''))
    mot_lm_a = float(ard_vals[ 5].replace(val_prefixes[ 5], ''))
    mot_lm_r = float(ard_vals[ 6].replace(val_prefixes[ 6], ''))
    mot_lr_v = float(ard_vals[ 7].replace(val_prefixes[ 7], ''))
    mot_lr_a = float(ard_vals[ 8].replace(val_prefixes[ 8], ''))
    mot_lr_r = float(ard_vals[ 9].replace(val_prefixes[ 9], ''))
    mot_rf_v = float(ard_vals[10].replace(val_prefixes[10], ''))
    mot_rf_a = float(ard_vals[11].replace(val_prefixes[11], ''))
    mot_rf_r = float(ard_vals[12].replace(val_prefixes[12], ''))
    mot_rm_v = float(ard_vals[13].replace(val_prefixes[13], ''))
    mot_rm_a = float(ard_vals[14].replace(val_prefixes[14], ''))
    mot_rm_r = float(ard_vals[15].replace(val_prefixes[15], ''))
    mot_rr_v = float(ard_vals[16].replace(val_prefixes[16], ''))
    mot_rr_a = float(ard_vals[17].replace(val_prefixes[17], ''))
    mot_rr_r = float(ard_vals[18].replace(val_prefixes[18], ''))

    us_li_cm = float(ard_vals[19].replace(val_prefixes[19], ''))
    us_lf_cm = float(ard_vals[20].replace(val_prefixes[20], ''))
    us_ct_cm = float(ard_vals[21].replace(val_prefixes[21], ''))
    us_rt_cm = float(ard_vals[22].replace(val_prefixes[22], ''))
    us_rr_cm = float(ard_vals[23].replace(val_prefixes[23], ''))

    imu_gr_dps  = float(ard_vals[24].replace(val_prefixes[24], ''))
    imu_gp_dps  = float(ard_vals[25].replace(val_prefixes[25], ''))
    imu_gy_dps  = float(ard_vals[26].replace(val_prefixes[26], ''))
    imu_ax_mps2 = float(ard_vals[27].replace(val_prefixes[27], ''))
    imu_ay_mps2 = float(ard_vals[28].replace(val_prefixes[28], ''))
    imu_az_mps2 = float(ard_vals[29].replace(val_prefixes[29], ''))

    ambient_temp_c = float(ard_vals[30].replace(val_prefixes[30], ''))
    relative_hum_pct = float(ard_vals[31].replace(val_prefixes[31], ''))
    visible_light_l  = float(ard_vals[32].replace(val_prefixes[32], ''))
    infrared_light_l = float(ard_vals[33].replace(val_prefixes[33], ''))

    batt_v = 0 #float(ard_vals[34].replace(val_prefixes[34], ''))
    batt_a = 0 #float(ard_vals[35].replace(val_prefixes[35], ''))
    batt_pct = 0                                                # TODO: COMPUTE 

    # POPULATE RASPBERRY PI TELEMETRY

    # All of this is pretty messy. It directly pulls RPI values via shell 
    # commands, so only worry about these if one of them breaks

    cpu_util: list[str] = os.popen('top -bn1 | grep "%Cpu(s):"').read(
        ).replace(',', ', ').split()
    cpu_util_pct: float = 0 #100 - float(cpu_util[7])       TODO: FIX

    adc_vals: list[str] = os.popen('vcgencmd pmic_read_adc').read().split()
    fmt = lambda idx, pre, post: round(
        float(adc_vals[idx].replace(pre,'').replace(post,'')), 4)
    vdd_core_a: float = fmt(13, 'current(6)=', 'A')
    vdd_core_v: float = fmt(49, 'volt(24)=', 'V')

    mem: list[str] = os.popen('free').read().split()[7:9]
    mem_util_pct: float = round(100*int(mem[1])/int(mem[0]), 2)

    storage_avail_mb: str = os.popen('df -h /').read().split()[10]

    uptime: str = os.popen("awk '{print $1}' /proc/uptime").read(
                            ).replace('\n', '')
    uptime_s: float = round(float(uptime))

    soc_temp_c: float = float(os.popen('vcgencmd measure_temp').read()
                            .replace('temp=','').replace("'C\n", ''))

    telemetry = {
        "rpi": {
            "uptime_s": uptime_s,
            "cpu_util_pct": cpu_util_pct,
            "mem_util_pct": mem_util_pct,
            "storage_avail_mb": storage_avail_mb,
            "temp_c": soc_temp_c,
            "vdd_core_a": vdd_core_a,
            "vdd_core_v": vdd_core_v
        },
        "arduino": {
            "uptime_s": ard_up_s
        },
        # "lidar": {  # Modified from scan.py
        #     "connected": False,
        #     "scanning": False,
        #     "scan_pct": 0,
        #     "saving_file": False,
        #     "fixed_mode": False,
        #     "motor_pos_deg": 0
        # },
        # "camera": { # Modified from camera.py
        #     "connected": False,
        #     "recording": False,
        #     "streaming": False,
        #     "last_file": None
        # },
        "motors": {
            "front_left": {
                "voltage_v": mot_lf_v, "current_a": mot_lf_a, "rpm": mot_lf_r
            },
            "mid_left": {
                "voltage_v": mot_lm_v, "current_a": mot_lm_a, "rpm": mot_lm_r
            },
            "rear_left": {
                "voltage_v": mot_lr_v, "current_a": mot_lr_a, "rpm": mot_lr_r
            },
            "front_right": {
                "voltage_v": mot_rf_v, "current_a": mot_rf_a, "rpm": mot_rf_r
            },
            "mid_right": {
                "voltage_v": mot_rm_v, "current_a": mot_rm_a, "rpm": mot_rm_r
            },
            "rear_right": {
                "voltage_v": mot_rr_v, "current_a": mot_rr_a, "rpm": mot_rr_r
            }
        },
        "ultrasonics": {
            "lidar_cm": us_li_cm,
            "left_cm": us_lf_cm,
            "center_cm": us_ct_cm,
            "right_cm": us_rt_cm,
            "rear_cm": us_rr_cm
        },
        "imu": {
            "roll_dps": imu_gr_dps,
            "pitch_dps": imu_gp_dps,
            "yaw_dps": imu_gy_dps,
            "accel_x_mps2": imu_ax_mps2,
            "accel_y_mps2": imu_ay_mps2,
            "accel_z_mps2": imu_az_mps2
        },
        "ugv": {
            "battery": {
                "capacity_pct": batt_pct,
                "voltage_v": batt_v,
                "current_a": batt_a
            },
            "headlights": False, 
            "ambient_temp_c": ambient_temp_c,
            "relative_hum_pct": relative_hum_pct,
            "ambient_light_l": visible_light_l,
            "ambient_infrared_l": infrared_light_l
        }
    }

    return telemetry

def control_UGV(serial_conn : Serial, dump_folder: str) -> None:
    '''
    Enables the UGV to be piloted by a controller, such as an XBOX controller.
    Reads controller input states from a background listener thread. Includes 
    measures to prevent the overflowing of the Arduino command buffer.

    Args:
        serial_conn (Serial): The serial connection between the Arduino and the
            Raspberry Pi.
    '''
    xb_listener_thread = Thread(target=controller.listen, daemon=True)
    xb_listener_thread.start()
    time_since_last_command = time.time()

    scanner = scan.Scanner()

    while True:
    
        current_time: float = time.time()

        if (current_time - time_since_last_command) > INPUT_BUFFER_SECONDS:

            # RIGHT TRIGGER: move forward
            if (controller.input_states['BTN_RZ'] and
            not controller.input_states['BTN_Z']):
                move_command = generate_command(
                    "MOVE", joy_pos=controller.input_states['BTN_RZ']
                )
                serial_conn.write(move_command)     #type: ignore

            # LEFT TRIGGER: move backward
            if (controller.input_states['BTN_Z'] and 
            not controller.input_states['BTN_RZ']):
                move_command = generate_command(
                    "MOVE", joy_pos=controller.input_states['BTN_Z'] * -1
                )
                serial_conn.write(move_command)     #type: ignore

            # LEFT BUMPER: spin turn left
            if (controller.input_states['BTN_TL']):
                move_command = generate_command("TURN", turn_dir="LEFT")
                serial_conn.write(move_command)     #type: ignore

            # RIGHT BUMPER: spin turn right
            if (controller.input_states['BTN_TR']):
                move_command = generate_command("TURN", turn_dir="RIGHT")
                serial_conn.write(move_command)     #type: ignore

            # START + A: start recording
            if (controller.input_states['BTN_START'] and 
            controller.input_states['BTN_A'] and not camera.UGV_Cam.recording):
                video_filename = camera.UGV_Cam.my_start_recording()
                print(f"UART.py: Recording video to '{video_filename}'...")

            # START + B: stop recording
            if (controller.input_states['BTN_START'] and 
            controller.input_states['BTN_B'] and camera.UGV_Cam.recording):
                camera.UGV_Cam.my_stop_recording()
                print(f"UART.py: Recording saved to '{video_filename}'.")   #type: ignore

            # START + Y: take LiDAR scan
            if (controller.input_states['BTN_START'] and
            controller.input_states['BTN_Y']):
                
                cloud: list[list[float]] = scanner.capture_cloud()
                scanner.save_scan(cloud, filepath=dump_folder)

            # START + RIGHT BUMPER: increase scan resolution
            if (controller.input_states['BTN_START'] and
            controller.input_states['BTN_TR']):
                if (scanner.rings_per_cloud < 1600):
                    scanner.set_rings_per_cloud(scanner.rings_per_cloud * 2)
                    print(f"[RUNTIME] UART.py: Increased scan resolution to {scanner.rings_per_cloud} rings.")
                
            # START + LEFT BUMPER: decrease scan resolution
            if (controller.input_states['BTN_START'] and
            controller.input_states['BTN_TL']):
                if (scanner.rings_per_cloud > 50):
                    scanner.set_rings_per_cloud(int(scanner.rings_per_cloud / 2))
                    print(f"[RUNTIME] UART.py: Decreased scan resolution to {scanner.rings_per_cloud} rings.")


            time_since_last_command: float = current_time
    
def run_comms() -> None:
    '''
    Establishes bidirectional UART communication between the Arduino and
    Raspberry Pi. Records the beginning of the trip, creates a trip folder,
    and spawns and joins two threads: one for the controls and one for the 
    telemetry retrieval.
    '''

    trip_start_timestamp: str = file_utils.get_current_timestamp()
    trip_folder: str = file_utils.make_folder(
        file_utils.TRIPS_FOLDER, trip_start_timestamp)
    print(f"[INIT] UART.py: Created trip folder at {trip_folder}.")

    serial_conn: Serial = open_serial_connection()
    
    controller_thread = Thread(target=control_UGV,
        args=[serial_conn, trip_folder])
    telemetry_thread = Thread(target=listen_to_UGV, 
        args=[serial_conn, trip_start_timestamp, trip_folder])

    controller_thread.start()
    telemetry_thread.start()

    controller_thread.join()
    telemetry_thread.join()

if __name__ == "__main__":
    run_comms()
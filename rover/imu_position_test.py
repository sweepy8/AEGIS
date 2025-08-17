'''
I2C Driver Test Program

    Read Gyro and Accelerometer by Interfacing Raspberry Pi with MPU6050 using Python
    http://www.electronicwings.com

    
    Connect SDA to pin 3, SCL to pin 5
    
'''

import smbus	            # SMBus module of I2C
from time import sleep
from time import time

READ_DELAY_SECONDS  = 0.05	# Seconds between reads
UPDATE_THRESHOLD    = 5  # Difference from new to old val., below which no update occurs
UPDATE_RATE_SECONDS = 1     # How frequently to update, regardless of threshold

# Some MPU6050 registers and their addresses
DEVICE_ADDR  = 0x68   # MPU6050 device address
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47

bus = smbus.SMBus(1) 	# or bus = smbus.SMBus(0) for older version boards
Ax, Ay, Az = 0, 0, 0
Gx, Gy, Gz = 0, 0, 0

def MPU_Init():
    # Write to sample rate register
    bus.write_byte_data(DEVICE_ADDR, SMPLRT_DIV, 7)	 # Sample rate = Gyroscope Output Rate / 1 + SMPLRT_DIV --> 1kHz
    
    # Write to power management register
    bus.write_byte_data(DEVICE_ADDR, PWR_MGMT_1, 1)	 # Configures pwr mode and clk source via PWR_MGMT_1 register
    
    # Write to Configuration register
    bus.write_byte_data(DEVICE_ADDR, CONFIG, 0)		 # Frame Sync is off, DLPF off
    
    # Write to Gyro configuration register
    bus.write_byte_data(DEVICE_ADDR, GYRO_CONFIG, 24) # Disable self test, set FS_SEL to 3 == 2000 deg/s in GYRO_CONFIG register
    
    # Write to interrupt enable register
    bus.write_byte_data(DEVICE_ADDR, INT_ENABLE, 1)	 # Configuration complete, begin transmitting IMU data

def read_raw_data(addr):
    # Accelero and Gyro value are 16-bit
    msb_val = bus.read_byte_data(DEVICE_ADDR, addr)
    lsb_val = bus.read_byte_data(DEVICE_ADDR, addr+1)

    # Concatenate higher and lower value
    value = (msb_val << 8) | lsb_val
    
    # Unsigned --> Signed value conversion
    if(value > 32768):
        value = value - 65536

    return value


def update_val(threshold : float):
    pass




MPU_Init()

print ("Reading Gyroscope and Accelerometer Data:")

position = [0.0, 0.0, 0.0]
pose = [0.0, 0.0, 0.0]

start_time = time()


while True:

    # Read Accelerometer raw value
    acc_x = read_raw_data(ACCEL_XOUT_H)/16384.0
    acc_y = read_raw_data(ACCEL_YOUT_H)/16384.0
    acc_z = read_raw_data(ACCEL_ZOUT_H)/16384.0
    
    # Read Gyroscope raw value
    gyro_x = read_raw_data(GYRO_XOUT_H)/131.0
    gyro_y = read_raw_data(GYRO_YOUT_H)/131.0
    gyro_z = read_raw_data(GYRO_ZOUT_H)/131.0

    acc_x = 0 if abs(acc_x) < 0.1 else acc_x
    acc_y = 0 if abs(acc_y) < 0.1 else acc_y
    acc_z = 0 if abs(acc_z) < 0.1 else acc_z
    gyro_x = 0 if abs(gyro_x) < 2 else gyro_x
    gyro_y = 0 if abs(gyro_y) < 2 else gyro_y
    gyro_z = 0 if abs(gyro_z) < 2 else gyro_z

    
    # Full scale range +/- 250 degree/s as per sensitivity scale factor
    if time() - start_time < UPDATE_RATE_SECONDS:
        Ax = acc_x if abs(acc_x - Ax) > UPDATE_THRESHOLD else Ax # 1g in +/- 2g range [-2,2] is 65536 / 4 == 16384
        Ay = acc_y if abs(acc_y - Ay) > UPDATE_THRESHOLD else Ay
        Az = acc_z if abs(acc_z - Az) > UPDATE_THRESHOLD else Az
        
        Gx = gyro_x if abs(gyro_x - Gx) > UPDATE_THRESHOLD else Gx
        Gy = gyro_y if abs(gyro_y - Gy) > UPDATE_THRESHOLD else Gy
        Gz = gyro_z if abs(gyro_z - Gz) > UPDATE_THRESHOLD else Gz
        
    else:
        Ax = 0
        Ay = 0
        Az = 0
        
        Gx = 0
        Gy = 0
        Gz = 0
    
    start_time = time()
    
    print(f"G: (PIT={Gx:8.4f}, ROL={Gy:8.4f}, YAW={Gz:8.4f})", end=',    ')
    print(f"A: (X={Ax:8.4f}, Y={Ay:8.4f}, Z={Az:8.4f})")

    position[0] += Ax * ((READ_DELAY_SECONDS)**2) / 2
    position[1] += Ay * ((READ_DELAY_SECONDS)**2) / 2
    position[2] += Az * ((READ_DELAY_SECONDS)**2) / 2

    pose[0] += Gx * (READ_DELAY_SECONDS)
    pose[1] += Gy * (READ_DELAY_SECONDS)
    pose[2] += Gz * (READ_DELAY_SECONDS)

    print(f"Pose: {pose[0]:8.4f} {pose[1]:8.4f} {pose[2]:8.4f}", end='    ')
    print(f"Position: {position[0]:8.4f} {position[1]:8.4f} {position[2]:8.4f}")

    sleep(READ_DELAY_SECONDS)
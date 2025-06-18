'''
I2C Driver Test Program

    Read Gyro and Accelerometer by Interfacing Raspberry Pi with MPU6050 using Python
    http://www.electronicwings.com

    
    Connect SDA to pin 3, SCL to pin 5
    
'''

import smbus	            # SMBus module of I2C
from time import sleep
from time import time

READ_DELAY_SECONDS  = 0.1	# Seconds between reads
UPDATE_THRESHOLD    = 0.01  # Difference from new to old val., below which no update occurs
UPDATE_RATE_SECONDS = 5     # How frequently to update, regardless of threshold

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

start_time = time()

while True:

    # Read Accelerometer raw value
    acc_x = read_raw_data(ACCEL_XOUT_H)
    acc_y = read_raw_data(ACCEL_YOUT_H)
    acc_z = read_raw_data(ACCEL_ZOUT_H)
    
    # Read Gyroscope raw value
    gyro_x = read_raw_data(GYRO_XOUT_H)
    gyro_y = read_raw_data(GYRO_YOUT_H)
    gyro_z = read_raw_data(GYRO_ZOUT_H)
    
    # Full scale range +/- 250 degree/s as per sensitivity scale factor
    if time() - start_time < UPDATE_RATE_SECONDS:
        Ax = acc_x/16384.0 if abs(acc_x/16384.0 - Ax) > UPDATE_THRESHOLD else Ax # 1g in +/- 2g range [-2,2] is 65536 / 4 == 16384
        Ay = acc_y/16384.0 if abs(acc_y/16384.0 - Ay) > UPDATE_THRESHOLD else Ay
        Az = acc_z/16384.0 if abs(acc_z/16384.0 - Az) > UPDATE_THRESHOLD else Az
        
        Gx = gyro_x/131.0 if abs(gyro_x/131.0 - Gx) > UPDATE_THRESHOLD else Gx
        Gy = gyro_y/131.0 if abs(gyro_y/131.0 - Gy) > UPDATE_THRESHOLD else Gy
        Gz = gyro_z/131.0 if abs(gyro_z/131.0 - Gz) > UPDATE_THRESHOLD else Gz
        
    else:
        Ax = acc_x/16384.0
        Ay = acc_y/16384.0
        Az = acc_z/16384.0
        
        Gx = gyro_x/131.0
        Gy = gyro_y/131.0
        Gz = gyro_z/131.0
        
        start_time = time()
    
    print(f"G: (X={Gx:8.4f}, Y={Gy:8.4f}, Z={Gz:8.4f})", end=',    ')
    print(f"A: (X={Ax:8.4f}, Y={Ay:8.4f}, Z={Az:8.4f})")
        
    sleep(READ_DELAY_SECONDS)
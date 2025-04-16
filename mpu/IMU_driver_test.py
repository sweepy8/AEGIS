'''
I2C Driver Test Program

    Read Gyro and Accelerometer by Interfacing Raspberry Pi with MPU6050 using Python
    http://www.electronicwings.com
    
    
TODO
    - Switch from running ring buffer to threshold variation from past to present
        in order to update value. Should fix the startup delay?
    
'''
import smbus					#import SMBus module of I2C
from time import sleep          #import

#some MPU6050 Registers and their Address
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



def MPU_Init():
    #write to sample rate register
    bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)	# Sample rate = Gyroscope Output Rate / 1 + SMPLRT_DIV --> 1kHz
    
    #Write to power management register
    bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)	#Configures pwr mode and clk source via PWR_MGMT_1 register
    
    #Write to Configuration register
    bus.write_byte_data(Device_Address, CONFIG, 0)		#Frame Sync is off, DLPF off
    
    #Write to Gyro configuration register
    bus.write_byte_data(Device_Address, GYRO_CONFIG, 24) # Disable self test, set FS_SEL to 3 == 2000 deg/s in GYRO_CONFIG register
    
    #Write to interrupt enable register
    bus.write_byte_data(Device_Address, INT_ENABLE, 1)	# Configuration complete, begin transmitting IMU data

def read_raw_data(addr):
    #Accelero and Gyro value are 16-bit
    high = bus.read_byte_data(Device_Address, addr)
    low = bus.read_byte_data(Device_Address, addr+1)

    #concatenate higher and lower value
    value = ((high << 8) | low)
    
    #to get signed value from mpu6050
    if(value > 32768):
            value = value - 65536
    return value


bus = smbus.SMBus(1) 	# or bus = smbus.SMBus(0) for older version boards
Device_Address = 0x68   # MPU6050 device address

MPU_Init()

print ("Reading Gyroscope and Accelerometer Data:")

AVERAGE_COUNT = 1000	# Initial delay == AVERAGE_COUNT * READ_DELAY
READ_DELAY    = 0.05	# seconds

acc_avg_buf = [None]  * AVERAGE_COUNT
gyro_avg_buf = [None] * AVERAGE_COUNT
avg_bufs_count = 0

while True:
    
    for i in range(0, AVERAGE_COUNT):
        #Read Accelerometer raw value
        acc_x = read_raw_data(ACCEL_XOUT_H)
        acc_y = read_raw_data(ACCEL_YOUT_H)
        acc_z = read_raw_data(ACCEL_ZOUT_H)
        
        #Read Gyroscope raw value
        gyro_x = read_raw_data(GYRO_XOUT_H)
        gyro_y = read_raw_data(GYRO_YOUT_H)
        gyro_z = read_raw_data(GYRO_ZOUT_H)
        
        #Full scale range +/- 250 degree/s as per sensitivity scale factor
        Ax = acc_x/16384.0		# 1g in +/- 2g range [-2,2] is 65536 / 4 == 16384
        Ay = acc_y/16384.0
        Az = acc_z/16384.0
        
        Gx = gyro_x/131.0
        Gy = gyro_y/131.0
        Gz = gyro_z/131.0
        
        acc_avg_buf[i] = (Ax, Ay, Az)
        gyro_avg_buf[i] = (Gx, Gy, Gz)
        
        if avg_bufs_count == AVERAGE_COUNT:
            acc_avg = [sum(read[0] for read in acc_avg_buf) / AVERAGE_COUNT,
                       sum(read[1] for read in acc_avg_buf) / AVERAGE_COUNT,
                       sum(read[2] for read in acc_avg_buf) / AVERAGE_COUNT]
            
            gyro_avg = [sum(read[0] for read in gyro_avg_buf) / AVERAGE_COUNT,
                        sum(read[1] for read in gyro_avg_buf) / AVERAGE_COUNT,
                        sum(read[2] for read in gyro_avg_buf) / AVERAGE_COUNT]
    
            print(f"G_AVG: (X={gyro_avg[0]:9.4f}, Y={gyro_avg[1]:9.4f}, Z={gyro_avg[2]:9.4f})", end=',    ')
            print(f"A_AVG: (X={acc_avg[0]:9.4f}, Y={acc_avg[1]:9.4f}, Z={acc_avg[2]:9.4f})")

        else:
            avg_bufs_count += 1
            
        sleep(READ_DELAY)
    

    #print ("Gx=%.4f" %Gx, u'\u00b0'+ "/s", "\tGy=%.4f" %Gy, u'\u00b0'+ "/s", "\tGz=%.4f" %Gz, u'\u00b0'+ "/s", "\tAx=%.4f g" %Ax, "\tAy=%.4f g" %Ay, "\tAz=%.4f g" %Az) 	
    #sleep(1)

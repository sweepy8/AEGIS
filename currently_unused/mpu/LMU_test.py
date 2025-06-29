import smbus2
import time

# MPU-6050 Registers and Address
MPU6050_ADDR = 0x68
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H = 0x43

# Initialize I2C bus
bus = smbus2.SMBus(1)

# Wake up the MPU-6050
bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0)

def read_raw_data(addr):
    # Read two bytes of data from the given address
    high = bus.read_byte_data(MPU6050_ADDR, addr)
    low = bus.read_byte_data(MPU6050_ADDR, addr+1)
    value = (high << 8) | low
    # Convert to signed value
    if value > 32767:
        value -= 65536
    return value

try:
    while True:
        # Read accelerometer data
        accel_x = read_raw_data(ACCEL_XOUT_H)
        accel_y = read_raw_data(ACCEL_XOUT_H + 2)
        accel_z = read_raw_data(ACCEL_XOUT_H + 4)

        # Read gyroscope data
        gyro_x = read_raw_data(GYRO_XOUT_H)
        gyro_y = read_raw_data(GYRO_XOUT_H + 2)
        gyro_z = read_raw_data(GYRO_XOUT_H + 4)

        # Convert raw data to meaningful values (optional scaling may be needed)
        accel_x_scaled = accel_x / 16384.0
        accel_y_scaled = accel_y / 16384.0
        accel_z_scaled = accel_z / 16384.0

        gyro_x_scaled = gyro_x / 131.0
        gyro_y_scaled = gyro_y / 131.0
        gyro_z_scaled = gyro_z / 131.0

        print(f"Accelerometer: X={accel_x_scaled:.2f}, Y={accel_y_scaled:.2f}, Z={accel_z_scaled:.2f}")
        print(f"Gyroscope: X={gyro_x_scaled:.2f}, Y={gyro_y_scaled:.2f}, Z={gyro_z_scaled:.2f}")

        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting...")

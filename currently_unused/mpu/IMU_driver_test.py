"""
ChatGPT code uses quaternion units to simplify the yaw, pitch, and roll computations

MPU-6050 + Madgwick AHRS Fusion (Python)

– Reads accel + gyro in one I²C burst (14 bytes)
– Calibrates gyro bias at startup (500 samples)
– Feeds (ax,ay,az, gx,gy,gz) into MadgwickAHRS each loop
– Prints Yaw, Pitch, Roll (in degrees)

Tested on Raspberry Pi (smbus2).
"""

import smbus2
import time
import math

# === MPU-6050 Registers & Constants ===
MPU_ADDR       = 0x68
PWR_MGMT_1     = 0x6B
SMPLRT_DIV     = 0x19
CONFIG         = 0x1A
GYRO_CONFIG    = 0x1B
ACCEL_CONFIG   = 0x1C
INT_ENABLE     = 0x38
ACCEL_XOUT_H   = 0x3B  # Read 14 bytes starting here

# When FS_SEL=0 (±250 °/s) and AFS_SEL=0 (±2 g):
ACCEL_SCALE = 16384.0   # LSB/g
GYRO_SCALE  = 131.0     # LSB/(°/s)

# I²C bus
bus = smbus2.SMBus(1)


def mpu_init():
    """
    Initialize MPU-6050:
      • Wake up (clear SLEEP bit)
      • Sample rate = GyroRate/(1+SMPLRT_DIV) = ~125 Hz
      • DLPF = 44 Hz
      • Gyro FS = ±250 °/s
      • Accel FS = ±2 g
      • Enable Data Ready interrupt (optional)
    """
    # Wake up
    bus.write_byte_data(MPU_ADDR, PWR_MGMT_1, 0x00)
    time.sleep(0.1)

    # Sample rate divider: 1 kHz/(1+7) = 125 Hz
    bus.write_byte_data(MPU_ADDR, SMPLRT_DIV, 0x07)

    # DLPF_CFG = 3 → 44 Hz
    bus.write_byte_data(MPU_ADDR, CONFIG, 0x03)

    # Gyro FS_SEL = 0 → ±250 °/s
    bus.write_byte_data(MPU_ADDR, GYRO_CONFIG, 0x00)

    # Accel AFS_SEL = 0 → ±2 g
    bus.write_byte_data(MPU_ADDR, ACCEL_CONFIG, 0x00)

    # (Optional) enable data ready interrupt
    bus.write_byte_data(MPU_ADDR, INT_ENABLE, 0x01)

    time.sleep(0.1)


def read_all_raw():
    """
    Do one I²C burst read of 14 bytes:
      [AxH, AxL, AyH, AyL, AzH, AzL, TempH, TempL,
       GxH, GxL, GyH, GyL, GzH, GzL]
    Returns a dict of signed 16-bit ints.
    """
    data = bus.read_i2c_block_data(MPU_ADDR, ACCEL_XOUT_H, 14)

    def to_int16(msb, lsb):
        val = (msb << 8) | lsb
        if val & 0x8000:
            val = val - 0x10000
        return val

    ax = to_int16(data[0], data[1])
    ay = to_int16(data[2], data[3])
    az = to_int16(data[4], data[5])
    # Skip data[6], data[7] (temp) unless you need it
    gx = to_int16(data[8], data[9])
    gy = to_int16(data[10], data[11])
    gz = to_int16(data[12], data[13])

    return {"ax": ax, "ay": ay, "az": az, "gx": gx, "gy": gy, "gz": gz}


def get_scaled(raw):
    """
    Convert raw readings → physical units:
      ax, ay, az in g  (±2 g range)
      gx, gy, gz in °/s (±250 °/s)
    """
    return {
        "ax": raw["ax"] / ACCEL_SCALE,
        "ay": raw["ay"] / ACCEL_SCALE,
        "az": raw["az"] / ACCEL_SCALE,
        "gx": raw["gx"] / GYRO_SCALE,
        "gy": raw["gy"] / GYRO_SCALE,
        "gz": raw["gz"] / GYRO_SCALE,
    }


def calibrate_gyro(samples=500, delay=0.005):
    """
    Average `samples` gyro readings (°/s) while stationary.
    Returns (ox, oy, oz) biases to subtract later.
    """
    print("Calibrating gyro – keep device flat and still…")
    ox = oy = oz = 0.0
    for _ in range(samples):
        raw = read_all_raw()
        s = get_scaled(raw)
        ox += s["gx"]
        oy += s["gy"]
        oz += s["gz"]
        time.sleep(delay)
    ox /= samples
    oy /= samples
    oz /= samples
    print(f"  Gyro biases (°/s): X={ox:.4f}, Y={oy:.4f}, Z={oz:.4f}\n")
    return ox, oy, oz


class MadgwickAHRS:
    """
    Madgwick’s AHRS (gradient descent) in pure Python.
    - beta: algorithm gain (default 0.1). Lower → slower convergence, smoother; higher → faster but noisier.
    - Internally keeps quaternion (q0,q1,q2,q3), where q0 = w.
    """

    def __init__(self, beta=0.1):
        self.beta = beta
        # Initialize quaternion to “no rotation”
        self.q0 = 1.0  # w
        self.q1 = 0.0  # x
        self.q2 = 0.0  # y
        self.q3 = 0.0  # z

    def update(self, gx, gy, gz, ax, ay, az, dt):
        """
        Call every loop with:
          gx,gy,gz in radians/sec (Ω from gyro)
          ax,ay,az in g (normalized)
          dt in seconds (time since last update)
        Updates self.q0…q3 in place.
        """
        # Short name locals
        q0 = self.q0
        q1 = self.q1
        q2 = self.q2
        q3 = self.q3
        beta = self.beta

        # 1) Normalize accelerometer (if zero vector, skip update)
        norm = math.sqrt(ax*ax + ay*ay + az*az)
        if norm == 0.0:
            return  # invalid accel, cannot correct
        ax /= norm
        ay /= norm
        az /= norm

        # 2) Auxiliary variables to avoid repeated arithmetic
        _2q0 = 2.0 * q0
        _2q1 = 2.0 * q1
        _2q2 = 2.0 * q2
        _2q3 = 2.0 * q3
        _4q0 = 4.0 * q0
        _4q1 = 4.0 * q1
        _4q2 = 4.0 * q2
        _8q1 = 8.0 * q1
        _8q2 = 8.0 * q2
        q0q0 = q0 * q0
        q1q1 = q1 * q1
        q2q2 = q2 * q2
        q3q3 = q3 * q3

        # 3) Gradient descent algorithm corrective step
        # See “Madgwick 2010” for derivation: f = objective function, J = Jacobian.
        s0 = _4q0 * q2q2 + _2q2 * ax + _4q0 * q1q1 - _2q1 * ay
        s1 = _4q1 * q3q3 - _2q3 * ax + 4.0 * q0q0 * q1 - _2q0 * ay - _4q1 + _8q1 * q1q1 + _8q1 * q2q2 + _4q1 * az
        s2 = 4.0 * q0q0 * q2 + _2q0 * ax + _4q2 * q3q3 - _2q3 * ay - _4q2 + _8q2 * q1q1 + _8q2 * q2q2 + _4q2 * az
        s3 = 4.0 * q1q1 * q3 - _2q1 * ax + 4.0 * q2q2 * q3 - _2q2 * ay

        # Normalize step magnitude
        norm_s = math.sqrt(s0*s0 + s1*s1 + s2*s2 + s3*s3)
        if norm_s == 0.0:
            return  # avoid division by zero
        s0 /= norm_s
        s1 /= norm_s
        s2 /= norm_s
        s3 /= norm_s

        # 4) Compute quaternion derivative from gyro (Ω) minus feedback step
        # Note: gx,gy,gz are in rad/s
        qDot0 = 0.5 * (-q1 * gx - q2 * gy - q3 * gz) - beta * s0
        qDot1 = 0.5 * ( q0 * gx + q2 * gz - q3 * gy) - beta * s1
        qDot2 = 0.5 * ( q0 * gy - q1 * gz + q3 * gx) - beta * s2
        qDot3 = 0.5 * ( q0 * gz + q1 * gy - q2 * gx) - beta * s3

        # 5) Integrate to yield new quaternion
        q0 += qDot0 * dt
        q1 += qDot1 * dt
        q2 += qDot2 * dt
        q3 += qDot3 * dt

        # 6) Normalize quaternion
        norm_q = math.sqrt(q0*q0 + q1*q1 + q2*q2 + q3*q3)
        if norm_q == 0.0:
            return
        q0 /= norm_q
        q1 /= norm_q
        q2 /= norm_q
        q3 /= norm_q

        # 7) Store back
        self.q0 = q0
        self.q1 = q1
        self.q2 = q2
        self.q3 = q3

    def quaternion_to_euler(self):
        """
        Convert current quaternion → (yaw, pitch, roll) in degrees.
          • yaw   = ψ   (around Z)
          • pitch = θ   (around Y)
          • roll  = φ   (around X)
        Using aerospace sequence: ZYX (yaw→pitch→roll).
        """
        q0 = self.q0
        q1 = self.q1
        q2 = self.q2
        q3 = self.q3

        # yaw (ψ) = atan2(2(q0q3 + q1q2), 1 − 2(q2² + q3²))
        siny_cosp = 2.0 * (q0 * q3 + q1 * q2)
        cosy_cosp = 1.0 - 2.0 * (q2 * q2 + q3 * q3)
        yaw = math.degrees(math.atan2(siny_cosp, cosy_cosp))

        # pitch (θ) = asin(2(q0q2 − q3q1))
        sinp = 2.0 * (q0 * q2 - q3 * q1)
        if abs(sinp) >= 1:
            pitch = math.degrees(math.copysign(math.pi / 2, sinp))  # use 90° if out of range
        else:
            pitch = math.degrees(math.asin(sinp))

        # roll (φ) = atan2(2(q0q1 + q2q3), 1 − 2(q1² + q2²))
        sinr_cosp = 2.0 * (q0 * q1 + q2 * q3)
        cosr_cosp = 1.0 - 2.0 * (q1 * q1 + q2 * q2)
        roll = math.degrees(math.atan2(sinr_cosp, cosr_cosp))

        return yaw, pitch, roll


def main():
    # 1) Initialize MPU-6050
    mpu_init()

    # 2) Calibrate gyro biases once
    gyro_offset = calibrate_gyro(samples=500, delay=0.005)

    # 3) Instantiate Madgwick filter (tweak beta as needed)
    madgwick = MadgwickAHRS(beta=0.1)

    # 4) Main loop timing
    last_time = time.time()

    print("Starting main loop (Ctrl+C to exit)…")
    print(f"{'Yaw [°]':>8}   {'Pitch [°]':>8}   {'Roll [°]':>8}")
    try:
        while True:
            now = time.time()
            dt = now - last_time
            last_time = now

            # 5) Read raw data & scale
            raw = read_all_raw()
            scaled = get_scaled(raw)

            # 6) Subtract gyro offset, then convert to rad/s
            gx = (scaled["gx"] - gyro_offset[0]) * (math.pi / 180.0)
            gy = (scaled["gy"] - gyro_offset[1]) * (math.pi / 180.0)
            gz = (scaled["gz"] - gyro_offset[2]) * (math.pi / 180.0)

            ax = scaled["ax"]
            ay = scaled["ay"]
            az = scaled["az"]

            # 7) Feed into Madgwick algorithm
            madgwick.update(gx, gy, gz, ax, ay, az, dt)

            # 8) Extract yaw, pitch, roll
            yaw, pitch, roll = madgwick.quaternion_to_euler()

            # 9) Print (overwrite the same line)
            print(f"\r{yaw:8.2f}   {pitch:8.2f}   {roll:8.2f}", end="")

            # 10) Sleep until ≈125 Hz (because SMPLRT_DIV=7 → ~125 Hz output)
            #     Adjust if your loop overhead is significant.
            time.sleep(max(0, 0.008 - (time.time() - now)))

    except KeyboardInterrupt:
        print("\nExited by user.")


if __name__ == "__main__":
    main()

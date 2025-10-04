// Put this in a sketch or whatever

#include "Adafruit_BNO08x.h"

#define RAD2DEG 180.0f / PI

static Adafruit_BNO08x imu(-1); // -1 to float reset pin in I2C mode, see ds

struct imu_pose_quat {
  float r = 0.0f;
  float i = 0.0f;
  float j = 0.0f;
  float k = 0.0f;
};

struct imu_pose_euler {
  float roll  = 0.0f;
  float pitch = 0.0f;
  float yaw   = 0.0f;
};

struct imu_avgs {
  imu_pose_euler pose;

  float accx  = 0.0f;
  float accy  = 0.0f;
  float accz  = 0.0f;
};

// Running IMU sensor values and accumulators
static imu_pose_quat q_pose_last;
static imu_pose_euler e_pose_last;

static float accx_last = 0.0f;
static float accy_last = 0.0f;
static float accz_last = 0.0f;

static float accx_sum = 0.0f;
static float accy_sum = 0.0f;
static float accz_sum = 0.0f;
static uint16_t imu_sample_count = 0; // N=0 averages are skipped



/*
Takes a reading of IMU sensor values and appends them to their accumulators.
Does not accumulate pose quaternion, as this is processed internally on chip.
This function should be called every N microseconds, where N is the period 
defined in config.h.
*/
void sensors_imu_tick(uint32_t /*now_us*/)
{
  sh2_SensorValue_t imuVals;
  
  while (imu.getSensorEvent(&imuVals))
  {
    switch (imuVals.sensorId) {
      case SH2_GAME_ROTATION_VECTOR:
        q_pose_last.r = imuVals.un.gameRotationVector.real;
        q_pose_last.i = imuVals.un.gameRotationVector.i;
        q_pose_last.j = imuVals.un.gameRotationVector.j;
        q_pose_last.k = imuVals.un.gameRotationVector.k;
        break;

      case SH2_ACCELEROMETER: {
        accx_last = imuVals.un.accelerometer.x;
        accy_last = imuVals.un.accelerometer.y;
        accz_last = imuVals.un.accelerometer.z; 
        if (isfinite(accx_last) && isfinite(accy_last) && isfinite(accz_last)) {
          accx_sum += accx_last;
          accy_sum += accy_last;
          accz_sum += accz_last;
          imu_sample_count++;
        }
        break;
      }
    }
  }
}

/*
Takes an average of the last N IMU sensor readings (except pose vector),
packages them into a struct, and resets the accumulators. Struct is then sent
to Raspberry Pi with the rest of the telemetry externally.
*/
void sensors_get_and_reset_imu_avg(imu_avgs& out)
{
  get_euler_from_quaternion(out, q_pose_last);
  const uint16_t n = imu_sample_count;
  out.accx = n ? (accx_sum / n) : 0.0f;
  out.accy = n ? (accy_sum / n) : 0.0f;
  out.accz = n ? (accz_sum / n) : 0.0f;

  accx_sum = 0.0f;
  accy_sum = 0.0f;
  accz_sum = 0.0f;
  imu_sample_count = 0;
}

/*
Helper function to compute the euler rotations (roll, pitch, yaw) relative to 
the rover body from the last captured quaternion vector (real, i, j, k). Updates
the output argument by reference from a copy of the quaternion.
*/
static void get_euler_from_quaternion(imu_avgs& out, imu_pose_quat q)
{
  // Normalize quaternion to combat sensor drift
  const float qmag = sqrtf(q.r*q.r + q.i*q.i + q.j*q.j + q.k*q.k);
  if (qmag > 0.0f) {
    q.r /= qmag; q.i /= qmag; q.j /= qmag; q.k /= qmag;
  } // Don't divide by zero. If qmag is zero, downstream values are junk anyways

  float sinr_cosp, cosr_cosp, sinp, siny_cosp, cosy_cosp;

  sinr_cosp = 2.0f * (q.r * q.i + q.j * q.k);
  cosr_cosp = 1.0f - 2.0f * (q.i * q.i + q.j * q.j);
  out.pose.roll = atan2f(sinr_cosp, cosr_cosp) * RAD2DEG;

  sinp = 2.0f * (q.r * q.j - q.k * q.i);
  sinp = (sinp > 1.0f) ? 1.0f : (sinp < -1.0f) ? -1.0f : sinp;
  out.pose.pitch = asinf(sinp) * RAD2DEG;

  siny_cosp = 2.0f * (q.r * q.k + q.i * q.j);
  cosy_cosp = 1.0f - 2.0f * (q.j * q.j + q.k * q.k);
  out.pose.yaw = atan2f(siny_cosp, cosy_cosp) * RAD2DEG;
}

uint64_t last_imu_sample_us = 0;
uint64_t last_talk_time_us    = 0;
uint32_t imu_sample_period_us = 100000;
uint32_t telemetry_period_us = 250000;
String t_str;
imu_avgs imu_avg{};

char IMU_BUF[10];

void setup() {
  
    imu.begin_I2C();
    imu.enableReport(SH2_GAME_ROTATION_VECTOR, imu_sample_period_us);
    imu.enableReport(SH2_ACCELEROMETER, imu_sample_period_us);
  
  Serial.begin(115200);
  while (!Serial) {}

}

void loop() {
  const uint64_t now_us = micros();

  if (now_us - last_imu_sample_us >= imu_sample_period_us)
  {
    sensors_imu_tick(now_us);
    last_imu_sample_us = now_us;
  }

  if ((now_us - last_talk_time_us) >= telemetry_period_us)
  {
    
    sensors_get_and_reset_imu_avg(imu_avg);

    t_str.reserve(256);
    t_str = "TIME=" + String(float(millis())/1000.0f, 3) + "|    ";

    dtostrf(imu_avg.pose.roll, 5,0, IMU_BUF);
    t_str += "R=" + String(IMU_BUF) + " | ";
    dtostrf(imu_avg.pose.pitch, 5,0, IMU_BUF);
    t_str += "P=" + String(IMU_BUF) + " | ";
    dtostrf(imu_avg.pose.yaw, 5,0, IMU_BUF);
    t_str += "Y=" + String(IMU_BUF) + " | ";
    dtostrf(imu_avg.accx, 5,2, IMU_BUF);
    t_str += "AX=" + String(IMU_BUF) + " | ";
    dtostrf(imu_avg.accy, 5,2, IMU_BUF);
    t_str += "AY=" + String(IMU_BUF) + " | ";
    dtostrf(imu_avg.accz, 5,2, IMU_BUF);
    t_str += "AZ=" + String(IMU_BUF) + " | ";

    Serial.println(t_str);
    last_talk_time_us = now_us;
  }

}

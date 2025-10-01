/**
 * sensors.cpp
 * Created 9/6/2025
 * 
 * Provides functions to sample ultrasonic, light, and temp sensors, 
 * and offload sampling calculations from ISRs. 
 */

#include "sensors.h"
#include "state.h"

#include "Adafruit_SHTC3.h"
#include "Adafruit_LTR329_LTR303.h"
#include "Adafruit_BNO08x.h"

static Adafruit_SHTC3 shtc3;
static Adafruit_LTR329 ltr;
static Adafruit_BNO08x imu(-1); // -1 to float reset pin in I2C mode, see ds

// Running environmental sensor values and accumulators
static float    temp_c_last   = 0.0f;
static float    rel_hum_last  = 0.0f;
static uint16_t visible_last  = 0;
static uint16_t infrared_last = 0;

static float    temp_c_sum    = 0.0f;
static float    rel_hum_sum   = 0.0f;
static uint32_t visible_sum   = 0;
static uint32_t infrared_sum  = 0;
static uint16_t temp_sensor_sample_count = 0; // N=0 averages are skipped
static uint16_t light_sensor_sample_count = 0;

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

// Ultrasonic accumulators and trigger states
static float    ultra_sum[num_ultrasonics] = {0, 0, 0};
static uint16_t ultra_sample_count = 0; // N=0 averages are skipped
static bool trig_high = false;  // All pulsed at once, should be staggered
static uint32_t last_trig_us = 0;

// Echo edge trackers (used in ISR)
static volatile uint8_t     echo_state[num_ultrasonics] = {0, 0, 0};
static volatile uint32_t echo_start_us[num_ultrasonics] = {0, 0, 0};

/*
Configures light, temp, IMU, and ultrasonic sensors to begin collecting data.
*/
void sensors_setup() 
{
  if (env_sensors_attached) 
  {
    while (!shtc3.begin());
    while (!ltr.begin());
    ltr.setGain(LTR3XX_GAIN_1);
    ltr.setIntegrationTime(LTR3XX_INTEGTIME_400);
    ltr.setMeasurementRate(LTR3XX_MEASRATE_500);
  }

  if (imu_attached)
  {
    imu.begin_I2C();
    imu.enableReport(SH2_GAME_ROTATION_VECTOR, imu_sample_period_us);
    imu.enableReport(SH2_ACCELEROMETER, imu_sample_period_us);
  }

  if (ultrasonics_attached) 
  {
    for (uint8_t i=0;i<num_ultrasonics;i++) 
    {
      pinMode(ultra_trig_pins[i], OUTPUT); 
      digitalWrite(ultra_trig_pins[i], LOW);
      pinMode(ultra_echo_pins[i], INPUT);
    }
  }
}

/*
Takes a reading of environmental sensors and appends them to their 
accumulators. This function should be called every N microseconds, 
where N is the period defined in config.h.
*/
void sensors_env_tick(uint32_t /*now_us*/)
{
  if (!env_sensors_attached) return;

  // Sample SHTC3 sensor
  sensors_event_t hum, tmp;
  shtc3.getEvent(&hum, &tmp);
  temp_c_last = tmp.temperature;
  rel_hum_last = hum.relative_humidity;
  temp_c_sum += temp_c_last;
  rel_hum_sum += rel_hum_last;
  temp_sensor_sample_count++;

  // Sample LTR sensor
  if (ltr.newDataAvailable()) 
  {
    uint16_t vis_plus_ir = 0, ir = 0;
    ltr.readBothChannels(vis_plus_ir, ir);
    visible_last  = (vis_plus_ir > ir) ? (vis_plus_ir - ir) : 0;
    infrared_last = ir;
    visible_sum += visible_last;
    infrared_sum += infrared_last;
    light_sensor_sample_count++;
  }
}

/*
Takes a reading of IMU sensor values and appends them to their accumulators.
Does not accumulate pose quaternion, as this is processed internally on chip.
This function should be called every N microseconds, where N is the period 
defined in config.h.
*/
void sensors_imu_tick(uint32_t /*now_us*/)
{
  if (!imu_attached) return;

  sh2_SensorValue_t imuVals;
  imu.getSensorEvent(&imuVals);

  q_pose_last.r = imuVals.un.gameRotationVector.real;
  q_pose_last.i = imuVals.un.gameRotationVector.i;
  q_pose_last.j = imuVals.un.gameRotationVector.j;
  q_pose_last.k = imuVals.un.gameRotationVector.k;

  accx_last = imuVals.un.accelerometer.x;
  accy_last = imuVals.un.accelerometer.y;
  accz_last = imuVals.un.accelerometer.z; 

  accx_sum += accx_last;
  accy_sum += accy_last;
  accz_sum += accz_last;

  imu_sample_count++;
}

/*
This function is called in bursts. On first call, raises TRIG pins on 
ultrasonic sensors. Then checks repeatedly until pulse duration has
elapsed, after which it samples ultrasonics and adds sample to accumulators.
Resets call interval AFTER taking sample, not after raising TRIG pins.
*/
void sensors_ultrasonics_tick(uint32_t now_us) 
{
  if (!ultrasonics_attached) return;

  // Raise TRIG pins
  if (!trig_high) 
  {
    for (int i = 0; i < num_ultrasonics; i++) 
    {
      digitalWrite(ultra_trig_pins[i], HIGH);
    }
    trig_high = true;
    last_trig_us = now_us;
  }

  // Drop TRIG pins
  if (trig_high && (now_us - last_trig_us) >= trig_pulse_us) 
  {
    for (int i = 0; i < num_ultrasonics; i++) 
    {
      digitalWrite(ultra_trig_pins[i], LOW);
    }
    trig_high = false;

    // Capture current distances (with tearing protection) and accumulate
    float snap[3];
    noInterrupts();
    for (int i = 0; i < num_ultrasonics; i++) snap[i] = ultrasonic_cm[i];
    interrupts();
    for (int i = 0; i < num_ultrasonics; i++) ultra_sum[i] += snap[i];
    ultra_sample_count++;

    last_ultra_sample_us = now_us;
  }
}

/*
Takes an average of the last N environmental sensor readings, packages them
into a struct, and resets the accumulators. Struct is then sent to Raspberry
Pi with the rest of the telemetry externally.
*/
void sensors_get_and_reset_env_avg(sensor_avgs& out)
{
  const uint16_t n1 = temp_sensor_sample_count;
  out.temp_c  = n1 ? (temp_c_sum / n1) : 0.0f;
  out.rel_hum = n1 ? (rel_hum_sum / n1) : 0.0f;
  const uint16_t n2 = light_sensor_sample_count;
  out.visible = n2 ? uint16_t(visible_sum / n2) : 0;
  out.infrared= n2 ? uint16_t(infrared_sum / n2) : 0;

  temp_c_sum = 0.0f;
  rel_hum_sum = 0.0f;
  visible_sum = 0;
  infrared_sum = 0;
  temp_sensor_sample_count   = 0;
  light_sensor_sample_count  = 0;
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
Takes an average of the last N ultrasonic readings and resets the accumulators.
Averages are then sent to Raspberry Pi with the rest of telemetry externally.
*/
void sensors_get_and_reset_ultra_avg(float out_cm[num_ultrasonics])
{
  const uint16_t n = ultra_sample_count;
  for (int i = 0; i < num_ultrasonics; i++)
  {
    out_cm[i] = n ? (ultra_sum[i] / n) : 0.0f;
    ultra_sum[i] = 0.0f;
  }
  ultra_sample_count = 0;
}

/*
Handles interrupts generated by pulses from the ECHO pins of the ultrasonic
sensors. Calculates and records distance measurements. Three ultrasonics are
wired to pins in PCINT0 register.
*/
void sensors_handle_pcint0_echoes()
{
  if (!ultrasonics_attached) return;

  for (int i = 0; i < num_ultrasonics; i++)
  {
    const uint8_t lvl = digitalRead(ultra_echo_pins[i]);
    if (lvl && !echo_state[i])
    {
      echo_start_us[i] = micros();
      echo_state[i] = 1;
    } 
    else if (!lvl && echo_state[i])
    {
      const uint32_t dt_us = micros() - echo_start_us[i];
      ultrasonic_cm[i] = float(dt_us) / 1000000
                      * speed_of_sound_mps * 100
                      / 2;
      echo_state[i] = 0;
    }
  }
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
  out.pose.roll = rad2deg(atan2f(sinr_cosp, cosr_cosp), 2);

  sinp = 2.0f * (q.r * q.j - q.k * q.i);
  sinp = (sinp > 1.0f) ? 1.0f : (sinp < -1.0f) ? -1.0f : sinp;
  out.pose.pitch = rad2deg(asinf(sinp), 2);

  siny_cosp = 2.0f * (q.r * q.k + q.i * q.j);
  cosy_cosp = 1.0f - 2.0f * (q.j * q.j + q.k * q.k);
  out.pose.yaw = rad2deg(atan2f(siny_cosp, cosy_cosp), 2);
}
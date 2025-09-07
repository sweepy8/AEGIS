// sensors.cpp
#include "sensors.h"
#include "state.h"

#include "Adafruit_SHTC3.h"
#include "Adafruit_LTR329_LTR303.h"
static Adafruit_SHTC3 shtc3;
static Adafruit_LTR329 ltr;

// env running values & accumulators (main thread only) 
static float    temp_c_last   = 0.0f;
static float    rel_hum_last  = 0.0f;
static uint16_t visible_last  = 0;
static uint16_t infrared_last = 0;

static float    temp_c_sum       = 0.0f;
static float    rel_hum_sum      = 0.0f;
static uint32_t visible_sum      = 0;
static uint32_t infrared_sum     = 0;
static uint16_t env_sample_count = 0;

// ultrasonic accumulators (main thread only) 
static float    ultra_sum[num_ultrasonics] = {0,0,0};
static uint16_t ultra_sample_count = 0;

// ultrasonic trigger state (main thread only) 
static bool trig_high = false;
static uint32_t last_trig_us = 0;

// echo edge tracking (ISR shared local state lives here) 
static volatile uint8_t     echo_state[num_ultrasonics] = {0,0,0};
static volatile uint32_t echo_start_us[num_ultrasonics] = {0,0,0};

void sensors_setup() 
{
  if (sensors_attached) 
  {
    while (!shtc3.begin());
    while (!ltr.begin());
    ltr.setGain(LTR3XX_GAIN_1);
    ltr.setIntegrationTime(LTR3XX_INTEGTIME_400);
    ltr.setMeasurementRate(LTR3XX_MEASRATE_500);
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

void sensors_env_tick(uint32_t /*now_us*/)
{
  if (!sensors_attached) return;

  sensors_event_t hum, tmp;
  shtc3.getEvent(&hum, &tmp);
  temp_c_last = tmp.temperature;
  rel_hum_last = hum.relative_humidity;

  uint16_t vis_plus_ir = 0, ir = 0;
  if (ltr.newDataAvailable()) 
  {
    ltr.readBothChannels(vis_plus_ir, ir);
    visible_last  = (vis_plus_ir > ir) ? (vis_plus_ir - ir) : 0;
    infrared_last = ir;
  }

  temp_c_sum += temp_c_last;
  rel_hum_sum += rel_hum_last;
  visible_sum += visible_last;
  infrared_sum += infrared_last;
  env_sample_count++;
}

void sensors_ultrasonics_tick(uint32_t now_us) 
{
  if (!ultrasonics_attached) return;

  // raise 10us pulse
  if (!trig_high) 
  {
    for (int i = 0; i < num_ultrasonics; i++) 
    {
      digitalWrite(ultra_trig_pins[i], HIGH);
    }
    trig_high = true;
    last_trig_us = now_us;
  }
  // drop 10us pulse
  if (trig_high && (now_us - last_trig_us) >= trig_pulse_us) 
  {
    for (int i = 0; i < num_ultrasonics; i++) 
    {
      digitalWrite(ultra_trig_pins[i], LOW);
    }
    trig_high = false;

    // snapshot current instantaneous distances and accumulate
    float snap[3];
    noInterrupts();
    for (int i = 0; i < num_ultrasonics; i++) snap[i] = ultrasonic_cm[i];
    interrupts();
    for (int i = 0; i < num_ultrasonics; i++) ultra_sum[i] += snap[i];
    ultra_sample_count++;
  }
}

void sensors_get_and_reset_env_avg(sensor_avgs& out) {
  const uint16_t n = env_sample_count;
  out.temp_c  = n ? (temp_c_sum / n) : 0.0f;
  out.rel_hum = n ? (rel_hum_sum / n) : 0.0f;
  out.visible = n ? uint16_t(visible_sum / n) : 0;
  out.infrared= n ? uint16_t(infrared_sum / n) : 0;

  temp_c_sum = rel_hum_sum = 0.0f;
  visible_sum = infrared_sum = 0;
  env_sample_count = 0;
}

void sensors_get_and_reset_ultra_avg(float out_cm[num_ultrasonics]) {
  const uint16_t n = ultra_sample_count;
  for (int i=0;i<num_ultrasonics;i++) {
    out_cm[i] = n ? (ultra_sum[i] / n) : 0.0f;
    ultra_sum[i] = 0.0f;
  }
  ultra_sample_count = 0;
}

// called by ISR(PCINT0_vect) in motors.cpp
void sensors_handle_pcint0_echoes() {
  if (!ultrasonics_attached) return;

  for (int i=0;i<num_ultrasonics;i++) {
    const uint8_t lvl = digitalRead(ultra_echo_pins[i]);
    if (lvl && !echo_state[i]) {
      echo_start_us[i] = micros();
      echo_state[i] = 1;
    } else if (!lvl && echo_state[i]) {
      const uint32_t dt_us = micros() - echo_start_us[i];
      // store instantaneous cm (float). One 32-bit write; readers snapshot with short irq-off.
      ultrasonic_cm[i] = (speed_of_sound_mps * 100.0f) * (float(dt_us) / 1000000.0f) / 2.0f;
      echo_state[i] = 0;
    }
  }
}

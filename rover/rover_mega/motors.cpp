// motors.cpp
#include <avr/interrupt.h>
#include "motors.h"
#include "config.h"
#include "state.h"

// patterns (LF, LR, RF, RR)
static const uint8_t  stop_pattern[4]      = {0,0,0,0};
static const uint8_t  fwd_pattern[4]       = {1,0,1,0};
static const uint8_t  rev_pattern[4]       = {0,1,0,1};
static const uint8_t  left_spin_pattern[4] = {0,1,1,0};
static const uint8_t  right_spin_pattern[4]= {1,0,0,1};

// encoder rpm accumulators (main thread only)
static float   rpm_sum[6]   = {0,0,0,0,0,0};
static uint16_t rpm_count    = 0;
// latest instantaneous rpm (useful to keep; not volatile)
static float   rpm_inst[6]  = {0,0,0,0,0,0};

static inline void set_rpm_pwm(uint8_t pin, uint8_t rpm) {
  analogWrite(pin, map(rpm, min_rpm, max_rpm, min_pw, max_pw));
}

void motors_setup() {
  for (uint8_t i=0;i<4;i++) { pinMode(driver_pins[i], OUTPUT); analogWrite(driver_pins[i], 0); }

  // encoder pins
  for (int i=0;i<6;i++) {
    pinMode(enc_a_pins[i], INPUT_PULLUP);
    pinMode(enc_b_pins[i], INPUT_PULLUP);
  }
}

void motors_move(move_dir dir, uint8_t rpm) {
  switch (dir) {
    case move_dir::stop:       for (int i=0;i<4;i++) set_rpm_pwm(driver_pins[i], uint8_t(rpm *      stop_pattern[i])); break;
    case move_dir::forward:    for (int i=0;i<4;i++) set_rpm_pwm(driver_pins[i], uint8_t(rpm *       fwd_pattern[i])); break;
    case move_dir::reverse:    for (int i=0;i<4;i++) set_rpm_pwm(driver_pins[i], uint8_t(rpm *       rev_pattern[i])); break;
    case move_dir::left_spin:  for (int i=0;i<4;i++) set_rpm_pwm(driver_pins[i], uint8_t(rpm * left_spin_pattern[i])); break;
    case move_dir::right_spin: for (int i=0;i<4;i++) set_rpm_pwm(driver_pins[i], uint8_t(rpm * right_spin_pattern[i]));break;
  }
}
void motors_stop() { motors_move(move_dir::stop, 0); }

void motors_encoder_tick(uint32_t /*now_us*/) {
  // Capture and clear motor encoder pulses (disable interrupts to avoid tears)
  uint16_t counts[6];
  noInterrupts();
  for (int i = 0; i < 6; i++) 
  {
    counts[i] = enc_pulse_counts[i];
    enc_pulse_counts[i] = 0;
  }
  interrupts();

  const float window_s = encoder_sample_period_us / 1000000;
  for (int i = 0; i < 6; i++)
  {
    const float inst = float(counts[i]) 
                      / enc_pulses_per_rev 
                      / window_s 
                      * enc_gear_ratio 
                      * 60;
    rpm_inst[i] = inst;
    rpm_sum[i] += inst;
  }
  rpm_count++;
}

void motors_get_and_reset_rpm_avg(float out_avg_rpm[6]) {
  for (int i = 0; i < 6; i++) 
  {
    out_avg_rpm[i] = rpm_count ? (rpm_sum[i] / rpm_count) : 0.0f;
    rpm_sum[i] = 0.0f;
  }
  rpm_count = 0;
}

void motors_handle_pcint0_encoders() {
  // Encoders on PB4..PB7  -> positions {0,1,2,5}
  static const uint8_t pos[4]    = { 0, 1, 2, 5};
  static const uint8_t a_pins[4] = {12,13,11,10};
  static const uint8_t b_pins[4] = {44,46,48,43};
  static uint8_t a_state[4] =      { 0, 0, 0, 0};

  for (int i = 0; i < 4; i++) 
  {
    const uint8_t a = digitalRead(a_pins[i]);
    if (a && !a_state[i]) 
    {
      enc_pulse_counts[pos[i]]++;
      const uint8_t b = digitalRead(b_pins[i]);
      enc_directions[pos[i]] = (!b) ? 1 : 0;
      a_state[i] = 1;
    } 
    else if (!a && a_state[i]) { a_state[i] = 0; }
  }
}

void motors_handle_pcint1_encoders() {
  // Encoders on PJ0, PJ1
  static const uint8_t pos[2]    = { 3, 4};
  static const uint8_t a_pins[2] = {15,14};
  static const uint8_t b_pins[2] = {41,39};
  static uint8_t a_state[2]      = { 0, 0};

  for (int i = 0; i < 2; i++) 
  {
    const uint8_t a = digitalRead(a_pins[i]);
    if (a && !a_state[i]) 
    {
      enc_pulse_counts[pos[i]]++;
      const uint8_t b = digitalRead(b_pins[i]);
      enc_directions[pos[i]] = (!b) ? 1 : 0;
      a_state[i] = 1;
    } 
    else if (!a && a_state[i]) { a_state[i] = 0; }
  }
}
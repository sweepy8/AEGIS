/**
 * motors.cpp
 * Created 9/6/2025
 * 
 * Provides movement patterns and functions that generate PWM signals, sample 
 * and reset encoders, and offload sampling calculations from ISRs.
 */

#include <avr/interrupt.h>
#include "motors.h"
#include "config.h"
#include "state.h"

// Movement patterns                          LF, LR, RF, RR
static const uint8_t stop_pattern[4]       = { 0,  0,  0,  0};
static const uint8_t fwd_pattern[4]        = { 1,  0,  1,  0};
static const uint8_t rev_pattern[4]        = { 0,  1,  0,  1};
static const uint8_t left_spin_pattern[4]  = { 0,  1,  1,  0};
static const uint8_t right_spin_pattern[4] = { 1,  0,  0,  1};

static float rpm_inst[6] = {0,0,0,0,0,0};   // Latest instantaneous rpm
static float rpm_sum[6] = {0,0,0,0,0,0};    // Encoder rpm accumulators
static uint16_t rpm_count = 0;              // Ensures n=0 averages are skipped

static inline void set_rpm_pwm(uint8_t pin, uint8_t rpm)
{
  analogWrite(pin, map(rpm, min_rpm, max_rpm, min_pw, max_pw));
}

void motors_setup()
{
  // PWM pins
  for (int i = 0; i < 4; i++)
  {
    pinMode(driver_pins[i], OUTPUT);
    analogWrite(driver_pins[i], 0);
  }

  // Encoder pins
  for (int i=0;i<6;i++) {
    pinMode(enc_a_pins[i], INPUT_PULLUP);
    pinMode(enc_b_pins[i], INPUT_PULLUP);
  }
}

void motors_move(move_dir dir, uint8_t rpm)
{
  uint8_t* pattern = stop_pattern;
  switch (dir)
  {
    case move_dir::stop:       pattern = stop_pattern;       break;
    case move_dir::forward:    pattern = fwd_pattern;        break;
    case move_dir::reverse:    pattern = rev_pattern;        break;
    case move_dir::left_spin:  pattern = left_spin_pattern;  break;
    case move_dir::right_spin: pattern = right_spin_pattern; break;
    default:                   pattern = stop_pattern;       break;
  }

  for (int i = 0; i < 4; i++)
    set_rpm_pwm(driver_pins[i], uint8_t(rpm * *(pattern + i)));
}

void motors_stop() { motors_move(move_dir::stop, 0); }

void motors_encoder_tick()
{
  // Capture and clear encoder pulses (disable interrupts to avoid tearing)
  uint16_t counts[6];
  noInterrupts();
  for (int i = 0; i < 6; i++) 
  {
    counts[i] = enc_pulse_counts[i];
    enc_pulse_counts[i] = 0;
  }
  interrupts();

  const float window_s = 0.1f;
  for (int i = 0; i < 6; i++)
  {
    const float inst = float(counts[i]) 
                      / enc_pulses_per_rev 
                      / window_s 
                      * 60;
    rpm_inst[i] = inst;
    rpm_sum[i] += inst;
  }
  rpm_count++;
}

void motors_get_and_reset_rpm_avg(float out_avg_rpm[6])
{
  for (int i = 0; i < 6; i++) 
  {
    out_avg_rpm[i] = rpm_count ? (rpm_sum[i] / rpm_count) : 0.0f;
    rpm_sum[i] = 0.0f;
  }
  rpm_count = 0;
}

void motors_handle_pcint0_encoders()
{
  // Encoders on PB4-PB7
  static const uint8_t pos[4]    = { 0, 1, 2, 5};
  static const uint8_t a_pins[4] = {12,13,11,10};
  static const uint8_t b_pins[4] = {44,46,48,43};
  static uint8_t a_state[4]      = { 0, 0, 0, 0};

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

void motors_handle_pcint1_encoders()
{
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

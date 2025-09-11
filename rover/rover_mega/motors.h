/**
 * motors.h
 * Created 9/6/2025
 * 
 * Provides movement patterns and functions that generate PWM signals, sample 
 * and reset encoders, and offload sampling calculations from ISRs.
 */

#ifndef AEGIS_MOTORS_H
#define AEGIS_MOTORS_H
#include <Arduino.h>

enum class move_dir : uint8_t {stop, forward, reverse, left_spin, right_spin};

void motors_setup();
void motors_move(move_dir dir, uint8_t rpm);
void motors_stop();

// called from loop: turn encoder pulses into instantaneous rpm & accumulate
void motors_encoder_tick();

// return 1-second rpm averages (and reset accumulators)
void motors_get_and_reset_rpm_avg(float out_avg_rpm[6]);

void motors_handle_pcint0_encoders();
void motors_handle_pcint1_encoders();
#endif

/**
 * config.h
 * Created 9/6/2025
 * 
 * Holds all pins, parameters, and flags used by other source files.
 */

#ifndef AEGIS_CONFIG_H
#define AEGIS_CONFIG_H
#include <Arduino.h>

// Subsytem Flags
constexpr bool uart_attached        = true;
constexpr bool motors_attached      = true;
constexpr bool sensors_attached     = false;    // SHTC3 + LTR-329
constexpr bool ultrasonics_attached = true;

// Serial Parameters
constexpr uint32_t mega_baudrate = 460800;     // Baud of serial
constexpr uint32_t ugv_baudrate  = 115200;     // Baud of serial1

// Timing Parameters
constexpr uint32_t telemetry_period_us         = 1000000;  // 1  Hz
constexpr uint32_t ultrasonic_sample_period_us =  100000;  // 10 Hz
constexpr uint32_t sensor_sample_period_us     =  100000;  // 10 Hz
constexpr uint32_t encoder_sample_period_us    =  100000;  // 10 Hz
constexpr uint32_t command_threshold_us        =   50000;  // 20 Hz

// Encoder Characteristics
constexpr float enc_pulses_per_rev = 753.2 / 4; // Four "events", see datasheet
constexpr float enc_gear_ratio     = 26.9;      // Encoder vs. motor shaft

// Motor Constraints
constexpr uint8_t min_rpm = 0;
constexpr uint8_t max_rpm = 223;
constexpr uint8_t min_pw  = 0;
constexpr uint8_t max_pw  = 255;

// Motor Pins
constexpr uint8_t left_fwd  = 3;
constexpr uint8_t left_rvs  = 4;
constexpr uint8_t right_fwd = 7;
constexpr uint8_t right_rvs = 6;
constexpr uint8_t driver_pins[4] = {left_fwd, left_rvs, right_fwd, right_rvs};

// Encoder Pins                    LF, LM, LR, RF, RM, RR
constexpr uint8_t enc_a_pins[6] = {12, 13, 11, 14, 15, 10};
constexpr uint8_t enc_b_pins[6] = {44, 46, 48, 39, 41, 43};

// Ultrasonic Pins, Parameters
constexpr uint8_t  num_ultrasonics = 3;
constexpr uint8_t  ultra_trig_pins[num_ultrasonics] = {47, 49, 45};
constexpr uint8_t  ultra_echo_pins[num_ultrasonics] = {52, 53, 51};
constexpr uint32_t trig_pulse_us = 10;
constexpr int      safe_dist_cm = -100; // Currently effectively disabled
constexpr float    speed_of_sound_mps = 345.0;   // 343 @ 20C + 0.6 per degC

#endif

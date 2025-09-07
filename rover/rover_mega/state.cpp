// state.cpp
#include "state.h"

// Initialize times to zero
uint32_t last_command_time_us   = 0;
uint32_t last_move_time_us      = 0;
uint32_t last_ultra_sample_us   = 0;
uint32_t last_env_sample_us     = 0;
uint32_t last_encoder_sample_us = 0;
uint32_t last_talk_time_us      = 0;

bool ugv_is_moving       = false;
bool skip_first_telemetry = true;

volatile uint16_t enc_pulse_counts[6] = {0,0,0,0,0,0};
volatile uint8_t enc_directions[6]    = {0,0,0,0,0,0};
volatile float ultrasonic_cm[num_ultrasonics] = {0,0,0};

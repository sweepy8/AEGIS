/**
 * sensors.h
 * Created 9/6/2025
 * 
 * Provides functions to sample ultrasonic, light, and temp sensors, 
 * and offload sampling calculations from ISRs. 
 */

#ifndef AEGIS_SENSORS_H
#define AEGIS_SENSORS_H
#include <Arduino.h>
#include "config.h"

// environment (SHTC3 + LTR-329) sampling
struct sensor_avgs {
  float    temp_c = 0.0f;
  float    rel_hum = 0.0f;
  uint16_t visible = 0;
  uint16_t infrared = 0;
};

void sensors_setup();

// called at 10 Hz
void sensors_env_tick(uint32_t now_us);
void sensors_ultrasonics_tick(uint32_t now_us);

// 1 s averages (and reset)
void sensors_get_and_reset_env_avg(sensor_avgs& out);
void sensors_get_and_reset_ultra_avg(float out_cm[num_ultrasonics]);

// PCINT0 echo handler called by motors' ISR
void sensors_handle_pcint0_echoes();

#endif

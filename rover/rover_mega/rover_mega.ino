/**
 * rover_mega.ino
 * Created 9/6/2025
 * 
 * The Arduino equivalent of main.cpp. Contains setup() and loop() functions.
 * Calls functions to configure attached subsystems and opens serial ports. 
 * Once they are open, enters main loop which periodically samples sensors and
 * encoders, performs commands, and transmits telemetry once per second.
 * 
 * NOTE: To flash the Mega using the Raspberry Pi command line:
 *    0. Install arduino-cli (see docs), plug in Arduino, go to the repo root
 *    1. arduino-cli compile --fqbn arduino:avr:mega ./rover/rover_mega
 *    2. arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:avr:mega ./rover/rover_mega
 *    3. arduino-cli monitor -p /dev/ttyACM0 -b arduino:avr:mega -c 230400
 * NOTE: Step 3 will only work if you uncomment the serial print in uart.cpp. 
 *    Make sure that the baudrate matches the baudrate in config.h.
 * NOTE: Serial prints are slow as hell. Don't use them if you can avoid it. 
 *    They will slow down the entire telemetry system severely. If you do, 
 *    stick to the highest baud you can. I had success with 460,800 bps.
 */

#include <Arduino.h>

#include "config.h"
#include "interrupts.h"
#include "state.h"
#include "uart.h"
#include "motors.h"
#include "sensors.h"

void setup() 
{
  if (motors_attached)                          { motors_setup(); }
  if (ultrasonics_attached || sensors_attached) { sensors_setup(); }
  if (motors_attached || sensors_attached)      { interrupts_setup(); }
  if (uart_attached) 
  {
    Serial.begin(mega_baudrate);
    Serial1.begin(ugv_baudrate);
    while (!Serial1) {}
  }
}

void loop() 
{
  const uint64_t now_us = micros();

  // Periodic Sampling
  if (ultrasonics_attached 
    && (now_us - last_ultra_sample_us) >= ultrasonic_sample_period_us) 
  {
    sensors_ultrasonics_tick(now_us);
    last_ultra_sample_us = now_us;
  }
  if (sensors_attached 
    && (now_us - last_env_sample_us) >= sensor_sample_period_us) 
  {
    sensors_env_tick(now_us);
    last_env_sample_us = now_us;
  }
  if (motors_attached 
    && (now_us - last_encoder_sample_us) >= encoder_sample_period_us) 
  {
    motors_encoder_tick(now_us);
    last_encoder_sample_us = now_us;
  }

  // Recieve Movement Command
  if (uart_attached) 
  {
    if (now_us - last_command_time_us > command_threshold_us) 
    { 
      uart_do_command();
    } 
    // This prevents jerking due to millisecond gap between commands
    else if (ugv_is_moving 
          && (now_us - last_move_time_us > (3 * command_threshold_us))) 
    {
      motors_stop();
      ugv_is_moving = false;
      last_move_time_us = now_us;
    }
  }

  // Send Telemetry String
  if (uart_attached 
    && (now_us - last_talk_time_us) >= telemetry_period_us) 
  {
    if (skip_first_telemetry) 
    { 
        skip_first_telemetry = false;
        last_talk_time_us = now_us; 
    }
    else { uart_send_telemetry(); } // updates last_talk_time_us internally
  }
}

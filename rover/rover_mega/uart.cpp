// uart.cpp
#include "uart.h"
#include "config.h"
#include "state.h"
#include "motors.h"
#include "sensors.h"

static const char* motor_names[6]      = {"LF","LM","LR","RF","RM","RR"};
static const char* ultrasonic_names[5] = {"USLI","USLF","USCT","USRT","USRR"};

void uart_do_command() 
{
  last_command_time_us = micros();

  if (Serial1.available() < 3) return;

  uint8_t cmd[3];
  for (int i = 0; i < 3; i++) cmd[i] = uint8_t(Serial1.read());
  const uint8_t opcode = (cmd[0] >> 6) & 0x03;

  switch (opcode) 
  {
    case 2: // TURN
    { 
      const move_dir spin = (cmd[0] & 0x01) 
                            ? move_dir::right_spin 
                            : move_dir::left_spin;
      const uint8_t rpm = map(cmd[1], min_pw, max_pw, min_rpm, max_rpm);

      // verify that it is safe to turn
      bool ok = !ultrasonics_attached;
      if (!ok) 
      {
        // get latest distances (with tear protection)
        float d0, d1, d2;
        noInterrupts();
        d0 = ultrasonic_cm[0]; d1 = ultrasonic_cm[1]; d2 = ultrasonic_cm[2];
        interrupts();
        ok = (d0 >= safe_dist_cm && d1 >= safe_dist_cm && d2 >= safe_dist_cm);
      }
      if (ok) 
      {
        motors_move(spin, rpm);
        last_move_time_us = micros();
        ugv_is_moving = true;
      }
      break;
    }
    case 3: // MOVE
    { 
      const move_dir dir = (cmd[0] & 0x01) 
                           ? move_dir::reverse 
                           : move_dir::forward;
      const uint8_t rpm  = map(cmd[1], min_pw, max_pw, min_rpm, max_rpm);

      // verify that it is safe to move
      bool ok = !ultrasonics_attached || dir == move_dir::reverse;
      if (!ok) 
      {
        float d0, d1, d2;
        noInterrupts();
        d0 = ultrasonic_cm[0]; d1 = ultrasonic_cm[1]; d2 = ultrasonic_cm[2];
        interrupts();
        ok = (d0 > safe_dist_cm && d1 > safe_dist_cm && d2 > safe_dist_cm);
      }
      if (ok) 
      {
        motors_move(dir, rpm);
        last_move_time_us = micros();
        ugv_is_moving = true;
      }
      break;
    }
    default: break;
  }
}

void uart_send_telemetry() 
{
  // gather & reset 1s averages
  float rpm_avg[6];         motors_get_and_reset_rpm_avg(rpm_avg);

  float us_avg[3] = {0,0,0}; 
  if (ultrasonics_attached) sensors_get_and_reset_ultra_avg(us_avg);

  sensor_avgs env{};
  if (sensors_attached)     sensors_get_and_reset_env_avg(env);

  // build telemetry string
  String t_str; 
  t_str.reserve(256);
  t_str  = "TIME=" + String(float(millis())/1000.0f, 3) + "|";

  if (motors_attached) 
  {
    for (int i=0;i<6;i++) 
    {
      t_str += motor_names[i];  t_str += "V=0|";  // placeholders for future meters
      t_str += motor_names[i];  t_str += "A=0|";
      t_str += motor_names[i];  t_str += "R="; 
      int rpm_i = int(rpm_avg[i] + (rpm_avg[i] >= 0 ? 0.5f : -0.5f)); // round
      t_str += String(rpm_i);
      t_str += "|";
    }
  } 
  else 
  {
    t_str += "LFV=0|LFA=0|LFR=0|LMV=0|LMA=0|LMR=0|LRV=0|LRA=0|LRR=0|"
             "RFV=0|RFA=0|RFR=0|RMV=0|RMA=0|RMR=0|RRV=0|RRA=0|RRR=0|";
  }

  if (ultrasonics_attached) 
  {
    t_str += String(ultrasonic_names[0]) + "=" + String(us_avg[0], 1) + "|";
    t_str += String(ultrasonic_names[1]) + "=" + String(us_avg[1], 1) + "|";
    t_str += String(ultrasonic_names[2]) + "=" + String(us_avg[2], 1) + "|";
  } 
  else { t_str += "USLI=0|USLF=0|USCT=0|USRT=0|USRR=0|"; }

  t_str  += "GR=0|GP=0|GY=0|AX=0|AY=0|AZ=0|";    // IMU placeholders

  if (sensors_attached) 
  {
    t_str += "TEMP=" + String(env.temp_c, 1)  + "|";
    t_str += "RHUM=" + String(env.rel_hum, 2) + "|";
    t_str += "LVIS=" + String(env.visible)    + "|";
    t_str += "LINF=" + String(env.infrared)   + "|";
  }
  else { t_str += "TEMP=0|RHUM=0|LVIS=0|LINF=0|"; }

  //Serial.println(t_str);        // Displays telemetry string over USB
  Serial1.println(t_str);         // Sends telemetry string to Raspberry Pi
  last_talk_time_us = micros();
}

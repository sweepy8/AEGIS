// Arduino to R.Pi Communication Driver (Version 2)
// AEGIS Senior Design, 7/21/2025

// Designed for Arduino MEGA and R.Pi 5
// Uses Serial1 TX/RX on pins 18/19
// and motor control on 4, 5, 6, and 7

#include <stdio.h>

// GENERAL DEFINITIONS --------------------------------------------------------------------------------------

#define SPEED_OF_SOUND_MPS 343.0    //331 + 0.69 * Temp (Celsius)

#define UART_ATTACHED         1
#define MOTORS_ATTACHED       1
#define ULTRASONICS_ATTACHED  1

#define UGV_BAUDRATE 115200

#define COMMAND_THRESHOLD_US   50000
#define SAMPLE_THRESHOLD_US    500000
#define TELEMETRY_THRESHOLD_US 1000000

uint32_t last_command_time_us = 0;
uint32_t last_move_time_us = 0;
uint32_t last_sample_time_us = 0;
uint32_t last_talk_time_us = 0;
bool ugv_is_moving = false;

// MOTOR FLAGS & DATA ---------------------------------------------------------------------------------------
 
#define MIN_RPM 0
#define MAX_RPM 223
#define MIN_PW 0
#define MAX_PW 255
#define MOVE_INCREMENT_US 50000

#define LEFT_PWM_F  4
#define LEFT_PWM_R  5
#define RIGHT_PWM_F 6
#define RIGHT_PWM_R 7
uint8_t DRIVER_PINS[4] = { LEFT_PWM_F, LEFT_PWM_R, RIGHT_PWM_F, RIGHT_PWM_R };

//                                  LF,  LR,  RF,  RR
uint8_t stop_pattern[4]         = {  0,   0,   0,   0};
uint8_t forward_pattern[4]      = {  1,   0,   1,   0};
uint8_t reverse_pattern[4]      = {  0,   1,   0,   1};
float   left_arc_pattern[4]     = {0.3,   0,   1,   0};   // Left, right arc won't work until closed loop PID
float   right_arc_pattern[4]    = {  1,   0, 0.3,   0};
uint8_t left_spin_pattern[4]    = {  0,   1,   1,   0};
uint8_t right_spin_pattern[4]   = {  1,   0,   0,   1};

volatile uint8_t rpm;

// ULTRASONIC FLAGS & DATA ----------------------------------------------------------------------------------

#define NUM_ULTRASONICS 3
#define SAFE_DISTANCE_CM -100
#define PULSE_DURATION_US 10

uint8_t ULTRASONIC_TRIG_PINS[NUM_ULTRASONICS] = {48, 50, 52};
uint8_t ULTRASONIC_ECHO_PINS[NUM_ULTRASONICS] = { 3, 21,  2};

volatile double ultrasonic_distances_cm[NUM_ULTRASONICS] = {0, 0, 0};

// UART RECIEVER & MOVEMENT FUNCTIONS -----------------------------------------------------------------------

// Decodes 3-byte command from the Raspberry Pi serial connection and performs an associated operation.
void do_rpi_command() 
{
  last_command_time_us = micros();

  static uint8_t command[] = {0, 0, 0};

  if (Serial1.available() < 3) { return; }

  for (int idx = 0; idx < 3; idx++) { command[idx] = Serial1.read(); }

  int opcode = (command[0] & 0xC0) / pow(2,6);  // gives opcode in range [0,3] from 2 MSBs

  switch (opcode)
  {
    case 2: // TURN
    {
      String dir = (command[0] & 0x01) ? "right spin" : "left spin";
      uint8_t  spd = map(command[1], MIN_PW, MAX_PW, MIN_RPM, MAX_RPM);
      //uint16_t dur = command[2] * MOVE_INCREMENT_MS;    // CURRENTLY UNUSED

      if((ultrasonic_distances_cm[0] >= SAFE_DISTANCE_CM && 
          ultrasonic_distances_cm[1] >= SAFE_DISTANCE_CM &&
          ultrasonic_distances_cm[2] >= SAFE_DISTANCE_CM)    ||
          !(ULTRASONICS_ATTACHED))
      {
        move_rover(dir, spd);
        last_move_time_us = micros();
        ugv_is_moving = true;
      }

      break;
    }
    case 3: // MOVE
    {
      String   dir = (command[0] & 0x01) ? "reverse" : "forward";
      uint8_t  spd = map(command[1], MIN_PW, MAX_PW, MIN_RPM, MAX_RPM);
      //uint16_t dur = command[2] * MOVE_INCREMENT_MS;    // CURRENTLY UNUSED

      // If all ultrasonics report safe forward movement
      // OR you're reversing OR no ultrasonics are connected
      if((ultrasonic_distances_cm[0] > SAFE_DISTANCE_CM &&
          ultrasonic_distances_cm[1] > SAFE_DISTANCE_CM &&
          ultrasonic_distances_cm[2] > SAFE_DISTANCE_CM)   ||
          (dir == "reverse")   ||
          !(ULTRASONICS_ATTACHED))
      {
        move_rover(dir, spd);
        last_move_time_us = micros();
        ugv_is_moving = true;
      }

      break;
    }
  }
  
  for (int i = 0; i < 3; i++) { command[i] = 0; }
}

// Sets rpm of each motor driver input in accordance with predefined movement patterns.
void move_rover(String dir, uint8_t rpm)
{
  int i;
  if      (dir == "stop")       { for (i = 0; i < 4; i++) { set_rpm( DRIVER_PINS[i], rpm * stop_pattern[i]);       } }
  else if (dir == "forward")    { for (i = 0; i < 4; i++) { set_rpm( DRIVER_PINS[i], rpm * forward_pattern[i]);    } }
  else if (dir == "reverse")    { for (i = 0; i < 4; i++) { set_rpm( DRIVER_PINS[i], rpm * reverse_pattern[i]);    } }
  else if (dir == "left arc")   { for (i = 0; i < 4; i++) { set_rpm( DRIVER_PINS[i], rpm * left_arc_pattern[i]);   } }
  else if (dir == "right arc")  { for (i = 0; i < 4; i++) { set_rpm( DRIVER_PINS[i], rpm * right_arc_pattern[i]);  } }
  else if (dir == "left spin")  { for (i = 0; i < 4; i++) { set_rpm( DRIVER_PINS[i], rpm * left_spin_pattern[i]);  } }
  else if (dir == "right spin") { for (i = 0; i < 4; i++) { set_rpm( DRIVER_PINS[i], rpm * right_spin_pattern[i]); } }
}

// Stops rover via a call to the move_rover function.
void stop(void) { move_rover("stop", 0); }

// Maps rpm input to PWM value between 0 and 255, then writes that value to the pin input
void set_rpm(int pin, uint8_t rpm) { analogWrite(pin, map(rpm, MIN_RPM, MAX_RPM, MIN_PW, MAX_PW)); }

// ULTRASONIC SENSOR FUNCTIONS ------------------------------------------------------------------------------

// Pulses the ultrasonic trigger pins.
void sample_ultrasonics(uint32_t curr_time_us) 
{
  static bool triggers_high = false;

  // Set trigger pins high every elapsed sample period
  if (!triggers_high && (curr_time_us - last_sample_time_us >= SAMPLE_THRESHOLD_US)) {
    for(int i = 0; i < NUM_ULTRASONICS; i++) { digitalWrite(ULTRASONIC_TRIG_PINS[i], HIGH); }
    triggers_high = true;
  }

  // ECHO pins are handled by interrupt, see ultrasonic_echo_handler function for more

  // Reset trigger pins every elapsed sample period + pulse duration
  if (triggers_high && ((curr_time_us - last_sample_time_us) >= (SAMPLE_THRESHOLD_US + PULSE_DURATION_US)))
  {
    for(int i = 0; i < NUM_ULTRASONICS; i++) { digitalWrite(ULTRASONIC_TRIG_PINS[i], LOW); }
    triggers_high = false;

    last_sample_time_us = micros();
  }
}

// ISR for changes on the ultrasonic echo pins. Captures echo pulse width and computes distance values.
void ultrasonic_echo_handler() 
{
  static bool reading_echo_pin[NUM_ULTRASONICS] = {false, false, false};
  static uint32_t echo_rising_time_us[NUM_ULTRASONICS] = {0, 0, 0};
  bool echo_level = false;

  for (int i = 0; i < NUM_ULTRASONICS; i++)
  {
    echo_level = digitalRead(ULTRASONIC_ECHO_PINS[i]);

    if ((echo_level == 1) && (!reading_echo_pin[i])) 
    {
      echo_rising_time_us[i] = micros();
      reading_echo_pin[i] = true;
    }
    else if ((echo_level == 0) && (reading_echo_pin[i]))
    {
      ultrasonic_distances_cm[i] = (double(SPEED_OF_SOUND_MPS) / 1000000 * 100) 
                                    * (micros() - echo_rising_time_us[i]) / 2;
      reading_echo_pin[i] = false;
    }
  }
}

// UART TELEMETRY FUNCTIONS ---------------------------------------------------------------------------------

// Generates and transmits telemetry data to the Raspberry Pi.
void talk_to_rpi() 
{
  String telemetry_string = "|";

  // Add ultrasonic distances to telemetry string
  for (int i = 0; i < NUM_ULTRASONICS; i++) 
  {
    telemetry_string += "US";
    telemetry_string += i + 1;
    telemetry_string += "=";

    char buf[5];
    dtostrf(ultrasonic_distances_cm[i], 5, 1, buf);
    telemetry_string += String(buf);
    telemetry_string += "cm";
    telemetry_string += "|";
  }

  // Prepend current time in seconds to serial output
  // Uh oh. 1 extra second gained every 20 mins, check on this later
  Serial1.print(double(millis()) / 1000);

  telemetry_string += "PLACEHOLDER_STATUS=1";

  Serial1.println(telemetry_string);

  last_talk_time_us = micros();

}

// MAIN SETUP AND LOOP FUNCTIONS ----------------------------------------------------------------------------

void setup() {

  if (MOTORS_ATTACHED)
  { 
    for (int i = 0; i < 4; i++) 
    { 
      pinMode(DRIVER_PINS[i], OUTPUT); 
    } 
  }

  if (ULTRASONICS_ATTACHED)
  {
    for (int i = 0; i < NUM_ULTRASONICS; i++) 
    {
      pinMode(ULTRASONIC_TRIG_PINS[i], OUTPUT); 
      digitalWrite(ULTRASONIC_TRIG_PINS[i], LOW);

      pinMode(ULTRASONIC_ECHO_PINS[i], INPUT);
      attachInterrupt(
        digitalPinToInterrupt(ULTRASONIC_ECHO_PINS[i]), 
        ultrasonic_echo_handler, CHANGE);
    }
  }

  if (UART_ATTACHED)
  {
    Serial.begin(115200);
    Serial1.begin(UGV_BAUDRATE);
    Serial.println("\nOpening serial connection...");
    while (!Serial1) {;} // Wait until serial1 is ready
    Serial.println("Serial connection opened!");
  }

}

void loop() {

  uint32_t curr_time_us = micros();   // Should probably revise this, rolls over every 70 minutes

  if (MOTORS_ATTACHED && UART_ATTACHED) 
  {
    if (curr_time_us - last_command_time_us > COMMAND_THRESHOLD_US) 
    {
      do_rpi_command();
    }
    else if (ugv_is_moving && curr_time_us - last_move_time_us > (2 * COMMAND_THRESHOLD_US))
    {
      stop();
      ugv_is_moving = false;
      last_move_time_us = curr_time_us;
    }
  }
  if (ULTRASONICS_ATTACHED)
  { 
    if (curr_time_us - last_sample_time_us > SAMPLE_THRESHOLD_US) 
    {
      sample_ultrasonics(curr_time_us);
    }
  }
  if (UART_ATTACHED)
  {
    if (curr_time_us - last_talk_time_us > TELEMETRY_THRESHOLD_US)
    {
      talk_to_rpi();
    }
  }

}

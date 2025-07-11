// Arduino to R.Pi Communication Driver
// AEGIS Senior Design, 4/26/2025

// Designed for Arduino MEGA and R.Pi 5
// Uses Serial1 TX/RX on pins 18/19
// and motor control on 4, 5, 6, and 7

#include <stdio.h>

// VARIABLE declarations and preprocessor macros ------------------------------

// Switch any of these on or off depending on their connection to the rover
#define UART_COMMS_ON   1
#define MOTORS_ON       1
#define ULTRASONICS_ON  1
#define SEND_DATA_ON    1
#define CAMERAS_ON      1
#define LIDAR_ON        1

// Motors ---------------------------------------------------------------------

// Forward and reverse pins for left and right 
#define LEFT_PWM_F  4
#define LEFT_PWM_R  5
#define RIGHT_PWM_F 6
#define RIGHT_PWM_R 7

uint8_t DRIVER_PINS[4] = {
  LEFT_PWM_F,
  LEFT_PWM_R,
  RIGHT_PWM_F,
  RIGHT_PWM_R
};
volatile uint8_t rpm;

// RPM LIMITS
#define MIN_RPM 0
#define MAX_RPM 223
#define MIN_PW 0
#define MAX_PW 255
#define MIN_SAFE_DIST -100 // 17cm offset from US sensors to front of tires (47)
#define MOVE_INCREMENT_MS 50      // Duration of move commands in milliseconds

// Movement pattern arrays:         LF,  LR,  RF,  RR
uint8_t stop_pattern[4]         = {  0,   0,   0,   0};
uint8_t forward_pattern[4]      = {  1,   0,   1,   0};
uint8_t reverse_pattern[4]      = {  0,   1,   0,   1};
float   left_arc_pattern[4]     = {0.3,   0,   1,   0};   // Left arc and right arc don't work until closed loop PID
float   right_arc_pattern[4]    = {  1,   0, 0.3,   0};
uint8_t left_spin_pattern[4]    = {  0,   1,   1,   0};
uint8_t right_spin_pattern[4]   = {  1,   0,   0,   1};

// MOVEMENT  ------------------------------------------------------------------

// move_rover: Sets rpm of each motor driver input in accordance with predefined movement patterns.
void move_rover(String dir, uint8_t rpm)
{
  if      (dir == "stop")       { for (int i = 0; i < 4; i++) { set_rpm( DRIVER_PINS[i], rpm * stop_pattern[i]);       } }
  else if (dir == "forward")    { for (int i = 0; i < 4; i++) { set_rpm( DRIVER_PINS[i], rpm * forward_pattern[i]);    } }
  else if (dir == "reverse")    { for (int i = 0; i < 4; i++) { set_rpm( DRIVER_PINS[i], rpm * reverse_pattern[i]);    } }
  else if (dir == "left arc")   { for (int i = 0; i < 4; i++) { set_rpm( DRIVER_PINS[i], rpm * left_arc_pattern[i]);   } }
  else if (dir == "right arc")  { for (int i = 0; i < 4; i++) { set_rpm( DRIVER_PINS[i], rpm * right_arc_pattern[i]);  } }
  else if (dir == "left spin")  { for (int i = 0; i < 4; i++) { set_rpm( DRIVER_PINS[i], rpm * left_spin_pattern[i]);  } }
  else if (dir == "right spin") { for (int i = 0; i < 4; i++) { set_rpm( DRIVER_PINS[i], rpm * right_spin_pattern[i]); } }
}

// stop: Stops rover via a call to the move_rover function.
void stop(void) { move_rover("stop", 0); }

// set_rpm: Maps rpm input to PWM value between 0 and 255, then writes that value to the pin input
void set_rpm(int pin, uint8_t rpm) { analogWrite(pin, map(rpm, MIN_RPM, MAX_RPM, MIN_PW, MAX_PW)); }


// MAIN SETUP AND LOOP --------------------------------------------------------

void setup() {

  if (MOTORS_ON)
  {
    // Set PWM forward and reverse connections as outputs
    for (int i = 0; i < 4; i++) { pinMode(DRIVER_PINS[i], OUTPUT); }
  }
  if (ULTRASONICS_ON)
  {
    // Set pin modes for Ultrasonic sensors
    for (int i = 0; i < 3; i++) { pinMode(US_trig_pins[i], OUTPUT); }
    for (int i = 0; i < 3; i++) { pinMode(US_echo_pins[i], INPUT); }

    // Ultrasonic Sensors, sets triggers low & interrupts
    attachInterrupt(digitalPinToInterrupt(US_echo_pins[0]), ultrasonic_echo_handler, CHANGE);
    attachInterrupt(digitalPinToInterrupt(US_echo_pins[1]), ultrasonic_echo_handler, CHANGE);
    attachInterrupt(digitalPinToInterrupt(US_echo_pins[2]), ultrasonic_echo_handler, CHANGE);
  }
  if (UART_COMMS_ON)
  {
    Serial.begin(9600);
    Serial1.begin(115200);
    Serial.println("Opening serial connection...");
    while (!Serial1) {;} // Wait until serial1 is ready
    Serial.println("Serial connections opened!");
  }

}


// NEW PHONE WHO DIS ----------------------------------------------------------



// MOTOR FLAGS
bool just_moved = false;    // If the previous command was to move      // MAYBE NEEDS VOLATILE???

// ULTRASONIC FLAGS
bool triggers_active = false;
bool reading_echo_pin[] = {0, 0, 0}
long echo_rising_time_us[] = {0, 0, 0}

// FUNCTION CALL INTERVAL PERIODS
uint16_t command_threshold_ms = 50;
uint16_t sample_threshold_ms = 250;
uint16_t enlightenment_threshold_ms = 500;

void loop() {

  uint32_t curr_time = millis();

  do_rpi_command(curr_time, just_moved);
  sample_ultrasonics(curr_time, triggers_active);
  enlighten_rpi(curr_time);

}

void do_rpi_command(float curr_time, bool just_moved) 
{
  static uint32_t last_call_time = 0;

  // Exit function unless enough time has elapsed since previous function call
  if (curr_time - last_call_time < command_threshold_ms) { return; }
  else if (just_moved) { stop(); }

  just_moved = false;

  uint8_t command[] = {0, 0, 0};

  if (Serial1.available() > 2)  // If a 3-byte command is waiting
  {
    // Read each byte into the command packet
    for (int idx = 0; idx < 3; idx++) { command[idx] = Serial1.read(); }
  }

  int opcode = (command[0] & 0xC0) / 64;  // gives opcode in range [0,3]

  // Executes commands
  switch (opcode)
  {
    case 3: // MOVE
    {
      Serial.print("Recieved MOVE command: ");
      for (int i = 0; i < 3; i++) {Serial.print(command[i]); Serial.print(" ");} Serial.println();

      String   dir = (command[0] & 0x01) ? "reverse" : "forward";
      uint8_t  spd = map(command[1], MIN_PW, MAX_PW, MIN_RPM, MAX_RPM);
      uint16_t dur = command[2] * MOVE_INCREMENT_MS;    // CURRENTLY UNUSED

      // If all ultrasonics report safe forward movement
      // OR you're reversing OR no ultrasonics connected
      if((US_distance[0] > MIN_SAFE_DIST &&
          US_distance[1] > MIN_SAFE_DIST &&
          US_distance[2] > MIN_SAFE_DIST)   ||
          (dir == "reverse")                ||
          !(ULTRASONICS_ON))
      {
        move_rover(dir, spd);
        just_moved = true;
      }

      break;
    }

    case 2: // TURN
    {
      Serial.print("Recieved TURN command: ");
      for (int i = 0; i < 3; i++) {Serial.print(command[i]); Serial.print(" ");} Serial.println();

      String dir = (command[0] & 0x01) ? "right spin" : "left spin";
      uint8_t  spd = map(command[1], MIN_PW, MAX_PW, MIN_RPM, MAX_RPM);
      uint16_t dur = command[2] * MOVE_INCREMENT_MS;    // CURRENTLY UNUSED

      if((US_distance[0] >= MIN_SAFE_DIST && 
          US_distance[1] >= MIN_SAFE_DIST &&
          US_distance[2] >= MIN_SAFE_DIST)    ||
          !(ULTRASONICS_ON))
      {
        move_rover(dir, spd);
        just_moved = true;
      }

      break;
    }

  }

}

void sample_ultrasonics(float curr_time, bool triggers_active) 
{
  static uint32_t last_call_time = 0;

  // Exit function unless enough time has elapsed since previous function call
  if (curr_time - last_call_time < sample_threshold_ms) { return; }

  // Set trigger pins high every elapsed sample period
  if (!triggers_active) {
    for(int i = 0; i < 3; i++) { digitalWrite(US_trig_pins[i], HIGH); }
    triggers_active = true;
  }

  // ECHO pins are monitored by interrupt, see ultrasonic_echo_handler function for more

  // Reset trigger pins every elapsed sample period + pulse_duration
  if (triggers_active && (curr_time - last_call_time > sample_threshold_ms + pulse_duration_ms))
  {
    for(int i = 0; i < 3; i++) { digitalWrite(US_trig_pins[i], LOW); }
    triggers_active = false;
  }
}

void ultrasonic_echo_handler() 
{
  for (int i = 0; i<3; i++)
  {
    bool echo_level = digitalRead(US_echo_pins[i]);
    if ((echo_level == 1) && (!reading_echo_pin[i]) 
    {
      echo_rising_time_us[i] = micros();
      reading_echo_pin[i] = true;
    }
    else if ((echo_level == 0) && (reading_echo_pin[i]))
    {
      ultrasonic_distances[i] = 0.0343 * (micros() - echo_rising_time_us[i]) / 2;
      //echo_rising_time_us[i] = 0;     // SHOULD BE UNNECCESSARY, SIMPLY MAKES VALUE INDETERMINATE BETWEEN READS
      reading_echo_pin[i] = false;
    }
  }
}

void enlighten_rpi(float curr_time) {

  static uint32_t last_call_time = 0;

  // exit function unless enough time has elapsed since previous function call
  if (curr_time - last_call_time < enlightenment_threshold_ms) { return; }
  
}
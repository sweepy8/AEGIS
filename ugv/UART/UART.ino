// Arduino to R.Pi Communication Driver (Version 2)
// AEGIS Senior Design, 7/21/2025

// Designed for Arduino MEGA and R.Pi 5
// Uses Serial1 TX/RX on pins 18/19
// and motor control on 4, 5, 6, and 7

// ATmega2560 Datasheet:
//   https://ww1.microchip.com/downloads/aemDocuments/documents/OTH/ProductDocuments/DataSheets/ATmega640-1280-1281-2560-2561-Datasheet-DS40002211A.pdf

// Compatible ports and pins for the Arduino Mega 2560 are as follows:
//   https://docs.arduino.cc/retired/hacking/hardware/PinMapping2560/



//  TODO: MAKE STUFF CONST

#include <stdio.h>

// GENERAL DEFINITIONS --------------------------------------------------------------------------------------

#define SPEED_OF_SOUND_MPS 343.0    //331 + 0.69 * Temp (Celsius)

#define UART_ATTACHED        1
#define MOTORS_ATTACHED      1
#define ULTRASONICS_ATTACHED 1

#define UGV_BAUDRATE 115200

#define COMMAND_THRESHOLD_US   50000
#define SAMPLE_THRESHOLD_US    500000
#define TELEMETRY_THRESHOLD_US 1000000

uint32_t last_command_time_us = 0;
uint32_t last_move_time_us = 0;
uint32_t last_sample_time_us = 0;
uint32_t last_talk_time_us = 0;
uint32_t last_flush_time_us = 0;
bool ugv_is_moving = false;

// MOTOR FLAGS & DATA ---------------------------------------------------------------------------------------
 
#define MIN_RPM 0
#define MAX_RPM 223
#define MIN_PW 0
#define MAX_PW 255
#define MOVE_INCREMENT_US 50000

//                                  LF,  LR,  RF,  RR
uint8_t stop_pattern[4]         = {  0,   0,   0,   0};
uint8_t forward_pattern[4]      = {  1,   0,   1,   0};
uint8_t reverse_pattern[4]      = {  0,   1,   0,   1};
float   left_arc_pattern[4]     = {0.3,   0,   1,   0};   // Left, right arc won't work until closed loop PID
float   right_arc_pattern[4]    = {  1,   0, 0.3,   0};
uint8_t left_spin_pattern[4]    = {  0,   1,   1,   0};
uint8_t right_spin_pattern[4]   = {  1,   0,   0,   1};

#define LEFT_PWM_FWD  4
#define LEFT_PWM_RVS  5
#define RIGHT_PWM_FWD 6
#define RIGHT_PWM_RVS 7
uint8_t DRIVER_PINS[4] = {LEFT_PWM_FWD, LEFT_PWM_RVS, RIGHT_PWM_FWD, RIGHT_PWM_RVS};

String MOTOR_NAMES[6] = {"LF", "LM", "LR", "RF", "RM", "RR"}; 

#define LEFT_FRONT_ENC_A  12    // B6 (PCINT6)
#define LEFT_FRONT_ENC_B  44
#define LEFT_MID_ENC_A    13    // B7 (PCINT7)
#define LEFT_MID_ENC_B    46  
#define LEFT_REAR_ENC_A   11    // B5 (PCINT5)
#define LEFT_REAR_ENC_B   48

#define RIGHT_FRONT_ENC_A 14    // J1 (PCINT10)
#define RIGHT_FRONT_ENC_B 39
#define RIGHT_MID_ENC_A   15    // J0 (PCINT9)
#define RIGHT_MID_ENC_B   41
#define RIGHT_REAR_ENC_A  10    // B4 (PCINT4)
#define RIGHT_REAR_ENC_B  43

uint8_t ENCODER_A_PINS[6] = {LEFT_FRONT_ENC_A,  LEFT_MID_ENC_A,  LEFT_REAR_ENC_A,
                             RIGHT_FRONT_ENC_A, RIGHT_MID_ENC_A, RIGHT_REAR_ENC_A};
uint8_t ENCODER_B_PINS[6] = {LEFT_FRONT_ENC_B,  LEFT_MID_ENC_B,  LEFT_REAR_ENC_B,
                             RIGHT_FRONT_ENC_B, RIGHT_MID_ENC_B, RIGHT_REAR_ENC_B};

volatile uint8_t target_rpm = 0;
volatile uint8_t enc_pulse_counts[6] = {0, 0, 0, 0, 0, 0};
volatile bool enc_directions[6]      = {0, 0, 0, 0, 0, 0};  // 0 for CCW, 1 for CW
float actual_rpms[6]                 = {0, 0, 0, 0, 0, 0};  

// ULTRASONIC FLAGS & DATA ----------------------------------------------------------------------------------

#define NUM_ULTRASONICS 3
#define SAFE_DISTANCE_CM -100
#define PULSE_DURATION_US 10

uint8_t ULTRASONIC_TRIG_PINS[NUM_ULTRASONICS] = {47, 49, 45};
uint8_t ULTRASONIC_ECHO_PINS[NUM_ULTRASONICS] = {52, 53, 51};

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

  // ECHO pins are handled by interrupt, see ISR function for more

  // Reset trigger pins every elapsed sample period + pulse duration
  if (triggers_high && ((curr_time_us - last_sample_time_us) >= (SAMPLE_THRESHOLD_US + PULSE_DURATION_US)))
  {
    for(int i = 0; i < NUM_ULTRASONICS; i++) { digitalWrite(ULTRASONIC_TRIG_PINS[i], LOW); }
    triggers_high = false;

    last_sample_time_us = micros();
  }
}

// INTERRUPT HANDLERS ------------------------------------------------------------------------------

#define ENCODER_PULSE_WINDOW_MS 80

// PCINT0 Interrupt Service Handler (PB0-7) (PCINT0-7)
// Handles Ultrasonic Echo Pin Interrupts (PB0-2) and Motor Encoder Interrupts (PB4-7)
ISR (PCINT0_vect)
{
  static const uint8_t PCINT0_ENC_A_PINS[4] = {LEFT_FRONT_ENC_A, LEFT_MID_ENC_A, LEFT_REAR_ENC_A, RIGHT_REAR_ENC_A};
  static const uint8_t PCINT0_ENC_B_PINS[4] = {LEFT_FRONT_ENC_B, LEFT_MID_ENC_B, LEFT_REAR_ENC_B, RIGHT_REAR_ENC_B};
  static const uint8_t ENC_POSITIONS[4] = {0, 1, 2, 5};
  static bool enc_a_states[4] = {LOW, LOW, LOW, LOW};
  static bool enc_b_states[4] = {LOW, LOW, LOW, LOW};
  static bool enc_a_level = LOW;

  static bool echo_states[NUM_ULTRASONICS] = {LOW, LOW, LOW};
  static uint32_t echo_start_times_us[NUM_ULTRASONICS] = {0, 0, 0};
  bool echo_level = LOW;

  // Check to see if interrupt came from a motor encoder
  for (int i = 0; i < 4; i++)
  {
    enc_a_level = digitalRead(PCINT0_ENC_A_PINS[i]);

    if ((enc_a_level == HIGH) && (enc_a_states[i] == LOW))
    {
      enc_pulse_counts[ENC_POSITIONS[i]] += 1;
      enc_a_states[i] = HIGH;
      enc_b_states[i] = digitalRead(PCINT0_ENC_B_PINS[i]);

      if (enc_b_states[i] == LOW)
      {
        // Clockwise
        enc_directions[ENC_POSITIONS[i]] = HIGH;
      }
      else
      {
        // Counterclockwise
        enc_directions[ENC_POSITIONS[i]] = LOW;
      }
    }

    if ((enc_a_level == LOW) && (enc_a_states[i] == HIGH))
    {
      enc_a_states[i] = LOW;
      enc_b_states[i] = digitalRead(PCINT0_ENC_B_PINS[i]);
    }
  }

  // Check to see if interrupt came from an ultrasonic sensor
  for (int i = 0; i < NUM_ULTRASONICS; i++)
  {
    echo_level = digitalRead(ULTRASONIC_ECHO_PINS[i]);

    if ((echo_level == HIGH) && (echo_states[i] == LOW))
    {
      echo_start_times_us[i] = micros();
      echo_states[i] = HIGH;
    }

    else if ((echo_level == LOW) && (echo_states[i] == HIGH))
    {
      ultrasonic_distances_cm[i] = (SPEED_OF_SOUND_MPS * 100) 
        * (float(micros() - echo_start_times_us[i]) / 1000000)
        / 2;

      echo_states[i] = LOW;
    }

  }
}

// PCINT1 Interrupt Service Handler (PE0, PJ0-6) (PCINT8-15)
// Handles Motor Encoder Interrupts (PJ0-1)
ISR (PCINT1_vect)
{
  static const uint8_t PCINT1_ENC_A_PINS[2] = {RIGHT_FRONT_ENC_A, RIGHT_MID_ENC_A};
  static const uint8_t PCINT1_ENC_B_PINS[2] = {RIGHT_FRONT_ENC_B, RIGHT_MID_ENC_B};
  static const uint8_t ENC_POSITIONS[2] = {3, 4};
  static bool enc_a_states[2] = {LOW, LOW};
  static bool enc_b_states[2] = {LOW, LOW};
  static bool enc_a_level = LOW;

  // Check to see if interrupt came from a motor encoder
  for (int i = 0; i < 2; i++)
  {
    enc_a_level = digitalRead(PCINT1_ENC_A_PINS[i]);

    if ((enc_a_level == HIGH) && (enc_a_states[i] == LOW))
    {
      enc_pulse_counts[ENC_POSITIONS[i]] += 1;
      enc_a_states[i] = HIGH;
      enc_b_states[i] = digitalRead(PCINT1_ENC_B_PINS[i]);

      if (enc_b_states[i] == LOW)
      {
        // Clockwise
        enc_directions[ENC_POSITIONS[i]] = HIGH;
      }
      else
      {
        // Counterclockwise
        enc_directions[ENC_POSITIONS[i]] = LOW;
      }
    }

    if ((enc_a_level == LOW) && (enc_a_states[i] == HIGH))
    {
      enc_a_states[i] = LOW;
      enc_b_states[i] = digitalRead(PCINT1_ENC_B_PINS[i]);
    }
  }
}

// UART TELEMETRY FUNCTIONS ---------------------------------------------------------------------------------

// Generates and transmits telemetry data to the Raspberry Pi.
void talk_to_rpi() 
{
  String telemetry_string = "|";

  // Add RPM values to telemetry string
  for (int i = 0; i < 6; i++)
  {
    telemetry_string += MOTOR_NAMES[i];
    telemetry_string += "=";

    char rpm_str[3];
    snprintf(rpm_str, 3, "%d", actual_rpms[i]);
    
    telemetry_string += rpm_str;
    telemetry_string += "RPM";
    if (enc_directions[i] == 1) 
    {
      telemetry_string += "CW";
    }
    else 
    {
      telemetry_string += "CCW";
    }

    telemetry_string += "|";
  }

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
  Serial1.println(telemetry_string);

  last_talk_time_us = micros();
}

// MAIN SETUP AND LOOP FUNCTIONS ----------------------------------------------------------------------------

void setup() {

  // CONFIGURE MOTOR DRIVER PWM CONTROL PINS 
  if (MOTORS_ATTACHED)
  { 
    for (int i = 0; i < 4; i++) 
    {
      pinMode(DRIVER_PINS[i], OUTPUT); 
    } 
  }

  if (MOTORS_ATTACHED && UART_ATTACHED)
  {
    for (int i = 0; i < 6; i++)
    {
      pinMode(ENCODER_A_PINS[i], INPUT);
      pinMode(ENCODER_B_PINS[i], INPUT);
    }

    // Enable pin change interrupts on ports B and J via PC Interrupt Control Register
    // Bit 0 is PCINT7:0, Bit 1 is PCINT15:8, Bit 2 is PCINT 23:16 (p. 112 of DS)
    PCICR |= 0x03;

    // Specifically enable PC interrupts on PB4-7 (PCINT4-7) and PJ0-1 (PCINT9-10) via PC Mask 0 and 1 Registers
    PCMSK0 |= 0xF0;
    PCMSK1 |= 0x06;

  }

  // CONFIGURE ULTRASONIC TRIGGER AND ECHO PINS
  if (ULTRASONICS_ATTACHED)
  {
    for (int i = 0; i < NUM_ULTRASONICS; i++) 
    {
      pinMode(ULTRASONIC_TRIG_PINS[i], OUTPUT); 
      digitalWrite(ULTRASONIC_TRIG_PINS[i], LOW);

      pinMode(ULTRASONIC_ECHO_PINS[i], INPUT);
    }

    // Enable pin change interrupts on port B via PC Interrupt Control Register
    // Bit 0 is PCINT7:0, Bit 1 is PCINT15:8, Bit 2 is PCINT 23:16 (p. 112 of DS)
    PCICR |= 0x01;

    // Specifically enable PC interrupts on PB0, PB1, PB2 via PC Mask 0 Register
    PCMSK0 |= 0x07;
  }

  // CONFIGURE ARDUINO IDE AND RASPBERRY PI SERIAL PORTS
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

  // OPERATE FEEDBACK LOOP ON ENCODERS
  if (MOTORS_ATTACHED && UART_ATTACHED)
  {
    if (curr_time_us - last_flush_time_us > 80000)
    {
      for (int i = 0; i < 6; i++) 
      {
        // pulses in window / pulses per revolution / length of window in ms * ms per minute
        actual_rpms[i] = double(enc_pulse_counts[i]) / 753.2 / ENCODER_PULSE_WINDOW_MS * 60000;
        Serial.print(actual_rpms[i]);
        Serial.print(" ");
        enc_pulse_counts[i] = 0;
      }
      Serial.println();
      last_flush_time_us = micros();
    }
  }

  // PERFORM RASPBERRY PI COMMAND
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

  // SAMPLE ULTRASONICS
  if (ULTRASONICS_ATTACHED)
  { 
    if (curr_time_us - last_sample_time_us > SAMPLE_THRESHOLD_US) 
    {
      sample_ultrasonics(curr_time_us);
    }
  }

  // TRANSMIT TELEMETRY TO RASPBERRY PI
  if (UART_ATTACHED)
  {
    if (curr_time_us - last_talk_time_us > TELEMETRY_THRESHOLD_US)
    {
      talk_to_rpi();
    }
  }

}
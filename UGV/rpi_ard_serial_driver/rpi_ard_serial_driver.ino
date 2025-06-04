// Arduino to R.Pi Communication Driver
// AEGIS Senior Design, 4/26/2025

// Designed for Arduino MEGA and R.Pi 5
// Uses Serial1 TX/RX on pins 18/19
// and motor control on 4, 5, 6, and 7


// VARIABLE declarations and preprocessor macros ------------------------------

// Switch any of these on or off depending on their connection to the rover
#define UART_COMMS_ON   1
#define MOTORS_ON       1
#define ULTRASONICS_ON  0
#define CAMERAS_ON      0
#define LIDAR_ON        0

// Forward and reverse pins for left and right 
#define LEFT_PWM_F  4
#define LEFT_PWM_R  5
#define RIGHT_PWM_F 6
#define RIGHT_PWM_R 7

uint8_t driver_pins[4] = {
  LEFT_PWM_F,
  LEFT_PWM_R,
  RIGHT_PWM_F,
  RIGHT_PWM_R
};

volatile uint8_t rpm;

// RPM LIMITS
#define MIN_RPM 0
#define MAX_RPM 223

// Simple string macros to improve readability, not necessary
#define STOP        String("stop")
#define FORWARD     String("forward")
#define REVERSE     String("reverse")
#define LEFT_ARC    String("left arc")
#define RIGHT_ARC   String("right arc")
#define LEFT_SPIN   String("left spin")
#define RIGHT_SPIN  String("right spin")
#define LEFT_PIVOT  String("left pivot")
#define RIGHT_PIVOT String("right pivot")


// Movement pattern arrays:         LF,  LR,  RF,  RR
uint8_t stop_pattern[4]         = {  0,   0,   0,   0};
uint8_t forward_pattern[4]      = {  1,   0,   1,   0};
uint8_t reverse_pattern[4]      = {  0,   1,   0,   1};
float left_arc_pattern[4]       = {0.3,   0,   1,   0};
float right_arc_pattern[4]      = {  1,   0, 0.3,   0};
uint8_t left_spin_pattern[4]    = {  0,   1,   1,   0};
uint8_t right_spin_pattern[4]   = {  1,   0,   0,   1};


// MOVEMENT FUNCTIONS -------------------------------------------------------------------------------------------------

// stop: Stops rover via a call to the move_rover function.
void stop(void) 
{
  move_rover(STOP, 0); 
}

// move: Sets rpm of each motor driver input in accordance with predefined movement patterns.
void move_rover(String dir, uint8_t rpm)
{
  if      (dir == "stop")       { for (int i = 0; i < 4; i++) { set_rpm(driver_pins[i], rpm*stop_pattern[i]);       } }
  else if (dir == "forward")    { for (int i = 0; i < 4; i++) { set_rpm(driver_pins[i], rpm*forward_pattern[i]);    } }
  else if (dir == "reverse")    { for (int i = 0; i < 4; i++) { set_rpm(driver_pins[i], rpm*reverse_pattern[i]);    } }
  else if (dir == "left arc")   { for (int i = 0; i < 4; i++) { set_rpm(driver_pins[i], rpm*left_arc_pattern[i]);   } }
  else if (dir == "right arc")  { for (int i = 0; i < 4; i++) { set_rpm(driver_pins[i], rpm*right_arc_pattern[i]);  } }
  else if (dir == "left spin")  { for (int i = 0; i < 4; i++) { set_rpm(driver_pins[i], rpm*left_spin_pattern[i]);  } }
  else if (dir == "right spin") { for (int i = 0; i < 4; i++) { set_rpm(driver_pins[i], rpm*right_spin_pattern[i]); } }
}

// set_rpm_pattern: Writes mapped rpm value to all driver pins from symmetric rpm_pattern array input
void set_rpm_pattern(uint8_t rpm_pattern[])
{
  for (int i = 0; i < 4; i++) { analogWrite( driver_pins[i], map(rpm_pattern[i], MIN_RPM, MAX_RPM, 0, 255) ); }
}

// set_rpm: Maps rpm input to PWM value between 0 and 255, then writes that value to the pin input
void set_rpm(int pin, uint8_t rpm) 
{ 
  analogWrite(pin, map(rpm, 0, 223, 0, 255)); 
}


// UART COMMUNICATION FUNCTIONS ---------------------------------------------------------------------------------------------------

void perform_rpi_command(int* command)
{
  int op_byte = *command;
  int op = (op_byte & 0xC0) / 64; // gives op in range [0, 3]

  switch (op)
  {
    case 0: // 00b --> SEND INFO
    {
      Serial.print("SEND INFO COMMAND RECIEVED... ");
      int arg = op_byte & 0x3F;
      Serial.print("Arg: ");
      Serial.println(arg);
      break;
    }

    case 1: // 01b --> CURRENTLY UNDEFINED
    {
      break;
    }

    case 2: // 10b --> TURN
    {
      Serial.println("TURN COMMAND RECIEVED... ");
      String dir = (op_byte & 0x01) ? LEFT_SPIN : RIGHT_SPIN;
      int spd = *(command+1);
      spd = spd * 223 / 255;
      int dur = *(command+2) * 100;

      move_rover(dir, uint8_t(spd));
      delay(dur);
      stop();

      break;
    }

    case 3: // 11b --> MOVE
    {
      Serial.println("MOVE COMMAND RECIEVED... ");
      String dir = (op_byte & 0x01) ? REVERSE : FORWARD;
      int spd = *(command+1);
      spd = spd * 223 / 255;
      int dur = *(command+2) * 100;

      move_rover(dir, spd);
      delay(dur);
      stop();

      break;
    }

    default:
    {
      Serial.println("ERROR! INVALID OPCODE");
    }
  }
}

// Performs command associated with controller input over serial1 port
void serial1_Handler()
{
  int command[] = {-1, -1, -1};
  int idx;

  if (Serial1 && (Serial1.available() > 2))    // If serial 1 is open and a 3-byte command is waiting
  {
    for (idx = 0; idx < 3; idx++)
    {
      command[idx] = Serial1.read();            // Record each byte into the command array
      if (Serial1.available() == 0) {break;}    // CURRENTLY WON'T EVER TRIGGER BECAUSE OF CONDITION avail > 2
    }

    perform_rpi_command(command);

    for (int i = 0; i < 3; i++) { command[i] = -1; }  // Reset command buffer
  }
}


// MAIN SETUP AND LOOP ------------------------------------------------------------------------------------------------

void setup() {

  // Set PWM forward and reverse connections as outputs
  if (MOTORS_ON) {
    for (int i = 0; i < 4; i++) { pinMode(driver_pins[i], OUTPUT); }
  }

  if (UART_COMMS_ON)
  {
    Serial.begin(9600);
    Serial1.begin(9600);
    Serial.println("Opening serial connection...");
    while (!Serial1) {;} // Wait until serial1 is ready
    Serial.println("Serial connections opened!");
  }

}

void loop() {

  if (MOTORS_ON)
  {
    uint8_t run_cycles = 1; // Set to 1 to run while block once

    while (run_cycles)
    {
      stop(); delay(1000);  // Start with 1 second pause

      // Test for no-load/load currents and voltages
      // 30% through 100% in 10% intervals, 10+1 second runtime each
      int i, j;
      for (i = 3; i <= 10; i++)
      {
        move_rover(FORWARD, 22 * (i)); delay(1000 * 10);
        stop(); delay(1000);
      }
      run_cycles--;
    }
  }

  if (UART_COMMS_ON)
  {
    serial1_Handler();
  }

}

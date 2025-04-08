/*
UGV piloting test code v0.3 
AEGIS Senior Design, CSUN 2025

  This program runs on a single arduino nano. It provides the framework to 
  move and stop the rover, and includes test movement patterns for forward 
  and reverse, as well as spin and pivot turns in both directions.

  If you modify this program, ensure that you NEVER:
    - drive a motor with greater than 223 rpm (untested, may be fine)
    - send a non-zero rpm value to both forward and reverse simultaneously
    - create an infinite loop for movement in any direction. Tests should be 
      limited to thirty seconds at full power in any direction for now.

TODO:

  Introduce mapping to percentage of usable rpm?
    - rpm = map(rpm_pct, 0, 1, 60, 223);
  
  Pivot turn currently uses opposite side forward, but could be implemented
  with turn direction side reversing. Could afford better turn flexibility.

PROBLEMS:

  Currently, turning AT ALL causes too much current draw and can melt the
  motor driver circuits. Avoid all turn tests until wiring has been redone.
  - RESOLVED BY REDUCING MOTOR VOLTAGE, SHOULD BE SAFE TO TURN

  Small step increments can cause an additional cycle to run than would be
  expected using relevant calculations due to a truncation error when
  casting the rpm to an integer, i.e. 223 * 0.1 == 22, NOT 22.3
    - This should not create any problems, as the RPM value should still not
      exceed 223. At present, this does not need to be corrected.

*/


// VARIABLE declarations and preprocessor macros ------------------------------

// Forward and reverse pins for left and right 
#define LEFT_PWM_F  5
#define LEFT_PWM_R  6
#define RIGHT_PWM_F 10
#define RIGHT_PWM_R 11

#define STOP String("stop")
#define FORWARD String("forward")
#define REVERSE String("reverse")
#define LEFT_ARC String("left arc")
#define RIGHT_ARC String("right arc")
#define LEFT_SPIN String("left spin")
#define RIGHT_SPIN String("right spin")
#define LEFT_PIVOT String("left pivot")
#define RIGHT_PIVOT String("right pivot")

// TEST TIMING PARAMETERS
#define RUN_TIME   3000    // milliseconds
#define ARC_RUN_TIME 5000  // milliseconds
#define PAUSE_TIME 3000    // milliseconds
#define INCLUDE_ARC_TURNS 1
#define INCLUDE_SHARP_TURNS 1
uint8_t run_cycles = 1;

// TEST RPM PARAMETERS
#define MIN_RPM 0
#define MAX_RPM 223
#define ARC_RPM 223
#define INC_RPM_STEP 0.25   // percent to increment power 
#define INC_RPM_STEPS 4     // STEP * STEPS MUST NOT EXCEED 1

uint8_t driver_pins[4] = {LEFT_PWM_F, LEFT_PWM_R, RIGHT_PWM_F, RIGHT_PWM_R};
volatile uint8_t rpm;

// Movement pattern arrays:         LF,  LR,  RF,  RR
uint8_t stop_pattern[4]         = {  0,   0,   0,   0};
uint8_t forward_pattern[4]      = {  1,   0,   1,   0};
uint8_t reverse_pattern[4]      = {  0,   1,   0,   1};
float left_arc_pattern[4]       = {0.3,   0,   1,   0};
float right_arc_pattern[4]      = {  1,   0, 0.3,   0};
uint8_t left_spin_pattern[4]    = {  0,   1,   1,   0};
uint8_t right_spin_pattern[4]   = {  1,   0,   0,   1};
uint8_t left_pivot_pattern[4]   = {  0,   0,   0,   1};
uint8_t right_pivot_pattern[4]  = {  1,   0,   0,   0};


// MAIN setup and loop functions --------------------------------------------------

void setup()
{
  // Set PWM forward and reverse connections as outputs
  for (int i = 0; i < 4; i++) { pinMode(driver_pins[i], OUTPUT); }
}

void loop()
{
  // analogWrite(5, 128);
  // analogWrite(6, 0);
  // analogWrite(10, 128);
  // analogWrite(11, 0);
  // delay(10000);
  // move_rover(FORWARD, MAX_RPM);
  // delay(RUN_TIME);

  while (run_cycles > 0) 
  {
    // Full power spin turn left check
    analogWrite(5, 0);
    analogWrite(6, 255);
    analogWrite(10, 255);
    analogWrite(11, 0);
    delay(5000);

    stop();
    delay(100);

    // Full power pin turn right check
    analogWrite(5, 255);
    analogWrite(6, 0);
    analogWrite(10, 0);
    analogWrite(11, 255);
    delay(3000);

    stop();
    delay(10000);

    // Forward and back 5 times
    for (int i = 0; i < 5; i++)
    {
      move_rover(FORWARD, MAX_RPM);
      delay(1000);

      stop();
      delay(100);

      move_rover(REVERSE, MAX_RPM);
      delay(1000);
    }

    if (INCLUDE_SHARP_TURNS) 
    {
      move_rover(LEFT_PIVOT, MAX_RPM);
      delay(PAUSE_TIME);

      move_rover(RIGHT_PIVOT, MAX_RPM);
      delay(PAUSE_TIME);

      move_rover(LEFT_SPIN, MAX_RPM);
      delay(PAUSE_TIME);

      move_rover(RIGHT_SPIN, MAX_RPM);
      delay(PAUSE_TIME);
    }

    if (INCLUDE_ARC_TURNS)
    {
      ring_test(LEFT_ARC, RUN_TIME);
      delay(PAUSE_TIME);

      ring_test(RIGHT_ARC, RUN_TIME);
      delay(PAUSE_TIME);

      figure_8_test(5);
      delay(PAUSE_TIME);
    }

    run_cycles--;
  }
}

// Function Declarations -------------------------------------------------

// incremental_test: Moves up through the power band incrementally
void incremental_test(String dir) 
{
  for (int i = 1; i <= INC_RPM_STEPS; i++) {
    rpm = i * INC_RPM_STEP * MAX_RPM;
    move_rover(dir, rpm);
    delay(RUN_TIME);
  }
  rpm = 0;    // Should be redundant fail-safe, can probably remove
  stop();
}

// ring_test: Performs an arcing turn for as long as is specified by the run_time input.
//            The direction of the turn is set by the dir input.
void ring_test(String dir, int run_time)
{
  move_rover(dir, ARC_RPM);
  delay(run_time);
  stop();
}

// figure_8_test: Performs left and right arcing turns to trace a figure 8 pattern.
//                Integer cycles input controls the number of figure 8s that are performed.
void figure_8_test(uint8_t cycles)
{
  for (int i = 0; i < cycles; i++) 
  {
  move_rover(RIGHT_ARC, ARC_RPM);
  delay(ARC_RUN_TIME);

  move_rover(LEFT_ARC, ARC_RPM);
  delay(ARC_RUN_TIME);
  }

  stop();
}

// stop: Stops rover via a call to the move_rover function.
void stop(void) { move_rover(STOP, 0); }

// move: Sets rpm of each motor driver input in accordance with predefined movement patterns.
void move_rover(String dir, uint8_t rpm)
{
  if      (dir == "stop")         { for (int i = 0; i < 4; i++) { set_rpm(driver_pins[i], rpm * stop_pattern[i]); } }
  else if (dir == "forward")      { for (int i = 0; i < 4; i++) { set_rpm(driver_pins[i], rpm * forward_pattern[i]); } }
  else if (dir == "reverse")      { for (int i = 0; i < 4; i++) { set_rpm(driver_pins[i], rpm * reverse_pattern[i]); } }
  else if (dir == "left arc")     { for (int i = 0; i < 4; i++) { set_rpm(driver_pins[i], rpm * left_arc_pattern[i]); } }
  else if (dir == "right arc")    { for (int i = 0; i < 4; i++) { set_rpm(driver_pins[i], rpm * right_arc_pattern[i]); } }
  else if (dir == "left spin")    { for (int i = 0; i < 4; i++) { set_rpm(driver_pins[i], rpm * left_spin_pattern[i]); } }
  else if (dir == "right spin")   { for (int i = 0; i < 4; i++) { set_rpm(driver_pins[i], rpm * right_spin_pattern[i]); } }
  else if (dir == "left pivot")   { for (int i = 0; i < 4; i++) { set_rpm(driver_pins[i], rpm * left_pivot_pattern[i]); } }
  else if (dir == "right pivot")  { for (int i = 0; i < 4; i++) { set_rpm(driver_pins[i], rpm * right_pivot_pattern[i]); } }
}

// set_rpm_pattern: Writes mapped rpm value to all driver pins from symmetric rpm_pattern array input
void set_rpm_pattern(uint8_t rpm_pattern[])
{
  for (int i = 0; i < 4; i++) { analogWrite( driver_pins[i], map(rpm_pattern[i], MIN_RPM, MAX_RPM, 0, 255) ); }
}

// set_rpm: Maps rpm input to PWM value between 0 and 255, then writes that value to the pin input
void set_rpm(int pin, uint8_t rpm) { analogWrite(pin, map(rpm, 0, 223, 0, 255)); }

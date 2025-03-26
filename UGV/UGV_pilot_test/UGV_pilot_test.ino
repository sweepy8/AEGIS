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
      limited to ten seconds at full power in any direction for now.

TODO:

  Introduce mapping to percentage of usable rpm?
    - rpm = map(rpm_pct, 0, 1, 60, 223);
  
  Pivot turn currently uses opposite side forward, but could be implemented
  with turn direction side reversing. Could afford better turn flexibility.

PROBLEMS:

  Will rpm update alongside the pattern arrays inside the incremental_test?
  - Requires testing. Should be fine.

  Currently, turning AT ALL causes too much current draw and can melt the
  motor driver circuits. Avoid all turn tests until wiring has been redone.

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
#define RIGHT_PWM_F 13
#define RIGHT_PWM_R 14

uint8_t driver_pins[4] = {LEFT_PWM_F, LEFT_PWM_R, RIGHT_PWM_F, RIGHT_PWM_R};

uint8_t rpm = 0;

// Movement pattern arrays:         LF,  LR,  RF,  RR
uint8_t stop_pattern[4]         = {  0,   0,   0,   0};
uint8_t forward_pattern[4]      = {rpm,   0, rpm,   0};
uint8_t reverse_pattern[4]      = {  0, rpm,   0, rpm};
uint8_t left_spin_pattern[4]    = {  0, rpm, rpm,   0};
uint8_t right_spin_pattern[4]   = {rpm,   0,   0, rpm};
uint8_t left_pivot_pattern[4]   = {  0,   0,   0, rpm};
uint8_t right_pivot_pattern[4]  = {rpm,   0,   0,   0};

#define STOP String("stop")
#define FORWARD String("forward")
#define REVERSE String("reverse")
#define LEFT_SPIN String("left spin")
#define RIGHT_SPIN String("right spin")
#define LEFT_PIVOT String("left pivot")
#define RIGHT_PIVOT String("right pivot")

// TEST PARAMETERS
#define RUN_TIME   5000    // milliseconds
#define PAUSE_TIME 5000    // milliseconds
#define INCLUDE_TURNS 0
uint8_t run_cycles = 1;

#define MAX_RPM 223
#define RPM_STEP 0.25    // percent to increment power 
                         // Small steps may cause +1 cycles due to truncation.
#define RPM_STEPS 4      // STEP * STEPS MUST NOT EXCEED 1


// MAIN setup and loop functions --------------------------------------------------

void setup()
{
  // Set PWM forward and reverse connections as outputs
  for (int i = 0; i < 4; i++) { pinMode(driver_pins[i], OUTPUT); }
}

void loop()
{
  while (run_cycles > 0) 
  {
    incremental_test(FORWARD);
    delay(PAUSE_TIME);

    incremental_test(REVERSE);
    delay(PAUSE_TIME);

    if (INCLUDE_TURNS) {

      incremental_test(LEFT_PIVOT);
      delay(PAUSE_TIME);

      incremental_test(RIGHT_PIVOT);
      delay(PAUSE_TIME);

      incremental_test(LEFT_SPIN);
      delay(PAUSE_TIME);

      incremental_test(RIGHT_SPIN);
      delay(PAUSE_TIME);

    }

    run_cycles--;
  }
}

// Function Declarations -------------------------------------------------

// incremental_test: Moves up through the power band incrementally
void incremental_test(String dir) 
{
  for (int i = 1; i <= RPM_STEPS; i++) {
    rpm = i * RPM_STEP * MAX_RPM;
    move(dir, rpm);
    delay(RUN_TIME);
  }
  rpm = 0;    // Should be redundant fail-safe, can probably remove
  stop();
}

void stop(void) { move(STOP, 0); }

// move: Sets rpm of each motor driver input in accordance with predefined movement patterns.
void move(String dir, uint8_t rpm)
{
  if      (dir == "stop")         { for (int i = 0; i < 4; i++) { set_rpm(driver_pins[i],        stop_pattern[i]); } }
  else if (dir == "forward")      { for (int i = 0; i < 4; i++) { set_rpm(driver_pins[i],     forward_pattern[i]); } }
  else if (dir == "reverse")      { for (int i = 0; i < 4; i++) { set_rpm(driver_pins[i],     reverse_pattern[i]); } }
  else if (dir == "left spin")    { for (int i = 0; i < 4; i++) { set_rpm(driver_pins[i],   left_spin_pattern[i]); } }
  else if (dir == "right spin")   { for (int i = 0; i < 4; i++) { set_rpm(driver_pins[i],  right_spin_pattern[i]); } }
  else if (dir == "left pivot")   { for (int i = 0; i < 4; i++) { set_rpm(driver_pins[i],  left_pivot_pattern[i]); } }
  else if (dir == "right pivot")  { for (int i = 0; i < 4; i++) { set_rpm(driver_pins[i], right_pivot_pattern[i]); } }
}

// set_rpm: Maps rpm input to PWM value between 0 and 255, then writes that value to the pin input
void set_rpm(int pin, uint8_t rpm) { analogWrite(pin, map(rpm, 0, 223, 0, 255)); }



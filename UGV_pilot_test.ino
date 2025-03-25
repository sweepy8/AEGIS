/*
UGV piloting test code v0.1 
March 20, 2025
AEGIS Senior Design

  This program runs on a single arduino nano. It sets the rpm of the left 
  and right side of the ugv independently and includes a function to move

TODO:
  Introduce mapping to percentage of usable rpm?
    - pct_pwr = map(0, 1, 60, 223);
*/


// VARIABLE declarations --------------------------------------------------

// Forward and reverse pins for left and right. 
// If one is PWM, make sure the other is LOW
#define LEFT_PWM_F  5
#define LEFT_PWM_R  6
#define RIGHT_PWM_F 13
#define RIGHT_PWM_R 14

#define FORWARD String("forward")
#define REVERSE String("reverse")

// TEST PARAMETERS
#define START_DELAY  5000    // milliseconds
#define UGV_RUN_TIME 5000    // milliseconds
uint8_t run_once = 1;

float rpm_pct = 0.5;           // 0 - 1
uint8_t rpm = rpm_pct * 223;   // 0 - 223

uint8_t driver_pins[4] = {LEFT_PWM_F, LEFT_PWM_R, RIGHT_PWM_F, RIGHT_PWM_R};

// Movement pattern arrays (symmetric with driver_pins array)
uint8_t forward_pattern[4] = {rpm, 0, rpm, 0};
uint8_t reverse_pattern[4] = {0, rpm, 0, rpm};
uint8_t stop_pattern[4]    = {0, 0, 0, 0};      


// MAIN setup and loop functions ------------------------------------------

void setup()
{
  // Set PWM forward and reverse connections as outputs
  for (int i = 0; i < 4; i++) { pinMode(driver_pins[i], OUTPUT); }
}

void loop()
{
  if (run_once) 
  {
    delay(START_DELAY);
    move(FORWARD, rpm);
    delay(UGV_RUN_TIME);
    stop();
    run_once = 0;
  }
}


// Function Declarations -------------------------------------------------

void set_rpm(int pin, int rpm)
{
  int duty_cycle = rpm * 255 / 223; // Set duty cycle (0-255) from rpm value (0-223)
  analogWrite(pin, duty_cycle);
}

void move(String dir, int rpm)
{
  if      (dir == "forward")  { for (int i = 0; i < 4; i++) { set_rpm(driver_pins[i], forward_pattern[i]); } }
  else if (dir == "reverse")  { for (int i = 0; i < 4; i++) { set_rpm(driver_pins[i], reverse_pattern[i]); } }
}

void stop(void)               { for (int i = 0; i < 4; i++) { analogWrite(driver_pins[i], stop_pattern[i]); } }

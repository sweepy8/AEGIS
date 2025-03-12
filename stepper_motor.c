#include <wiringPi.h>  
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>  // For usleep()
#include <errno.h>   // For error handling

// Define GPIO pins using physical numbering
#define DIR_PIN 16   // Direction pin (Physical pin 16)
#define STEP_PIN 18  // Step pin (Physical pin 18)
#define MS3_PIN 11   // MS3 pin (Physical pin 11)
#define MS2_PIN 13   // MS2 pin (Physical pin 13)
#define MS1_PIN 15   // MS1 pin (Physical pin 15)

#define STEP_DELAY 1000  // Microseconds between steps
#define STEPS_PER_REV 400  // Half-step mode (400 steps per revolution)

// Function to move stepper motor by a specified angle
void moveStepper(float angle, int direction) {
    int steps = (int)((angle / 360.0) * STEPS_PER_REV);

    // Set direction: HIGH for CW, LOW for CCW
    digitalWrite(DIR_PIN, direction ? HIGH : LOW);

    printf("Moving motor by %.2f degrees (%d steps)...\n", angle, steps);

    for (int i = 0; i < steps; i++) {
        digitalWrite(STEP_PIN, HIGH);
        usleep(STEP_DELAY);
        digitalWrite(STEP_PIN, LOW);
        usleep(STEP_DELAY);
    }

    printf("Movement complete.\n");
}

int main(void) {
    // Set up WiringPi using physical pin numbering
    if (wiringPiSetupPhys() == -1) {
        fprintf(stderr, "Failed to initialize WiringPi: %s\n", strerror(errno));
        return 1;
    }

    // Set pins as output
    pinMode(DIR_PIN, OUTPUT);
    pinMode(STEP_PIN, OUTPUT);
    pinMode(MS3_PIN, OUTPUT);
    pinMode(MS2_PIN, OUTPUT);
    pinMode(MS1_PIN, OUTPUT);

    // Set microstepping mode to HALF STEP (MS1 = 1, MS2 = 0, MS3 = 0)
    digitalWrite(MS3_PIN, LOW);
    digitalWrite(MS2_PIN, LOW);
    digitalWrite(MS1_PIN, HIGH);

    float angle;
    int direction;

    // Get user input
    printf("Enter angle to move (degrees): ");
    scanf("%f", &angle);
    
    printf("Enter direction (1 for CW, 0 for CCW): ");
    scanf("%d", &direction);

    // Move the stepper motor
    moveStepper(angle, direction);

    return 0;
}
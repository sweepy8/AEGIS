#include <wiringPi.h>  // Include WiringPi library
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>  // For usleep()

// Define GPIO pins using physical numbering
#define DIR_PIN 16   // Direction pin (Physical pin 16)
#define STEP_PIN 18  // Step pin (Physical pin 18)
#define MS3_PIN 11   // MS3 pin (Physical pin 11)
#define MS2_PIN 13   // MS2 pin (Physical pin 13)
#define MS1_PIN 15   // MS1 pin (Physical pin 15)

#define STEP_DELAY 1000  // Microseconds between steps

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

    // Set microstepping mode to FULL STEP (MS1 = 0, MS2 = 0, MS3 = 0)
    digitalWrite(MS3_PIN, LOW);
    digitalWrite(MS2_PIN, LOW);
    digitalWrite(MS1_PIN, LOW);

    // Set direction (1 for CW, 0 for CCW)
    digitalWrite(DIR_PIN, HIGH);

    printf("Rotating stepper motor one full revolution...\n");

    // Send 200 step pulses for one full revolution
    for (int i = 0; i < 200; i++) {
        digitalWrite(STEP_PIN, HIGH);
        usleep(STEP_DELAY);
        digitalWrite(STEP_PIN, LOW);
        usleep(STEP_DELAY);
    }

    printf("Rotation complete.\n");

    return 0;
}

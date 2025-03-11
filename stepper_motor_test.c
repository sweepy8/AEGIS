#include <wiringPi.h> // Include WiringPi library!
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <stdlib.h>
#include <time.h>

int main(void)
{

  /*
    int wiringPiSetupPinType(enum WPIPinType pinType)

    pinType: Type of PIN numbering...

    WPI_PIN_BCM ... BCM-Numbering
    WPI_PIN_WPI ... WiringPi-Numbering
    WPI_PIN_PHYS ... Physical Numbering

  */
  
// set up pins by physcial pin numbering
    wiringPiSetupPinType(WPI_PIN_PHYS);

  /*
    void pinMode(int pin, int mode)

    Pin: The desired PIN (BCM, Wiringpi or PIN number).
    Mode: The desired pin mode...

    INPUT ... Input
    OUTPUT ... Output
    PWM_OUTPUT ... PWM output (frequency and pulse break ratio can be configured)
    PWM_MS_OUTPUT ... PWM output with MS (Mark/Space) (since version 3)
    PWM_BAL_OUTPUT ... PWM output with mode balanced) (since version 3)
    GPIO_CLOCK ... Frequency output
    PM_OFF ... Release
  */
  
//set pins of driver  
    // set pin 16 to output (direction)
    pinMode(16, OUTPUT);
    
    // set pin 18 to output (step)
    pinMode(18, OUTPUT);
    
    // set pin 11 to output (MS3)
    pinMode(11, OUTPUT);
    
    // set pin 13 to output (MS2)
    pinMode(13, OUTPUT);
    
    // set pin 15 to output (MS1)
    pinMode(15, OUTPUT);
    

/*
    digitalWrite(int pin, int value)

    pin: The desired Pin (BCM-, Wiringpi- or PIN number).
    value: The logical value...

    HIGH ... Value 1 (electrical ~ 3.3 V)
    LOW ... Value 0 (electrical ~0 V / GND)

*/

//writing to pins
    
    //full step for 200 which is one revolution
    for () {
        DigitalWrite(11, LOW);
        DigitalWrite(13, LOW);
        DigitalWrite(15, LOW);
    }

  
}

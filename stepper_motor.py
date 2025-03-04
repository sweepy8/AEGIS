#######################################
# Copyright (c) 2021 Maker Portal LLC
# Author: Joshua Hrisko
#######################################
#
# NEMA 17 (17HS4023) Raspberry Pi Tests
# --- rotating the NEMA 17 to test
# --- wiring and motor functionality
#
#curl -sL https://github.com/gavinlyonsrepo/RpiMotorLib/archive/3.3.tar.gz | tar xz
#cd RpiMotorLib-3.3
#python3 setup.py build 
#python3 setup.py install --user
#######################################
#
import RPi.GPIO as GPIO
from RpiMotorLib import RpiMotorLib
import time

################################
# RPi and Motor Pre-allocations
################################
#
#define GPIO pins
#direction= 23 # Direction (DIR) GPIO Pin
#step = 24 # Step GPIO Pin
#EN_pin = 24 # enable pin (LOW to enable)

# Declare a instance of class pass GPIO pins numbers and the motor type
#mymotortest = RpiMotorLib.A4988Nema(direction, step, (21,21,21), "DRV8825")
#GPIO.setup(EN_pin,GPIO.OUT) # set enable pin as output

#define GPIO pins
GPIO_pins = (22, 27, 17) # Microstep Resolution MS1-MS3 -> GPIO Pin
direction= 23       # Direction -> GPIO Pin
step = 24      # Step -> GPIO Pin

# Declare an named instance of class pass GPIO pins numbers
mymotortest = RpiMotorLib.A4988Nema(direction, step, GPIO_pins, "A4988")

###########################
# Actual motor control
###########################
#
# call the function, pass the arguments
mymotortest.motor_go(False, "Full" , 100, .01, False, .05)

#GPIO.output(EN_pin,GPIO.LOW) # pull enable to low to enable motor
#mymotortest.motor_go(False, # True=Clockwise, False=Counter-Clockwise
 #                    "Full" , # Step type (Full,Half,1/4,1/8,1/16,1/32)
  #                   200, # number of steps
   #                  .0005, # step delay [sec]
    #                 False, # True = print verbose output 
     #                .05) # initial delay [sec]

#GPIO.cleanup() # clear GPIO allocations after run

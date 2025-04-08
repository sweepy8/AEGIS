#!/usr/bin/env python
"""
Motor Driver for AEGIS LiDAR Scanner

This module provides the Motor class used to control a stepper motor (via an A4988 driver)
mounted on a Raspberry Pi. The motor rotates the LiDAR sensor—whose scanning plane is in the ZY plane—
around the global Z-axis.

Pin assignments (BCM numbering) are as follows (adjust as necessary):
  - STEP_PIN: GPIO5    (step pulse)
  - DIR_PIN : GPIO6    (direction control)
  - MS1_PIN : GPIO22   (microstepping resolution control)
  - MS2_PIN : GPIO27   (microstepping resolution control)
  - MS3_PIN : GPIO17   (microstepping resolution control)

Author: [Your Name]
Date: [Current Date]
"""

import time
import RPi.GPIO as GPIO

class MicrostepResolution:
    def __init__(self, name: str, denom: int, value: tuple):
        """
        Initializes a microstepping resolution setting.
        
        Args:
            name (str): Name of the resolution (e.g., 'FULL', 'HALF').
            denom (int): Denominator value (number of microsteps per full step).
            value (tuple): Tuple of booleans representing the states of MS1, MS2, and MS3 pins.
        """
        self.name = name
        self.denom = denom
        self.value = value  # (MS1, MS2, MS3)

class Motor:
    def __init__(self):
        """
        Initialize the Motor driver by setting up the GPIO pins.
        """
        # Pin configuration (BCM numbering)
        self.STEP_PIN = 5
        self.DIR_PIN  = 6
        self.MS1_PIN  = 22
        self.MS2_PIN  = 27
        self.MS3_PIN  = 17

        # Setup GPIO mode and pins.
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.STEP_PIN, GPIO.OUT)
        GPIO.setup(self.DIR_PIN, GPIO.OUT)
        GPIO.setup(self.MS1_PIN, GPIO.OUT)
        GPIO.setup(self.MS2_PIN, GPIO.OUT)
        GPIO.setup(self.MS3_PIN, GPIO.OUT)

        # Default configuration.
        self.speed_hz = 1.0  # rotations per second
        self.direction = "CCW"  # default direction (Counter Clockwise)
        self.curr_angle = 0.0  # current position in degrees

        # Define available microstepping modes.
        self.resolutions = {
            "FULL":      MicrostepResolution("FULL", 1, (False, False, False)),
            "HALF":      MicrostepResolution("HALF", 2, (True, False, False)),
            "QUARTER":   MicrostepResolution("QUARTER", 4, (False, True, False)),
            "EIGHTH":    MicrostepResolution("EIGHTH", 8, (True, True, False)),
            "SIXTEENTH": MicrostepResolution("SIXTEENTH", 16, (True, True, True))
        }
        # Set default microstepping mode.
        self.ms_resolution = self.resolutions["FULL"]
        self.set_ms_res("SIXTEENTH")
        self.set_dir(self.direction)

    def set_speed(self, speed_hz: float):
        """
        Set the turning speed of the motor in rotations per second.
        
        Args:
            speed_hz (float): Motor speed in Hz.
        """
        self.speed_hz = speed_hz

    def set_dir(self, direction: str):
        """
        Set the motor's rotation direction.
        
        Args:
            direction (str): "CW" for clockwise or "CCW" for counter-clockwise.
        """
        self.direction = direction.upper()
        if self.direction == "CW":
            GPIO.output(self.DIR_PIN, GPIO.LOW)
        else:
            GPIO.output(self.DIR_PIN, GPIO.HIGH)

    def set_ms_res(self, resolution: str):
        """
        Set the microstepping resolution.
        
        Args:
            resolution (str): One of "FULL", "HALF", "QUARTER", "EIGHTH", "SIXTEENTH".
        """
        res_key = resolution.upper()
        if res_key in self.resolutions:
            self.ms_resolution = self.resolutions[res_key]
            ms_values = self.ms_resolution.value
            GPIO.output(self.MS1_PIN, ms_values[0])
            GPIO.output(self.MS2_PIN, ms_values[1])
            GPIO.output(self.MS3_PIN, ms_values[2])
        else:
            raise ValueError("Invalid microstepping resolution value. Must be one of: FULL, HALF, QUARTER, EIGHTH, SIXTEENTH.")

    def get_ms_denom(self):
        """
        Returns the microstepping denominator (number of microsteps per full step).
        
        Returns:
            int: The microstepping denominator.
        """
        return self.ms_resolution.denom

    def turn_degs(self, deg: float):
        """
        Rotate the motor by a specified number of degrees.
        
        Args:
            deg (float): Degrees to rotate.
        """
        # For a typical 200 full-step motor:
        full_steps_per_rev = 200
        total_steps = full_steps_per_rev * self.get_ms_denom()
        steps_to_move = int(round((deg / 360.0) * total_steps))
        if steps_to_move < 1:
            raise Exception("Turn amount is too small to move a single step.")
        
        # Calculate the delay per step.
        # Time for one full revolution: 1 / speed_hz seconds.
        # Delay per step = (1 / speed_hz) / total_steps.
        step_delay = 1.0 / (self.speed_hz * total_steps)
        
        for _ in range(steps_to_move):
            # Generate a pulse on the STEP_PIN.
            GPIO.output(self.STEP_PIN, GPIO.HIGH)
            time.sleep(step_delay / 2)
            GPIO.output(self.STEP_PIN, GPIO.LOW)
            time.sleep(step_delay / 2)
        
        # Update current angle (wrap around at 360 degrees).
        self.curr_angle = (self.curr_angle + deg) % 360

    def cleanup(self):
        """
        Clean up GPIO settings.
        """
        GPIO.cleanup()

if __name__ == "__main__":
    # Example test routine for the Motor driver.
    motor = Motor()
    motor.set_speed(1)           # 1 rotation per second.
    motor.set_ms_res("SIXTEENTH") 
    motor.set_dir("CCW")
    print("Rotating 90 degrees...")
    motor.turn_degs(90)
    print("Current angle: ", motor.curr_angle)
    motor.cleanup()

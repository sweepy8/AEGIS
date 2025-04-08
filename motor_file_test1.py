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
            raise ValueError("Invalid microstepping resolution value. Must be one of: FULL, HALF, QUARTER, EIGHTH,

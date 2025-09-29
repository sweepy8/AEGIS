# Address Map Utilities
# Created 9/28/2025

'''
This file is used to address and operate the status LEDs on the rover.
It uses the RGB Smart NeoPixels from Adafruit: www.adafruit.com/product/1312

They are arranged in a 4x4 matrix on the status board.

Install the Adafruit CircuitPython NeoPixel libraries:
    pip3 install adafruit-circuitpython
    pip3 install adafruit-circuitpython-pixelbuf
    pip3 install adafruit-circuitpython-neopixel

https://docs.circuitpython.org/projects/neopixel/en/latest/
    
Whoops, won't work. Needs PWM pin, and we didn't plan for that. Should use 
GPIO 10, 12, 18, or 21 for 800kHz PWM, can't bit bang that on linux :(
Maybe splice under boards? Also should drop LED Vdd with a diode to be able to
keep CMOS logic within 3.3V output range of R.Pi pins, and use a bulk cap

'''

import board
import neopixel

DATA_PIN = board.D10
num_pixels = 16
brightness = 0.2

pixels = neopixel.NeoPixel(
    DATA_PIN,
    num_pixels,
    brightness=brightness,
    auto_write=True     # Immediately update pixel state when written
)

#           RED, GRN, BLU
PX_OFF   = (  0,   0,   0)
PX_WHITE = (255, 255, 255)
PX_RED   = (255,   0,   0)
PX_GREEN = (  0, 255,   0)
PX_BLUE  = (  0,   0, 255)
PX_PURPLE= (255,   0, 255)
PX_YELLOW= (255, 255,   0)

LQ1_ADDR = 0
LQ2_ADDR = 1
LQ3_ADDR = 2
LQ4_ADDR = 3

USLF_ADDR = 4
USCT_ADDR = 5
USRT_ADDR = 6
USRR_ADDR = 7

LM_ADDR = 8
LMC_ADDR = 9
RM_ADDR = 12
RMC_ADDR = 13

RPI_ADDR = 10
CAM_ADDR = 11
ARD_ADDR = 14
BAT_ADDR = 15

def set_pixel(addr : int, color : tuple) -> None:
    if addr < 0 or addr > num_pixels - 1:
        raise ValueError("Invalid pixel index!")
    
    pixels[addr] = tuple([int(brightness * v) for v in color])

def map_ultrasonic_to_pixel(addr, dist_cm):
    if dist_cm > 100:
        set_pixel(addr, PX_GREEN)
    elif dist_cm < 100 and dist_cm >= 30:
        set_pixel(addr, PX_YELLOW)
    elif dist_cm < 30 and dist_cm >= 0:
        set_pixel(addr, PX_RED)
    else:
        set_pixel(addr, PX_WHITE)

def map_rpm_to_pixel(addr, avg_rpm):
    if avg_rpm > 125:
        set_pixel(addr, PX_RED)
    elif avg_rpm < 125 and avg_rpm >= 50:
        set_pixel(addr, PX_YELLOW)
    elif avg_rpm < 50 and avg_rpm > 0:
        set_pixel(addr, PX_GREEN)
    else:
        set_pixel(addr, PX_WHITE)

def map_mot_current_to_pixel(addr, avg_curr):
    if avg_curr > 4:
        set_pixel(addr, PX_RED)
    elif avg_curr < 4 and avg_curr >= 1:
        set_pixel(addr, PX_YELLOW)
    elif avg_curr < 1 and avg_curr > 0:
        set_pixel(addr, PX_GREEN)
    else:
        set_pixel(addr, PX_WHITE)

def map_batt_to_pixel(addr, pct):
    if pct > 75:
        set_pixel(addr, PX_GREEN)
    elif pct < 75 and pct >= 50:
        set_pixel(addr, PX_YELLOW)
    elif pct < 50 and pct > 25:
        set_pixel(addr, PX_RED)
    else:
        set_pixel(addr, PX_WHITE)
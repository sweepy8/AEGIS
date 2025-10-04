# Address Map Utilities
# Created 9/28/2025

'''
This file is used to address and operate the status LEDs on the rover.
It uses the RGB Smart NeoPixels from Adafruit: www.adafruit.com/product/1312

They are arranged in a 4x4 matrix on the status board.
    
Whoops, won't work. Needs PWM pin, and we didn't plan for that. Should use 
GPIO 10, 12, 18, or 21 for 800kHz PWM, can't bit bang that on linux :(
Maybe splice under boards? Also should drop LED Vdd with a diode to be able to
keep CMOS logic within 3.3V output range of R.Pi pins, and use a bulk cap

'''

import board
import neopixel
import time

DATA_PIN = board.D18
num_pixels = 16
brightness = 0.25

pixels = neopixel.NeoPixel(
    pin=DATA_PIN,
    n=num_pixels,
    bpp=3,
    brightness=brightness,
    auto_write=True     # Immediately update pixel state when written
)

#             R G B
PX_OFF    = 0x000000
PX_WHITE  = 0xFFFFFF
PX_RED    = 0xFF0000
PX_GREEN  = 0x00FF00
PX_BLUE   = 0x0000FF
PX_PURPLE = 0xFF00FF
PX_YELLOW = 0xFFFF00
PX_TEAL   = 0x00FFFF

colors = [
    PX_WHITE, PX_RED, PX_GREEN, PX_BLUE, PX_PURPLE, PX_YELLOW, PX_TEAL
]

'''
15  14  13  12     LI1 USF  LF  RF
08  09  10  11     LI2 USR  LM  RM
04  05  06  07     LI3 USL  LR  RR
00  01  02  03     RPM CAM ARD BAT
'''

LQ1_ADDR = 15
LQ2_ADDR = 8
LQ3_ADDR = 4

USFT_ADDR = 14
USRR_ADDR = 9
USLI_ADDR = 5

LF_ADDR = 13
RF_ADDR = 12
LM_ADDR = 10
RM_ADDR = 11
LR_ADDR = 6
RR_ADDR = 7

RPM_ADDR = 0
CAM_ADDR = 1
ARD_ADDR = 2
BAT_ADDR = 3

def set_pixel(addr : int, color) -> None:
    if addr < 0 or addr > num_pixels - 1:
        raise ValueError("Invalid pixel index!")

    pixels[addr] = color

def off() -> None:
    pixels.fill(PX_OFF)


# TESTS
def seq_fill(color) -> None:
    off()
    for i in range(len(pixels)):
        pixels[i] = color
        time.sleep(0.02)
    
    for i in range(len(pixels)):
        pixels[i] = PX_OFF
        time.sleep(0.02)
    off()

def colors_fill() -> None:
    off()
    for j in range(len(colors)):
        pixels.fill(colors[j])
        time.sleep(0.1)
    off()

def pulse_fill(color) -> None:
    off()
    for i in range(0, 100):
        pixels.brightness = i * 0.01
        pixels.fill(color)
        time.sleep(0.001)

    for i in range(0, 100):
        pixels.brightness = 1 - i * 0.01
        pixels.fill(color)
        time.sleep(0.001)

    pixels.brightness = brightness
    off()

if __name__ == "__main__":

    time.sleep(5)

    for i in range(len(colors)):
        seq_fill(colors[i])

    time.sleep(0.1)

    colors_fill()

    time.sleep(0.1)

    for i in range(len(colors)):
        pulse_fill(colors[i])

# XBOX Controller Input Capture
# AEGIS Senior Design, Created 6/13/2025
# Second try using xow --> evdev after an update killed xone --> inputs

# Uses inbuilt joystick api:
# https://www.kernel.org/doc/Documentation/input/joystick-api.txt
#
# And evdev library:
# https://python-evdev.readthedocs.io
#
# See EOF for specific controller characteristics

import asyncio
from evdev import InputDevice, list_devices
from time import sleep

XBOX_DEVICE_NAME = 'Xbox One Wireless Controller'

STICK_NORMALIZER_Y = -1 / 32768
STICK_NORMALIZER_X =  1 / 32768
TRIG_NORMALIZER    =  1 / 1023

INPUT_CODES = {
    315: 'BTN_START',
    304: 'BTN_A',  305: 'BTN_B', 307: 'BTN_X', 308: 'BTN_Y',
    310: 'BTN_TL', 311: 'BTN_TR', 
      2: 'BTN_Z',    3: 'ABS_RX',  4: 'ABS_RY',  5: 'BTN_RZ'
}

# To get controller state from another file, access dict 'input_states' directly.
input_states = { 'BTN_START' : 0,
    'BTN_A' : 0, 'BTN_B' : 0, 'BTN_X' : 0, 'BTN_Y' : 0,
    'BTN_TL': 0, 'BTN_TR': 0,
    'BTN_Z' : 0, 'ABS_RX': 0, 'ABS_RY': 0, 'BTN_RZ': 0
}

def get_event_path(dev_name : str) -> str:
    devices = [InputDevice(path) for path in list_devices()]
    dev_event_path = None
    for device in devices:
        #print(' ', device.path, device.name, device.phys)
        if device.name == dev_name:
            dev_event_path = device.path

    if dev_event_path is None:
        raise OSError('[INIT_ERROR] Event object path not found!')
    
    return dev_event_path

def normalize_input(name : str, value : int) -> int:
    if name in ['ABS_X', 'ABS_RX']:
        return round(value * STICK_NORMALIZER_X, 3)
    if name in ['ABS_Y', 'ABS_RY']:
        return round(value * STICK_NORMALIZER_Y, 3)
    if name in ['BTN_Z', 'BTN_RZ']:
        return round(value * TRIG_NORMALIZER, 3)
    return value

# Asynchronous approach
async def listener(dev, print_updates):

    async for event in dev.async_read_loop(): 
        if event.code in INPUT_CODES:
            event_name = INPUT_CODES[event.code]
            input_states[event_name] = normalize_input(event_name, event.value)

            if print_updates: 
                print(input_states)
            
        #print(dev.path, evdev.categorize(event), sep=': ') # Debug print

def listen(print_updates=0):
    '''
    Attempts to connect to a controller infinitely. Upon connection, runs the asynchronous
    listener function, which updates the controller input_state dict. Upon disconnection,
    an OSError is caught and the loop waits 5 seconds before trying to connect again.
    '''
    while True:
        try:
            xbox_event_path = get_event_path(XBOX_DEVICE_NAME)
            xb_device = InputDevice(xbox_event_path)

            print(f"[RUNTIME] controller.py: {XBOX_DEVICE_NAME} connected!")
            asyncio.run(listener(xb_device, print_updates))
        
        except OSError:
            print("[RUNTIME] controller.py: No controller detected! Searching every 5s...")
        
        finally:
            sleep(5)


if __name__ == '__main__':
    listen(print_updates=1)


"""
>>> device.capabilities(verbose=True)   # Returns the following:
{
    ('EV_SYN', 0): [
        ('SYN_REPORT', 0), 
        ('SYN_CONFIG', 1), 
        ('SYN_DROPPED', 3), 
        ('?', 21)], 
    ('EV_KEY', 1): [
        (('BTN_A', 'BTN_GAMEPAD', 'BTN_SOUTH'), 304),
        (('BTN_B', 'BTN_EAST'), 305),
        (('BTN_NORTH', 'BTN_X'), 307), 
        (('BTN_WEST', 'BTN_Y'), 308), 
        ('BTN_TL', 310), 
        ('BTN_TR', 311), 
        ('BTN_SELECT', 314), 
        ('BTN_START', 315), 
        ('BTN_MODE', 316), 
        ('BTN_THUMBL', 317), 
        ('BTN_THUMBR', 318)], 
    ('EV_ABS', 3): [
        (('ABS_X', 0),      AbsInfo(value=-2764,    min=-32768, max=32767,  fuzz=255,   flat=4095,  resolution=0)), 
        (('ABS_Y', 1),      AbsInfo(value=436,      min=-32768, max=32767,  fuzz=255,   flat=4095,  resolution=0)), 
        (('ABS_Z', 2),      AbsInfo(value=0,        min=0,      max=1023,   fuzz=3,     flat=63,    resolution=0)), 
        (('ABS_RX', 3),     AbsInfo(value=-591,     min=-32768, max=32767,  fuzz=255,   flat=4095,  resolution=0)), 
        (('ABS_RY', 4),     AbsInfo(value=-662,     min=-32768, max=32767,  fuzz=255,   flat=4095,  resolution=0)), 
        (('ABS_RZ', 5),     AbsInfo(value=0,        min=0,      max=1023,   fuzz=3,     flat=63,    resolution=0)), 
        (('ABS_HAT0X', 16), AbsInfo(value=0,        min=-1,     max=1,      fuzz=0,     flat=0,     resolution=0)),
        (('ABS_HAT0Y', 17), AbsInfo(value=0,        min=-1,     max=1,      fuzz=0,     flat=0,     resolution=0))], 
    ('EV_FF', 21): [
        (('FF_EFFECT_MIN', 'FF_RUMBLE'), 80)]
}
"""
# XBOX Controller Input Recognition
# AEGIS Senior Design, Created 5/23/2025

import inputs
import math
import threading
import time

class XboxController(object):
    
    MAX_TRIG_VAL = math.pow(2, 8)
    MAX_JOY_VAL = math.pow(2, 15)
        
    def __init__(self):
        self.A = 0
        self.X = 0
        self.Y = 0
        self.B = 0
        self.LeftJoystickY = 0
        self.LeftBumper = 0
        self.RightBumper = 0
    
        self._monitor_thread = threading.Thread(target=self._monitor_controller, args=())
        self._monitor_thread.daemon = True
        self._monitor_thread.start()

    def read(self):
        a = self.A
        x = self.X
        b = self.B
        y = self.Y

        ly = self.LeftJoystickY
        ly = int(-1*ly*255) if (abs(ly) > 0.05) else 0	#Normalize joystick from -254 to 255
        if ly == -254:
            ly = -253	# Not sure why it hates -254 but it won't read it. Fix later

        lb = self.LeftBumper
        rb = self.RightBumper

        return [a, x, b, y, ly, lb, rb]


    def _monitor_controller(self):
        while True:
            events = inputs.get_gamepad()
            for event in events:
                if event.code == 'ABS_Y':
                    self.LeftJoystickY = event.state / XboxController.MAX_JOY_VAL # -1 to 1
                if event.code == 'BTN_TL':
                    self.LeftBumper = event.state
                if event.code == 'BTN_TR':
                    self.RightBumper = event.state
                if event.code == 'BTN_SOUTH':
                    self.A = event.state
                if event.code == 'BTN_WEST':
                    self.B = event.state
                if event.code == 'BTN_EAST':
                    self.X = event.state
                if event.code == 'BTN_NORTH':
                    self.Y = event.state

if __name__ == '__main__':

    joy = XboxController()

    while True:
        time.sleep(0.1)
        if joy.controller_connected:
            print(joy.read())


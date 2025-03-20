# Library for A4988 Stepper motor driver and NEMA17 stepper motor

# Raspberry Pi 5 to A4988 Pinout:
#    Pin 31 == GPIO 6  --> DIRECTION
#    Pin 29 == GPIO 5  --> STEP
#    Pin 11 == GPIO 17 --> MS3
#    Pin 13 == GPIO 27 --> MS2
#    Pin 15 == GPIO 22 --> MS1


#   | MS1 | MS2 | MS3 |   Resolution   |
#   |-----|-----|-----|----------------|
#   |  0  |  0  |  0  | Full Step      |
#   |  1  |  0  |  0  | Half Step      |
#   |  0  |  1  |  0  | Quarter Step   |
#   |  1  |  1  |  0  | Eighth Step    |
#   |  1  |  1  |  1  | Sixteenth Step |


# TO DO
#   - Provide GPIO pin to the active-low enable input in order to
#     quickly disable the motor?


import gpiozero as gpz
from time import sleep


class microstep_resolution:
    
    def __init__(self):
        name = "NULL"
        value = -1
        denom = 1

    def __init__(self, name : str, denom : int, value : tuple):
        self.name = name
        self.value = value
        self.denom = denom


class Motor:
    
    microstep_resolutions = [
        microstep_resolution("FULL",       1, (0, 0, 0)),
        microstep_resolution("HALF",       2, (1, 0, 0)),
        microstep_resolution("QUARTER",    4, (0, 1, 0)),
        microstep_resolution("EIGHTH",     8, (1, 1, 0)),
        microstep_resolution("SIXTEENTH", 16, (1, 1, 1))
    ]

    def __init__(self):
        self.speed  = 1		# Speed in Hz
        self.dir    = gpz.OutputDevice(pin=6, initial_value=False) 
        self.step   = gpz.OutputDevice(pin=5, initial_value=False)
        self.ms_res = gpz.CompositeOutputDevice(
            gpz.OutputDevice(pin=22, initial_value=False),
            gpz.OutputDevice(pin=27, initial_value=False),
            gpz.OutputDevice(pin=17, initial_value=False)
        )
        
        self.curr_angle = None

    def set_speed(self, speed : int):
        self.speed = speed

    def set_dir(self, dir : str):
        if dir == "CW":
            self.dir.on()
        elif dir == "CCW":
            self.dir.off()
        else:
            raise Exception("Failed to set direction. Invalid input!")

    def set_start_angle(self):
        self.curr_angle = 0

    def turn_degs(self, deg : int):
        
        steps = (deg / 360) * (200 * self.get_ms_res_denom())
        if steps < 1:
            raise Exception("Turn amount is too small!")
        delay = 1 / (200 * self.get_ms_res_denom() * self.speed)

        print(f"Moving {steps} steps with delay of {delay}...")


        for i in range(0, int(steps)):
            self.step.on()
            sleep(delay / 2)        # 50% Duty Cycle
            self.step.off()
            sleep(delay / 2)
        
        self.curr_angle += deg
        self.curr_angle %= 360


    def set_ms_res(self, res : str):
        for msr in self.microstep_resolutions:
            print(f"MS_RES_NAME = {msr.name}")
            if msr.name == res:
                self.ms_res.value = msr.value
                return
        print(res)
        raise Exception("Invalid microstep resolution!")

    def get_ms_res_denom(self):
        for msr in self.microstep_resolutions:
            if msr.value == self.ms_res.value:
                return msr.denom
            
        raise Exception("Failed to retrieve MS_RES_DENOM.")
        
    
    def close(self):	# THIS IS AN EMERGENCY FUNCTION THAT SHOULD NOT REMAIN IN THIS LIBRARY
        self.dir.close()
        self.step.close()
        self.ms_res.close()

def main():
    M1 = Motor()
    M1.set_speed(4.5)	# 0 - 4.5
    M1.set_ms_res("SIXTEENTH")
    M1.set_start_angle()
    print(f"MS_RES set to {M1.ms_res.value}, ms_res_denom = {M1.get_ms_res_denom()}")

    M1.set_dir("CCW")
    for i in range(0, 180):
        M1.turn_degs(1)
        sleep(0.25)    
#     sleep(3)
    #M1.turn_degs(0)
    #M1.close()
    
    #for i in range(0, 1000):
    #    print(f"Spd={M1.speed}, Dir={M1.dir.value}, Step={M1.step.value}, msr={M1.ms_res.value}")

if __name__ == "__main__":
    main()
    
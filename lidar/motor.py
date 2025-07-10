'''
Motor driver for AEGIS senior design.
Compatible with A4988 Stepper motor driver and NEMA17 stepper motor.
'''

#################################
# Raspberry Pi to A4988 Pinout  #
#-------------------------------#
#   Pin 31 == GPIO 6  --> DIR   #
#   Pin 33 == GPIO 13 --> STEP  #
#   Pin 11 == GPIO 17 --> MS3   #
#   Pin 13 == GPIO 27 --> MS2   #
#   Pin 15 == GPIO 22 --> MS1   #
#   Pin  9 == GROUND            #
#   Pin  1 == VDD               #
#################################

#################################
# MS1 | MS2 | MS3 | Resolution  #
#-----|-----|-----|-------------#
#  0  |  0  |  0  | Full Step   #
#  1  |  0  |  0  | Half        #
#  0  |  1  |  0  | Quarter     #
#  1  |  1  |  0  | Eighth      #
#  1  |  1  |  1  | Sixteenth   #
#################################

import gpiozero as gpz		# gpz.OutputDevice, gpz.CompositeOutputDevice
from time import sleep

# Class to hold microstep resolution characteristics (move to tuple eventually)
class microstep_resolution:
    
    def __init__(self, name : str, denom : int, value : tuple):
        self.name = name
        self.value = value
        self.denom = denom


class Motor:
    '''
    Class intro **********************.
    '''
    
    # Array of all possible microstep resolutions as class instances
    microstep_resolutions = [
        microstep_resolution("FULL",       1, (0, 0, 0)),
        microstep_resolution("HALF",       2, (1, 0, 0)),
        microstep_resolution("QUARTER",    4, (0, 1, 0)),
        microstep_resolution("EIGHTH",     8, (1, 1, 0)),
        microstep_resolution("SIXTEENTH", 16, (1, 1, 1))
    ]


    def __init__(self):
        '''
        Initializes a motor object by attaching R.Pi GPIO pins to various fields and
        declaring the current angle and angle correction factor values.
        @param 
            None
        @return: 
            None
        '''
        
        self.speed  = 1.0												# Speed in Hz
        self.dir    = gpz.OutputDevice(pin=6, initial_value=False)		# Direction signal on GPIO 6 (pin 31)
        self.step   = gpz.OutputDevice(pin=13, initial_value=False)		# Step signal on GPIO 5 (pin 29)
        self.ms_res = gpz.CompositeOutputDevice(						# Microstep resolution on GPIO 17, 27, 22 (pins 11, 13, 15)
            gpz.OutputDevice(pin=22, initial_value=False),
            gpz.OutputDevice(pin=27, initial_value=False),
            gpz.OutputDevice(pin=17, initial_value=False)
        )
        
        self.curr_angle = None				# None implies "start angle not yet assigned"
        self.angle_correction_factor = 1.0	# Default to no prescribed angle correction (x1)

    def set_speed(self, speed : float):
        '''
        Sets the speed of the motor.
        @param 
            speed: Speed in Hz (0, 4.5]
        @return: 
            None
        '''

        self.speed = speed


    def set_dir(self, dir : str):
        '''
        Sets the direction of the motor.    
        Raises exception if string does not match either "CW" (clockwise) or "CCW" (counterclockwise).
        @param 
            dir: A string representing the direction of turn ("CW" or "CCW"). 
        @return: 
            None
        '''

        if   dir == "CW":  self.dir.on()
        elif dir == "CCW": self.dir.off()
        else: raise Exception("Failed to set direction. Invalid input!")


    def set_start_angle(self, angle : int):
        '''
        Sets the starting angle of the motor.
        @param 
            speed: Angle in degrees
        @return: 
            None
        '''
        self.curr_angle = angle
        

    def set_correction_factor(self, f : float):
        '''
        Sets the angular correction factor of the motor.
        The value is multiplied to the angle added to curr_angle after each movement.
        E.g. 1 degree per ring * 0.5 --> Despite physically moving 1 degree, prescribed
        angle only increases by 0.5 degrees
        @param 
            f: Correction factor multiplier
        @return: 
            None
        '''
        self.angle_correction_factor = f


    def turn_degs(self, deg : int):
        '''
        Turns the motor a set number of degrees.
        @param 
            speed: Speed in Hz
        @return: 
            None
        '''

        steps = (deg / 360) * (200 * self.get_ms_res_denom())
        if steps < 1:
            raise Exception("Turn amount is too small!")
        delay = 1 / (200 * self.get_ms_res_denom() * self.speed)

        print(f"Current Angle: {round(self.curr_angle, 3)}")
        
        for i in range(0, int(steps)):
            self.step.on()
            sleep(delay / 2)        # 50% Duty Cycle
            self.step.off()
            sleep(delay / 2)
        
        self.curr_angle += deg * self.angle_correction_factor
        

    def turn_steps(self, steps : int):
        '''
        ******************.
        '''
        deg = float(steps) / (200 * self.get_ms_res_denom()) * 360
        if steps < 1:
            raise Exception("Turn amount is too small!")
        delay = 1 / (200 * self.get_ms_res_denom() * self.speed)
        
        print(f"Current Angle: {round(self.curr_angle, 3)}")
        
        for i in range(0, steps):
            self.step.on()
            sleep(delay / 2)
            self.step.off()
            sleep(delay / 2)
        
        self.curr_angle += deg * self.angle_correction_factor
        
        
    def set_ms_res(self, res : str):        
        '''
        **************.
        '''
        for msr in self.microstep_resolutions:
            if msr.name == res:
                self.ms_res.value = msr.value
                return
        print(res)
        raise Exception("Invalid microstep resolution!")


    def get_ms_res_denom(self):
        '''
        ***************.
        '''
        for msr in self.microstep_resolutions:
            if msr.value == self.ms_res.value:
                return msr.denom
            
        raise Exception("Failed to retrieve MS_RES_DENOM.")
        

def main():
    '''
    This main function instantiates a motor object and turns the motor a set number of steps.
    @param None
    @return: None
    '''

    M1 = Motor()
    M1.set_speed(1)
    M1.set_ms_res("SIXTEENTH")
    M1.set_start_angle(0)
    print(f"MS_RES set to {M1.ms_res.value}, ms_res_denom = {M1.get_ms_res_denom()}")

    M1.set_dir("CW")
    for i in range(0, 180):
        M1.turn_steps(8)
        sleep(0.25)
        

if __name__ == "__main__":
    main()
    
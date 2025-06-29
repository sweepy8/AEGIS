'''
3D LiDAR scanner driver for AEGIS senior design.
Compatible with STL27L LiDAR sensor, A4988 motor driver, and NEMA17 stepper motor.
'''

import lidar.lidar as Lidar
import lidar.motor as Motor
import numpy as np				# deg2rad(), cos(), sin()
import time						# time(), sleep()

# Global motor parameters
MOTOR_TURN_SPD = 1				# (0, 4] Hz
MOTOR_TURN_DIR = "CCW"			# "CW" = clockwise or "CCW" = counterclockwise
MOTOR_TURN_RES = "SIXTEENTH"	# "FULL", "HALF", "QUARTER", "EIGTH", "SIXTEENTH"
MOTOR_TURN_RESET = False		# Turn back to initial position after scan?
MOTOR_CORRECTION_FACTOR = 1		# Scales prescribed motor turn. 0.5 --> 1 degree actual is 0.5 degrees prescribed
MOTOR_START_ANGLE = 0			# Initial motor angle in software (for coordinate transform)

#Global scan parameters
END_ANGLE = 180			# Span == END_ANGLE - MOTOR_START_ANGLE
USE_STEPS = True		# Use steps (or degrees) to increment rings?
DEG_PER_RING = 1		# Number of degrees between each ring (if using degrees)
NUM_RINGS = 200			# Number of rings to capture per scan (if using steps)
STEPS_PER_RING = 8		# NUM_RINGS * STEPS_PER_RING == 0.5 revs * 200 steps/rev * MOTOR_TURN_RES_DENOM


'''
This function converts an array of points from spherical to cartesian coordinates.
@param pts: An array of 4-element arrays containing point data (rho, phi, theta, intensity)
@return: The converted array of 4-element arrays containing point data (x, y, z, intensity)
'''
def conv_pts_sph_to_cart(pts):
    
    c_pts = []
    sensor_offset = 0.044 # Horizontal lidar offset in meters
    
    for pt in pts:
        c_pt = []
        
        dist = pt[0]								# radial distance rho in meters
        l_angle = np.deg2rad(pt[1])					# lidar angle phi in radians
        m_angle = np.deg2rad(pt[2])					# motor angle theta in radians
        
        x = dist*np.sin(l_angle)*np.cos(m_angle)	# x = r*sin(phi)*cos(theta)
        y = dist*np.sin(l_angle)*np.sin(m_angle)	# y = r*sin(phi)*sin(theta)
        z = dist*np.cos(l_angle)					# z = r*cos(phi)
        i = pt[3]									# intensity
        
        x = x + sensor_offset*np.sin(m_angle)		# Correct for horizontal lidar offset
        y = y + sensor_offset*np.cos(m_angle)		# Correct for horizontal lidar offset
        
        c_pt.extend([x, y, z, i])					# Add dimensions to cartesian point
        c_pts.append(c_pt)							# Add cartesian point to points array
        
    return c_pts

'''
This main function instantiates a motor and lidar unit, takes a spherical scan, and
    writes the processed data to two PCD files.
@param None
@return: None
'''
def main():
    
    # Initialize motor object and configure using global parameters
    M1 = Motor.Motor()
    M1.set_dir(MOTOR_TURN_DIR)
    M1.set_speed(MOTOR_TURN_SPD)
    M1.set_ms_res(MOTOR_TURN_RES)
    M1.set_start_angle(MOTOR_START_ANGLE)
    M1.set_correction_factor(MOTOR_CORRECTION_FACTOR)
    
    # Initialize LiDAR object
    L1 = Lidar.Lidar()
    
    start_time = time.time()		# Start scan timer
    
    # Take as many scans as fit into span according to global parameters
    file_data = []
    while M1.curr_angle < END_ANGLE:
    
        # Open serial connection FOR EACH RING! THIS SHOULD BE IMPROVED
        L1.open_serial()
       
        pts = L1.get_processed_ring(
            motor_angle = M1.curr_angle)	# Get a ring (formatted into array of spherical points)
        
        file_data.extend(pts)				# Add ring of points to end of file_data array

        # Rotate motor according to preferred units
        if USE_STEPS: M1.turn_steps(STEPS_PER_RING)
        else:		  M1.turn_degs(DEG_PER_RING)
        
        L1.close_serial()
                
        
    print(f"Data captured! Num pts: {len(file_data)}. Elapsed time: {round(time.time()-start_time, 1)} seconds.")
    
#     pcd_filename_pre = L1.make_file()								# Create PCD file to store raw data    
#     L1.write_pcd_header_to_file(pcd_filename_pre+"_raw", len(file_data)) 	# PCD header requires number of points in cloud
#     L1.write_pts_to_file(pcd_filename_pre, file_data)				# Write raw points to file
#     print(f"Raw points written to file! Elapsed time: {round(time.time()-start_time, 1)} seconds.")

    # Convert all points from spherical (r, phi, theta) coordinates to cartesian (x, y, z)
    file_data = conv_pts_sph_to_cart(file_data)
    print(f"Points converted! Elapsed time: {round(time.time()-start_time, 1)} seconds.")
    
    #time.sleep(1)												# Ensure that file names are unique
    pcd_filename = L1.make_file()								# Create PCD file to store converted data
    L1.write_pcd_header_to_file(pcd_filename, len(file_data))	# PCD header requires number of points in cloud
    L1.write_pts_to_file(pcd_filename, file_data)				# Write converted points to file
    print(f"Processed points written to file! Elapsed time: {round(time.time()-start_time, 1)} seconds.")
    
    # Rotate the motor in the opposite direction to the starting point
    #if MOTOR_TURN_RESET:
    #    M1.set_dir("CCW") if MOTOR_TURN_DIR == "CW" else M1.set_dir("CW")
    #    M1.turn_degs(END_ANGLE / MOTOR_CORRECTION_FACTOR) 
    
if __name__ =="__main__":
    main()
    
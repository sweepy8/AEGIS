# Zach's code but updated to match new idea
# Celeste's hopeful fix

# use other driver files and add libraries
import lidar_test as Lidar
import motor_driver as Motor
import numpy as np
import time

# set global variables for motor diver
MOTOR_TURN_SPD = 1			# 0 - 4.5 Hz
MOTOR_TURN_DIR = "CCW"
MOTOR_TURN_RES = "SIXTEENTH"
MOTOR_TURN_RESET = False
MOTOR_CORRECTION_FACTOR = 1 #none

# set global variables for our use
NUM_RINGS = 200
USE_STEPS = True
DEG_PER_RING = 1
STEPS_PER_RING = 8

# function to convert spherical coordiantes to cartesian
def conv_pts_sph_to_cart(pts):
    c_pts = []
    sensor_offset = 0.044  # sensor offset in meters (adjust as needed)

    for pt in pts:
        c_pt = []
        
        # assign variables (rho, theta, phi); theta and phi in degrees in 'pt'
        rho = pt[0]
        theta = np.deg2rad(pt[1])  # theta now in radians
        phi = np.deg2rad(pt[2])    # phi now in radians
        
        # restrict theta to (0, π) i.e., (0, 180°)
        if (theta > 0) and (theta < np.pi):         
            # convert to (x,y,z)
            x = rho * np.sin(theta) * np.cos(phi)   # x = r*sin(theta)*cos(phi)
            y = rho * np.sin(theta) * np.sin(phi)   # y = r*sin(theta)*sin(phi)
            z = rho * np.cos(theta)                 # z = r*cos(theta)
        else:
            # If theta is out-of-bound, discard or set to (0,0,0)
            x = 0
            y = 0
            z = 0
                  
        # If the sensor offset is a horizontal offset from the center, correct using the azimuth angle (phi)
        # Otherwise, if the offset is along the z-axis, adjust z instead.
        x = x + sensor_offset * np.cos(phi)   # horizontal offset correction on x
        y = y + sensor_offset * np.sin(phi)   # horizontal offset correction on y
        # For a z-axis offset, you might instead do:
        # z = z + sensor_offset
        
        i = pt[3]  # intensity
        
        c_pt.extend([x, y, z, i])
        c_pts.append(c_pt)  # Add Cartesian point with intensity to points array
        
    return c_pts


def main():
    
    # Initialize motor object
    M1 = Motor.Motor()
    M1.set_speed(MOTOR_TURN_SPD)
    M1.set_ms_res(MOTOR_TURN_RES)
    M1.set_dir(MOTOR_TURN_DIR)
    M1.set_start_angle(0)
    M1.set_correction_factor(MOTOR_CORRECTION_FACTOR)
    
    # Initialize LiDAR object
    L1 = Lidar.Lidar()
    L1.open_serial()	# Open LIDAR serial connection

    # file containing coordinates
    pcd_filename = L1.make_file()
    
    # for using sleep
    start_time = time.time()
    
    # open data for writing to file
    file_data = []

    # 0 to 360
    while M1.curr_angle < 360:
        
        pts = L1.get_processed_ring(motor_angle = M1.curr_angle)
        file_data.extend(pts)
        
        M1.turn_steps(STEPS_PER_RING) if USE_STEPS else M1.turn_degs(DEG_PER_RING)
        time.sleep(0.01)
        
    # write to terminal data is finished
    print(f"Data captured! Num pts: {len(file_data)}, Elapsed time: {round(time.time()-start_time, 4)} seconds")
    
    # convert points captured
    file_data = conv_pts_sph_to_cart(file_data)

    # write to terminal conversion is finished
    print(f"Points converted to Cartesian coordinates! Elapsed time: {round(time.time()-start_time, 4)} seconds")
   
    # write converted points to file
    L1.write_pcd_header_to_file(pcd_filename, len(file_data))
    L1.write_pts_to_file(pcd_filename, file_data)

    # write to terminal points to file finished
    print(f"Points written to file! Elapsed time: {round(time.time()-start_time, 4)} seconds.")
    
    # reset motor driver
    if MOTOR_TURN_RESET:
        M1.set_dir("CCW") if MOTOR_TURN_DIR == "CW" else M1.set_dir("CW")
        M1.turn_degs(360 / MOTOR_CORRECTION_FACTOR) 
    
if __name__ =="__main__":
    main()
    
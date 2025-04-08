#Scanning program for AEGIS LiDAR Module

import lidar_test as Lidar
import motor_driver as Motor
import numpy as np
import time

MOTOR_TURN_SPD = 1			# 0 - 4.5 Hz
MOTOR_TURN_DIR = "CCW"
MOTOR_TURN_RES = "SIXTEENTH"
MOTOR_TURN_RESET = False
MOTOR_CORRECTION_FACTOR = 0.5

NUM_RINGS = 200
USE_STEPS = True
DEG_PER_RING = 1
STEPS_PER_RING = 8


def conv_pts_sph_to_cart(pts):
    
    c_pts = []
    sensor_offset = 0.044 # 1.8 inch radius off z axis == 0.04572 meters
    
    for pt in pts:
        c_pt = []
        
        rho = pt[0]
        phi = np.deg2rad(pt[1])
        theta = np.deg2rad(pt[2])
        
        # Wrap around
        #if theta > np.pi:
        #    theta -= 2*np.pi
        
        # Old transform: works but has problems in q1 and q3
        #x = rho*np.sin(phi)*np.cos(theta)	# x = r*sin(phi)*cos(theta)
        #y = rho*np.sin(phi)*np.sin(theta)	# y = r*sin(phi)*sin(theta)
        #z = rho*np.cos(phi)	# z = r*cos(phi)
        
        # Updated transform: hacky way to flip quadrants 2 and 4?
        if (0 <= theta <= (np.pi/2)) or (np.pi <= theta <= 3/2*np.pi):
            x = rho*np.sin(phi)*np.cos(theta)
            y = rho*np.sin(phi)*np.sin(theta)
        else:
            x = -rho*np.sin(phi)*np.sin(theta)	# x = r*sin(phi)*cos(theta)
            y = -rho*np.sin(phi)*np.cos(theta)	# y = r*sin(phi)*sin(theta)
        z = rho*np.cos(phi)	# z = r*cos(phi)
        
        i = pt[3]	# intensity
        
        x = x + sensor_offset*np.cos(theta)		# Correct for z axis offset of LiDAR
        y = y + sensor_offset*np.sin(theta)		# Correct for z axis offset of LiDAR
        
        c_pt.extend([x, y, z, i])
        c_pts.append(c_pt)	# Add cartesian point with intensity to points array
        
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

    pcd_filename = L1.make_file()
    
    start_time = time.time()
    
    file_data = []
    while M1.curr_angle < 90:
        
        pts = L1.get_processed_ring(motor_angle=M1.curr_angle)
        file_data.extend(pts)
        
        M1.turn_steps(STEPS_PER_RING) if USE_STEPS else M1.turn_degs(DEG_PER_RING)
        time.sleep(0.01)
        
        
    M1.curr_angle = 180;
    
    while M1.curr_angle < 270:
        
        pts = L1.get_processed_ring(motor_angle=M1.curr_angle)
        file_data.extend(pts)
        
        M1.turn_steps(STEPS_PER_RING) if USE_STEPS else M1.turn_degs(DEG_PER_RING)
        time.sleep(0.01)
        
    print(f"Data captured! Num pts: {len(file_data)}, Elapsed time: {round(time.time()-start_time, 4)} seconds")
    
    file_data = conv_pts_sph_to_cart(file_data)
    print(f"Points converted to Cartesian coordinates! Elapsed time: {round(time.time()-start_time, 4)} seconds")
   
    L1.write_pcd_header_to_file(pcd_filename, len(file_data))
    L1.write_pts_to_file(pcd_filename, file_data)
    print(f"Points written to file! Elapsed time: {round(time.time()-start_time, 4)} seconds.")
    
    if MOTOR_TURN_RESET:
        M1.set_dir("CCW") if MOTOR_TURN_DIR == "CW" else M1.set_dir("CW")
        M1.turn_degs(180 / MOTOR_CORRECTION_FACTOR) 
    
if __name__ =="__main__":
    main()
    
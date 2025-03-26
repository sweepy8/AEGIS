#Scanning program for AEGIS LiDAR Module

import lidar_test as Lidar
import motor_driver as Motor
import numpy as np
import time

NUM_RINGS = 360
DEG_PER_RING = 1

MOTOR_TURN_SPD = 1			# 0 - 4.5 Hz
MOTOR_TURN_DIR = "CCW"
MOTOR_TURN_RES = "SIXTEENTH"

def conv_pts_sph_to_cart(pts):
    
    c_pts = []
    
    for pt in pts:
        c_pt = []
        c_pt.append(round(pt[0]*np.sin(np.deg2rad(pt[1]))*np.cos(np.deg2rad(pt[2])), 4))	# x = r*sin(phi)*cos(theta)
        c_pt.append(round(pt[0]*np.sin(np.deg2rad(pt[1]))*np.sin(np.deg2rad(pt[2])), 4))	# y = r*sin(phi)*sin(theta)
        c_pt.append(round(pt[0]*np.cos(np.deg2rad(pt[1])), 4))								# z = r*cos(phi)
        c_pt.append(pt[3])																	# Intensity
        c_pts.append(c_pt)	# Add cartesian point with intensity to points array
        
    return c_pts


def main():
    
    # Initialize motor object
    M1 = Motor.Motor()
    M1.set_speed(MOTOR_TURN_SPD)
    M1.set_ms_res(MOTOR_TURN_RES)
    M1.set_dir(MOTOR_TURN_DIR)
    M1.curr_angle = 0
    
    # Initialize LiDAR object
    L1 = Lidar.Lidar()
    L1.open_serial()	# Open LIDAR serial connection

    pcd_filename = L1.make_file()
    
    start_time = time.time()
    
    file_data = []
    for i in range(0, NUM_RINGS):
        
        pts = []
        while (len(pts) / 12 < L1.max_packets * L1.hit_rate_threshold):
            pts = []
            print("Requesting %d points (%d packets)..." % (L1.max_packets * 12, L1.max_packets), end='')
            for p in L1.get_packets(L1.max_packets, no_vis=1):
                for pt in L1.process_packet(p, motor_angle = M1.curr_angle):                    
                    pts.append(pt)
            print(f" Recieved {len(pts)} points...")
        
        file_data.extend(pts)
        M1.turn_degs(DEG_PER_RING)
        
    print(f"Data captured! Num pts: {len(file_data)}, Elapsed time: {round(time.time()-start_time, 4)} seconds")
    
    file_data = conv_pts_sph_to_cart(file_data)
    
    print("Points converted to Cartesian coordinates! Elapsed time: {round(time.time()-start_time, 4)} seconds")
    print("Writing points to text file... ", end='')
   
    L1.write_pcd_header_to_file(pcd_filename, len(file_data))
    L1.write_pts_to_file(pcd_filename, file_data)
    
    print(f"Points written to file! Elapsed time: {round(time.time()-start_time, 4)} seconds.")
    
if __name__ =="__main__":
    main()
    
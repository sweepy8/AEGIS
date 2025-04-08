#!/usr/bin/env python
"""
Updated Scanning Program for AEGIS LiDAR Module

This program collects point data from the LiDAR sensor using a stepper motor.
The sensor is mounted so that its scanning plane is the ZY plane (vertical).
The motor rotates the sensor about the global Z-axis.
The points are converted from the sensor’s local (ZY) coordinates into
global Cartesian coordinates using a custom conversion function.
"""

import lidar_test as Lidar
import motor_driver as Motor
import numpy as np
import time

NUM_RINGS = 360
DEG_PER_RING = 1

MOTOR_TURN_SPD = 1            # motor speed in Hz (0 - 4.5 Hz)
MOTOR_TURN_DIR = "CCW"
MOTOR_TURN_RES = "SIXTEENTH"

def conv_pts_zy_to_cart(pts):
    """
    Converts LiDAR points from the sensor's local frame (scanning in the ZY plane)
    to global Cartesian coordinates after applying a motor rotation about the Z-axis.
    
    Each input point has the format:
      [pt_dist, sensor_angle, motor_angle, intensity]
    
    Where:
      - pt_dist: measured distance (r) in meters.
      - sensor_angle: angle (in degrees) of the point within the sensor's scan (ZY plane).
                      (For a vertical scan, this is the angle from the sensor's Z-axis.)
      - motor_angle: current rotation (in degrees) provided by the stepper motor.
      - intensity: reflectivity or intensity measure.
    
    The conversion process is as follows:
      1. In the sensor’s local frame:
           y_local = r * sin(sensor_angle)
           z_local = r * cos(sensor_angle)
           x_local = 0
      2. The sensor’s local point is rotated about the global Z-axis using motor_angle:
           x_global = - y_local * sin(motor_angle)
           y_global =   y_local * cos(motor_angle)
           z_global =   z_local
    """
    c_pts = []
    for pt in pts:
        r = pt[0]
        sensor_angle = pt[1]   # in degrees (in the sensor's ZY plane)
        motor_angle = pt[2]    # in degrees (rotation about the Z-axis)
        intensity = pt[3]
        
        # Convert degrees to radians.
        sensor_rad = np.deg2rad(sensor_angle)
        motor_rad = np.deg2rad(motor_angle)
        
        # Sensor's local coordinates in the ZY plane.
        y_local = r * np.sin(sensor_rad)
        z_local = r * np.cos(sensor_rad)
        x_local = 0  # no variation because the sensor scans only in ZY.
        
        # Rotate the point about the Z-axis by motor_angle.
        # Since x_local is 0, the transformed coordinates become:
        x_global = -y_local * np.sin(motor_rad)
        y_global =  y_local * np.cos(motor_rad)
        z_global =  z_local
        
        c_pts.append([round(x_global, 4), round(y_global, 4), round(z_global, 4), intensity])
    return c_pts

def main():
    # Initialize the motor.
    M1 = Motor.Motor()
    M1.set_speed(MOTOR_TURN_SPD)
    M1.set_ms_res(MOTOR_TURN_RES)
    M1.set_dir(MOTOR_TURN_DIR)
    M1.curr_angle = 0  # start at 0 degrees.
    
    # Initialize the LiDAR sensor.
    L1 = Lidar.Lidar()
    L1.open_serial()  # Open LiDAR serial connection.
    
    pcd_filename = L1.make_file()
    
    start_time = time.time()
    file_data = []
    
    # Collect a complete scan by rotating the sensor NUM_RINGS times.
    for i in range(0, NUM_RINGS):
        pts = []
        # Ensure we have enough points from the sensor for a complete scan.
        while (len(pts) / 12 < L1.max_packets * L1.hit_rate_threshold):
            pts = []
            print("Requesting %d points (%d packets)..." % (L1.max_packets * 12, L1.max_packets), end='')
            for p in L1.get_packets(L1.max_packets, no_vis=1):
                for pt in L1.process_packet(p, motor_angle=M1.curr_angle):
                    pts.append(pt)
            print(" Received %d points." % len(pts))
        file_data.extend(pts)
        M1.turn_degs(DEG_PER_RING)
    
    elapsed = time.time() - start_time
    print("Data captured! Number of points: %d, Elapsed time: %.4f seconds" % (len(file_data), elapsed))
    
    # Convert the collected points to global Cartesian coordinates.
    file_data = conv_pts_zy_to_cart(file_data)
    print("Points converted to global Cartesian coordinates using ZY plane transformation!")
    
    # Write the converted points to a PCD file.
    print("Writing points to file...", end='')
    L1.write_pcd_header_to_file(pcd_filename, len(file_data))
    L1.write_pts_to_file(pcd_filename, file_data)
    print(" Points written to file!")
    
if __name__ == "__main__":
    main()

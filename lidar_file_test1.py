#!/usr/bin/env python
"""
LiDAR Driver for AEGIS Senior Design
Compatible with LD20 and STL27L LiDAR sensors

Baudrates:
  LD20:   230400 bps
  STL27L: 921600 bps

Note:
  The sensor scanning plane is assumed to be the ZY plane.
  Each processed packet returns 12 points with the format:
     [distance (meters), sensor_angle (degrees in the ZY plane), motor_angle (degrees), intensity]
"""

import numpy
import serial
import time
import datetime

class Lidar:
    CRCTABLE = [
        0x00, 0x4d, 0x9a, 0xd7, 0x79, 0x34, 0xe3, 0xae, 0xf2, 0xbf, 0x68, 0x25, 0x8b, 0xc6, 0x11, 0x5c,
        0xa9, 0xe4, 0x33, 0x7e, 0xd0, 0x9d, 0x4a, 0x07, 0x5b, 0x16, 0xc1, 0x8c, 0x22, 0x6f, 0xb8, 0xf5,
        0x1f, 0x52, 0x85, 0xc8, 0x66, 0x2b, 0xfc, 0xb1, 0xed, 0xa0, 0x77, 0x3a, 0x94, 0xd9, 0x0e, 0x43,
        0xb6, 0xfb, 0x2c, 0x61, 0xcf, 0x82, 0x55, 0x18, 0x44, 0x09, 0xde, 0x93, 0x3d, 0x70, 0xa7, 0xea,
        0x3e, 0x73, 0xa4, 0xe9, 0x47, 0x0a, 0xdd, 0x90, 0xcc, 0x81, 0x56, 0x1b, 0xb5, 0xf8, 0x2f, 0x62,
        0x97, 0xda, 0x0d, 0x40, 0xee, 0xa3, 0x74, 0x39, 0x65, 0x28, 0xff, 0xb2, 0x1c, 0x51, 0x86, 0xcb,
        0x21, 0x6c, 0xbb, 0xf6, 0x58, 0x15, 0xc2, 0x8f, 0xd3, 0x9e, 0x49, 0x04, 0xaa, 0xe7, 0x30, 0x7d,
        0x88, 0xc5, 0x12, 0x5f, 0xf1, 0xbc, 0x6b, 0x26, 0x7a, 0x37, 0xe0, 0xad, 0x03, 0x4e, 0x99, 0xd4,
        0x7c, 0x31, 0xe6, 0xab, 0x05, 0x48, 0x9f, 0xd2, 0x8e, 0xc3, 0x14, 0x59, 0xf7, 0xba, 0x6d, 0x20,
        0xd5, 0x98, 0x4f, 0x02, 0xac, 0xe1, 0x36, 0x7b, 0x27, 0x6a, 0xbd, 0xf0, 0x5e, 0x13, 0xc4, 0x89,
        0x63, 0x2e, 0xf9, 0xb4, 0x1a, 0x57, 0x80, 0xcd, 0x91, 0xdc, 0x0b, 0x46, 0xe8, 0xa5, 0x72, 0x3f,
        0xca, 0x87, 0x50, 0x1d, 0xb3, 0xfe, 0x29, 0x64, 0x38, 0x75, 0xa2, 0xef, 0x41, 0x0c, 0xdb, 0x96,
        0x42, 0x0f, 0xd8, 0x95, 0x3b, 0x76, 0xa1, 0xec, 0xb0, 0xfd, 0x2a, 0x67, 0xc9, 0x84, 0x53, 0x1e,
        0xeb, 0xa6, 0x71, 0x3c, 0x92, 0xdf, 0x08, 0x45, 0x19, 0x54, 0x83, 0xce, 0x60, 0x2d, 0xfa, 0xb7,
        0x5d, 0x10, 0xc7, 0x8a, 0x24, 0x69, 0xbe, 0xf3, 0xaf, 0xe2, 0x35, 0x78, 0xd6, 0x9b, 0x4c, 0x01,
        0xf4, 0xb9, 0x6e, 0x23, 0x8d, 0xc0, 0x17, 0x5a, 0x06, 0x4b, 0x9c, 0xd1, 0x7f, 0x32, 0xe5, 0xa8
    ]
    
    def __init__(self):
        self.name         = 'STL27L'
        self.max_packets  = 245    # STL27L: 245 packets per scan, LD20: 80 packets.
        self.packet_size  = 47
        self.start_byte   = 0x54
        self.hit_rate_threshold = 0.8
        
        self.serial_conn = serial.Serial()
        self.port_name   = '/dev/ttyAMA0'
        self.baudrate    = 921600  # STL27L Baud rate.
        self.byte_size   = 8
        self.parity_bits = 'N'
        self.stop_bits   = 1
        self.timeout     = 0       # Non-blocking mode.
        
    def open_serial(self):
        self.serial_conn.port     = self.port_name
        self.serial_conn.baudrate = self.baudrate
        self.serial_conn.bytesize = self.byte_size
        self.serial_conn.parity   = self.parity_bits
        self.serial_conn.stopbits = self.stop_bits
        self.serial_conn.timeout  = self.timeout
        self.serial_conn.open()
        time.sleep(0.05)  # Allow serial connection to stabilize.
    
    def close_serial(self):
        if self.serial_conn.is_open:
            self.serial_conn.close()
    
    def get_packets(self, packets, show=0, no_vis=0):
        data_arr = []
        for p in range(0, packets):
            data = self.serial_conn.read(self.packet_size)
            if show:
                print("\n#%3.3d (L=%2.2d): " % (p, len(data)), end='')
            if len(data) != self.packet_size:
                if show:
                    print("Incorrect Packet Size! N =", len(data), end='')
                packets += 1
                continue
            if data[0] != self.start_byte:
                if show:
                    print("Misaligned Packet!", end='')
                self.serial_conn.read_until(str(self.start_byte))
                packets += 1
                continue
            if data[self.packet_size-1] != self.calc_crc8(data):
                if show:
                    print("Incorrect Checksum!", end='')
                self.serial_conn.read_until(str(self.start_byte))
                packets += 1
                continue
            data_arr.append(data)
            if show:
                for b in data:
                    print("%2.2x" % b, end=' ')
                print(" Appended packet %3.3d!" % p, end='')
            if no_vis:
                time.sleep(0.001)
        if show: 
            print("\nFunction get_scan finished!")
        return data_arr
    
    def process_packet(self, p, show=0, motor_angle=0):
        """
        Processes a LiDAR data packet and returns 12 points.
        
        Each point is returned as:
          [distance (meters), sensor_angle (degrees, in the ZY plane),
           motor_angle (degrees), intensity]
        
        The sensor_angle is computed from the start and end angles encoded in the packet.
        The motor_angle (passed in as a parameter) is added to each point.
        """
        speed = p[3] * (2**8) + p[2]
        start_angle = p[5] * (2**8) + p[4]
        end_angle = p[43] * (2**8) + p[42]
        timestamp = p[45] * (2**8) + p[44]
        
        angle_delta = numpy.abs((end_angle - start_angle)) / (12 - 1)
        pts_arr = []
        for i in range(0, 12):
            pt_dist = ( p[6 + 3*i + 1] * (2**8) + p[6 + 3*i] ) / 1000  # distance in meters.
            pt_angle = ( start_angle + angle_delta * i ) / 100  # sensor angle in degrees.
            pt_intensity = p[6 + 3*i + 2]
            pts_arr.append([pt_dist, pt_angle, motor_angle, pt_intensity])
        if show:
            print("\nPacket Info: SB=%2.2x|VL=%2.2x|SP=%d|ST_A=%d|E_A=%d|TIME=%d" % 
                  (p[0], p[1], speed, start_angle, end_angle, timestamp))
            print(" Data: ", end='')
            for pt in pts_arr:
                print("(D=%.4f|A=%.4f|M=%.4f|I=%d)" % (pt[0], pt[1], pt[2], pt[3]), end=' ')
        return pts_arr
    
    def calc_crc8(self, packet):
        crc = 0
        for i in range(0, self.packet_size - 1):
            crc = self.CRCTABLE[(crc ^ packet[i]) & 0xff]
        return crc
    
    def make_file(self):
        timestamp = datetime.datetime.now().strftime("%Y_%m_%d_time_%H_%M_%S")
        filename = f"../test_clouds/cloud_{timestamp}.pcd"
        print(f"File '{filename}' created successfully.")
        return filename
    
    def write_pcd_header_to_file(self, filename, pts_count):
        header = [
            "VERSION .7\n",
            "FIELDS x y z rgb\n",
            "SIZE 4 4 4 4\n",
            "TYPE F F F F\n",
            "COUNT 1 1 1 1\n",
            f"WIDTH {pts_count}\n",
            "HEIGHT 1\n",
            "VIEWPOINT 0 0 0 1 0 0 0\n",
            f"POINTS {pts_count}\n",
            "DATA ascii\n"
        ]
        with open(filename, "a") as file:
            file.writelines(header)
    
    def write_pts_to_file(self, filename, pts):
        with open(filename, "a") as file:
            for pt in pts:
                file.write("%s %s %s %s\n" % (pt[0], pt[1], pt[2], pt[3]))
                
if __name__ == "__main__":
    # Simple test routine (for debugging only).
    L = Lidar()
    L.open_serial()
    pkts = L.get_packets(10)
    for p in pkts:
        L.process_packet(p, show=True)
    L.close_serial()

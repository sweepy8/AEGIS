'''
LiDAR driver for AEGIS senior design.
Compatible with STL27L LiDAR sensor.
'''

import numpy
import serial
import time
import matplotlib.animation as animation	# Used in visualizer
import matplotlib.pyplot as plt				# Used in visualizer
import datetime # for timestamped data files

PRINT_NO_VIS = 0	# 1 for data print, 0 for 2D visualizer

class Lidar:
    
    CRCTABLE = [
        0x00, 0x4d, 0x9a, 0xd7, 0x79, 0x34, 0xe3, 0xae, 0xf2, 0xbf,
        0x68, 0x25, 0x8b, 0xc6, 0x11, 0x5c, 0xa9, 0xe4, 0x33, 0x7e,
        0xd0, 0x9d, 0x4a, 0x07, 0x5b, 0x16, 0xc1, 0x8c, 0x22, 0x6f,
        0xb8, 0xf5, 0x1f, 0x52, 0x85, 0xc8, 0x66, 0x2b, 0xfc, 0xb1,
        0xed, 0xa0, 0x77, 0x3a, 0x94, 0xd9, 0x0e, 0x43, 0xb6, 0xfb,
        0x2c, 0x61, 0xcf, 0x82, 0x55, 0x18, 0x44, 0x09, 0xde, 0x93,
        0x3d, 0x70, 0xa7, 0xea, 0x3e, 0x73, 0xa4, 0xe9, 0x47, 0x0a,
        0xdd, 0x90, 0xcc, 0x81, 0x56, 0x1b, 0xb5, 0xf8, 0x2f, 0x62,
        0x97, 0xda, 0x0d, 0x40, 0xee, 0xa3, 0x74, 0x39, 0x65, 0x28,
        0xff, 0xb2, 0x1c, 0x51, 0x86, 0xcb, 0x21, 0x6c, 0xbb, 0xf6,
        0x58, 0x15, 0xc2, 0x8f, 0xd3, 0x9e, 0x49, 0x04, 0xaa, 0xe7,
        0x30, 0x7d, 0x88, 0xc5, 0x12, 0x5f, 0xf1, 0xbc, 0x6b, 0x26,
        0x7a, 0x37, 0xe0, 0xad, 0x03, 0x4e, 0x99, 0xd4, 0x7c, 0x31,
        0xe6, 0xab, 0x05, 0x48, 0x9f, 0xd2, 0x8e, 0xc3, 0x14, 0x59,
        0xf7, 0xba, 0x6d, 0x20, 0xd5, 0x98, 0x4f, 0x02, 0xac, 0xe1,
        0x36, 0x7b, 0x27, 0x6a, 0xbd, 0xf0, 0x5e, 0x13, 0xc4, 0x89,
        0x63, 0x2e, 0xf9, 0xb4, 0x1a, 0x57, 0x80, 0xcd, 0x91, 0xdc,
        0x0b, 0x46, 0xe8, 0xa5, 0x72, 0x3f, 0xca, 0x87, 0x50, 0x1d,
        0xb3, 0xfe, 0x29, 0x64, 0x38, 0x75, 0xa2, 0xef, 0x41, 0x0c,
        0xdb, 0x96, 0x42, 0x0f, 0xd8, 0x95, 0x3b, 0x76, 0xa1, 0xec,
        0xb0, 0xfd, 0x2a, 0x67, 0xc9, 0x84, 0x53, 0x1e, 0xeb, 0xa6,
        0x71, 0x3c, 0x92, 0xdf, 0x08, 0x45, 0x19, 0x54, 0x83, 0xce,
        0x60, 0x2d, 0xfa, 0xb7, 0x5d, 0x10, 0xc7, 0x8a, 0x24, 0x69,
        0xbe, 0xf3, 0xaf, 0xe2, 0x35, 0x78, 0xd6, 0x9b, 0x4c, 0x01,
        0xf4, 0xb9, 0x6e, 0x23, 0x8d, 0xc0, 0x17, 0x5a, 0x06, 0x4b,
        0x9c, 0xd1, 0x7f, 0x32, 0xe5, 0xa8
    ]
    
    
    def __init__(self):
        '''
        Initializes a lidar object with UART parameters and application-specific parameters
        @param None
        @return: None
        '''
        
        self.name        = 'STL27L'
        self.max_packets = 245				# (921600b/s) / (10Hz) / (8b/B) / (47 B/p)
        self.packet_size = 47				# One packet contains 47 bytes
        self.start_byte  = 0x54				# Each packet begins with 0x54
        self.hit_rate_threshold = 0.95		# Allows rings with a % of max_packets above the threshold
        
        self.serial_conn = serial.Serial()	# Create (but do not open) a serial connection
        
        self.port_name   = '/dev/ttyAMA0'	# UART port on GPIO 14 and 15 (check this? could be wrong)
        self.baudrate    = 921600			# STL27L Baud
        self.byte_size   = 8				# 8 bits per byte
        self.parity_bits = 'N'				# No parity bit
        self.stop_bits   = 1				# One stop bit per byte
        self.timeout     = 0				# Non-blocking mode (return immediately)
        
    

    def open_serial(self):
        '''
        Opens a serial connection using UART parameters defined in initializer
        @param None
        @return: None
        '''        
        # Configure serial connection parameters
        self.serial_conn.port     = self.port_name
        self.serial_conn.baudrate = self.baudrate
        self.serial_conn.bytesize = self.byte_size
        self.serial_conn.parity   = self.parity_bits
        self.serial_conn.stopbits = self.stop_bits
        self.serial_conn.timeout  = self.timeout
        
        # Open configured serial connection
        self.serial_conn.open()
        
        # Allow connection to form
        time.sleep(0.05)
    

    def close_serial(self):
        '''
        Closes the serial connection if it is open
        @param None
        @return None
        '''
        if self.serial_conn.is_open:
            self.serial_conn.close()
        
    
    def get_packets(self, packets, show=0, no_vis=0):
        '''
        Obtains data packets from the LiDAR device over the serial connection.
        @param  
            packets: Number of packets to retrieve
            show: A flag value to either print (1) or hide (0) detailed information to the console
            no_vis: A flag value specifying whether (0) or not (1) a visualizer is being used
        @return
            data_arr: Array containing packet arrays
        '''
        data_arr = []

        for p in range(0, packets):
            
            data = self.serial_conn.read(self.packet_size)
            
            if show:
                print("\n#%3.3d (L=%2.2d): " %(p, len(data)), end=' ')
                for byte in data: print("%2x" % byte, end=' ')
            
            # If the packet is not 47 bytes long, reject it
            if (len(data) != self.packet_size):
                if show: print("Incorrect Packet Size! N =", len(data), end='')
                packets += 1
                continue
            
            # If the packet does not begin with the start byte, reject it
            if (data[0] != self.start_byte):
                if show: print("Misaligned Packet!", end='')
                self.serial_conn.read_until(str(self.start_byte))
                packets += 1
                continue
            
            # If the packet has an invalid CRC checksum, reject it
            if (data[self.packet_size-1] != self.calc_crc8(data)):
                if show: print("Incorrect Checksum!", end='')
                self.serial_conn.read_until(str(self.start_byte))
                packets += 1
                continue
            
            data_arr.append(data)

            if no_vis:
                time.sleep(0.004)	#Allow time to scan. Visualizer offers enough delay
            
        return data_arr 

    def process_packet(self, p, show=0, motor_angle=None):
        '''
        Extracts information from packet data in accordance with STL27L communication protocol
        @param  
            p: packet to process as an array of bytes 
            show: A flag value to either print (1) or hide (0) detailed information to the console
            motor_angle: Current angle of motor used to describe a point in spherical coordinates
        @return
            pts_arr: Array containing points as either 3 or 4 element float arrays
        '''
        
        # data comes in as LSB then MSB
        speed       = p[3]  * (2**8) + p[2]		# speed of rotation in degrees per second
        start_angle = p[5]  * (2**8) + p[4]		# start angle in units of 0.01 degrees
        end_angle   = p[43] * (2**8) + p[42]	# end angle in units of 0.01 degrees
        timestamp   = p[45] * (2**8) + p[44]	# units of ms, rollover at 30000
        
        # If we've rolled over from 360 degrees to 0, add 1 revolution to correct delta
        if end_angle < start_angle:
            angle_delta = numpy.abs(end_angle - start_angle + 36000) / (12-1)
        else:
            angle_delta = numpy.abs(end_angle - start_angle) / (12-1)
        
        # Construct points array (12 points per packet)
        pts_arr = []
        for i in range(0,12):
            pt_dist  = ( p[7 + 3*i] * (2**8) + p[6 + 3*i] ) / 1000	# distance in mm, converted to meters
            pt_angle = ( start_angle + angle_delta * i ) / 100		# angle in 0.01 deg, converted to deg
            pt_intensity = p[8 + 3*i]								# reflection intensity
            
            # Enable 2D for tests without motor. ("is" not None delineates between 0 and None type)
            if motor_angle is not None: pts_arr.append([pt_dist, pt_angle, motor_angle, pt_intensity])
            else:						pts_arr.append([pt_dist, pt_angle, pt_intensity])
                
        if show:
            print("\nPacket Info: SB=%2.2x|VL=%2.2x|SP=%d|ST_A=%d|E_A=%d|TIME=%d"
                  % (p[0], p[1], speed, start_angle, end_angle, timestamp), end='')
    
        return pts_arr
    
    def get_processed_ring(self, show=0, no_vis=1, motor_angle=None):
        '''
        Obtains a ring's worth of data from the LiDAR device over the serial connection.
        @param  
            show: A flag value to either print (1) or hide (0) detailed information to the console
            no_vis: A flag value specifying whether (0) or not (1) a visualizer is being used
            motor_angle: Current angle of motor used to describe a point in spherical coordinates
        @return 
            pts: Array containing points as either 3 or 4 element float arrays
        '''

        pts = []
        
        while (len(pts) / 12 < self.max_packets * self.hit_rate_threshold):
        
            pts = []
            if show: print(f"Requesting {self.max_packets * 12} points...", end=' ')
            packets = self.get_packets(self.max_packets, show, no_vis)
            for p in packets:
                pts_in_packet = self.process_packet(p, show, motor_angle)
                for pt in pts_in_packet:
                    pts.append(pt)
                
        if show: print(f"Recieved {len(pts)} points...")
        
        return pts
    
    def calc_crc8(self, packet):
        '''
        Calculates the CRC8 checksum in accordance with the STL27L communications protocol.
        @param 
            packet: Packet to be verified (as an array of bytes)
        @return
            crc: The correct integer checksum of the packet
        '''

        crc = 0
        for i in range(0, self.packet_size - 1):
            crc = self.CRCTABLE[(crc ^ packet[i]) & 0xff]
        return crc
    

    def conv_pts_coords(self, pts):
        '''
        Converts an array of two-dimensional points from polar to cartesian coordinates.
        @param 
            pts: Array containing polar points
        @return
            cart_pts: Array containing cartesian points
        '''    
        cart_pts = []
        
        for pt in pts:
            cart_pt = pol_to_cart(pt[0], pt[1])
            cart_pt.append(0)
            cart_pts.append(cart_pt)
            
        return cart_pts

    def make_file(self):
        '''
        ****************************************************.
        @param  pts: Array containing polar points
        @return cart_pts: Array containing cartesian points
        '''
        timestamp = datetime.datetime.now().strftime("%Y_%m_%d_time_%H_%M_%S")
        filename = f"cloud_{timestamp}.pcd"
        print(f"File '{filename}' created successfully.")
        return filename
    
    

    def write_pcd_header_to_file(self, filename, pts_count):
        '''
        ***********************************************.
        '''    
        header = ["VERSION .7\n",
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
        '''
        *******************************.
        '''
        with open(filename, "a") as file:
            for pt in pts:
                file.write("%s %s %s %s\n" % (pt[0], pt[1], pt[2], pt[3]))


# GLOBAL FUNCTIONS (MOVE TO SEPARATE FILE) -----------------------------------------------------------------

def pol_to_cart(rho, phi):		# Takes radius and angle (IN DEG) and converts coordinate system of a point
    '''
    **************************.
    '''
    x = rho * numpy.cos(numpy.deg2rad(phi))
    y = rho * numpy.sin(numpy.deg2rad(phi))
    return [round(x, 8), round(y, 8)]


def print_pts_test():
    '''
    ***************************.
    '''
    print("Instantiating LiDAR object...", end='')
    L1 = Lidar()
    print(" Done!\nOpening serial connection...", end='')
    L1.open_serial()
    print("  Done!")
    
    start_time = time.time()
    
    pts = L1.get_processed_ring(no_vis=1)
        
    end_time = time.time()
    
    print(f"Point capture took {round(end_time - start_time, 4)} seconds...") 
    print("Data processed! Num pts: %d" % len(pts))
    c_pts = L1.conv_pts_coords(pts)
    print("Points converted to Cartesian coordinates!")
    print(c_pts)
    #print("Writing points to text file...", end='')
    #L1.write_pts_to_file("testpcd.txt", c_pts)
    #print(" Done!")


def visualize_pts_test():
    '''
    *********************************.
    '''
    
    def init():
        scat.set_offsets(numpy.empty(2))
        return scat,
    
    def get_new_data(L1):
        pts = []
        for p in L1.get_packets(L1.max_packets):
            for pt in L1.process_packet(p):
                pts.append(pt)
            
        return L1.conv_pts_coords(pts)
    
    def update(frame, L1):
        scat.set_offsets(get_new_data(L1))
        return scat,
    
    print("Instantiating LiDAR object...", end='')
    L1 = Lidar()
    print(" Done!\nOpening serial connection...", end='')
    L1.open_serial()         
    print(" Done!\nLaunching visualization...")
    
    # This block sets up the visualization plot (and sets black on white color scheme)
    fig, ax = plt.subplots(figsize=(8, 6))
    scat = ax.scatter([],[], s=1, c='w')
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    for spine in ax.spines.values(): spine.set_edgecolor('white')
    ax.set_xlim(-8, 5)		# Experimental values
    ax.set_ylim(-5, 12)		# Experimental values
    ax.set_title("Live LiDAR Data Visualization", color='w')
    ax.set_xlabel("X", color='white')
    ax.set_ylabel("Y", color='white')
    ax.tick_params(colors='w', which='both')

    # Declares the custom animation. Matplotlib is awesome
    anim = animation.FuncAnimation(fig, update, fargs=(L1,), init_func=init, blit=True, interval=L1.max_packets / 4.9)

    # Show em what you got
    plt.show()
    

def main():
    
    if PRINT_NO_VIS: print_pts_test()
    else: 			 visualize_pts_test()


if __name__ == "__main__":
    main()
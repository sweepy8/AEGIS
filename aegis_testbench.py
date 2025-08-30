# Relative importing is a nightmare, and it is my principle frustration with 
# Python as a language. I didn't want to join parent folders to the sys path for
# each file. Import submodules and test them here.

'''MOTOR TEST'''
# from lidar import motor
# motor.test_motor()


'''LIDAR TEST'''
# from lidar import lidar

# print("\nTESTING 1 RING (VERBOSE, SAVES FILE)\n")
# lidar.test_ring_capture(save=True, verbose=True)

# print("\nTESTING 100 RINGS:\n")
# avg_duration_s: float = 0
# for x in range(0, 100):
#     duration_s, pts = lidar.test_ring_capture(save=False, verbose=False)
#     print(f"Duration: %.4f, Points: %4d" % (duration_s, pts))
#     avg_duration_s += duration_s

# avg_duration_s /= 100
# print(f"Average duration: {round(avg_duration_s, 4)} seconds.")


'''SCANNER TEST'''
from lidar import scan

print("\nTESTING 3D SCANNER (SAVES FILE)")
test_scanner = scan.Scanner()
test_scanner.scan()


'''COORDINATE TRANSFORM TEST'''
# from utils import math_utils

# # rho, phi, theta == dist, l_angle, m_angle
# sph_pt = [1, 0, 0, 100]

# cart_pt = math_utils.sph_to_cart(*sph_pt)

# print(cart_pt)


'''ADD:
    Camera Test

'''
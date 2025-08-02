# Relative importing is a nightmare, and my principle frustration with Python as
# a language. Import submodules and test them here.

'''MOTOR TEST'''
# from lidar import new_motor
# new_motor.main()

'''LIDAR TEST'''
# from lidar import new_lidar

# print("\nTESTING 1 RING (VERBOSE, SAVES FILE)\n")
# new_lidar.test_ring_capture(save=True, verbose=True)

# print("\nTESTING 100 RINGS:\n")
# for x in range(0, 100):
#     duration_s, pts = new_lidar.test_ring_capture(save=False, verbose=False)
#     print(f"Duration: %.4f, Points: %4d" % (duration_s, pts))

'''SCANNER TEST'''
from lidar import new_scan

print("/nTESTING 3D SCANNER (SAVES FILE)")
new_scan.test_scan(save=True, verbose=False)
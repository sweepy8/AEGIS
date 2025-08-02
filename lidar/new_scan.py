'''
3D LiDAR scanner driver for AEGIS senior design. Version 2
Compatible with STL27L LiDAR scanner, A4988 motor driver, and NEMA17 stepper 
motor.

TODO:
    FIX OPENING SERIAL PORT EACH TIME IN TAKE_SCAN FUNCTION !!! 
        This could reduce scan time by a factor of 3

    Experiment with different stepper motor speeds during scan. 
        Too much kickback at high speeds?

    set_rings_per_cloud --> set_resolution(res: float)? 
        It would involve rounding error but give user a different kind of 
        control over scan resolution. Maybe both?
'''

import time                     # time()

from new_lidar import Lidar
from new_motor import Motor
from utils import file_utils    # get_timestamped_filename()
from utils import math_utils    # sph_to_cart_array()


class Scanner():
    """
    The AEGIS 3D LiDAR scanner class.
    
    This class combines the STL27L LiDAR scanner and NEMA17 stepper motor as a 
    single 360 degree, 3D scanner with configurable scan resolution. It 
    provides methods that configure the resolution of scans, and take, print, 
    and save scans.

    Attributes:
        lidar (Lidar): An object of the Lidar class which enables STL27L sensor
            functionality.
        motor (Motor): An object of the Motor class which enables stepper motor
            functionality.
        rings_per_cloud (int): The number of rings per point cloud.
        steps_per_ring (int): The number of steps taken by the stepper motor
            after capturing each ring.
        resolution (float): The angular resolution of scans on the XY plane
            (i.e. the angular distance between rings).
    """

    def __init__(self) -> None:
        """
        """
        self.lidar: Lidar = Lidar()
        self.motor: Motor = Motor(res_name="sixteenth", start_angle=0, speed=1)
        self.rings_per_cloud: int = 200
        self.steps_per_ring: int = int(100 * self.motor.ms_res_denom / self.rings_per_cloud)
        self.resolution: float = 180 / self.rings_per_cloud
    
    def set_rings_per_cloud(self, num_rings: int) -> None:
        '''
        
        Note that values not divisible by 100 or values which call for 
        one-step-at-a-time motion below full resolution have not been tested.
        The actual vs. expected motor.curr_angle error might be too large to get
        good scans when turning less than 4 or 8 steps per ring at sixteenth-step 
        resolution, for example.
        '''

        if (num_rings > self.motor.ms_res_denom * 100):
            raise ValueError(f"Resolution is too high!",
                "Must not exceed (steps/rev) / 2 at currently configured",
                "microstep resolution. ({resolution}, {self.motor.ms_res})")
        
        self.rings_per_cloud = num_rings
        self.steps_per_ring: int = int(100 * self.motor.ms_res_denom / self.rings_per_cloud)
        self.resolution: float = 180 / self.rings_per_cloud

    def capture_cloud(self) -> tuple[list[list[float]], int, float]:
        """
        Takes a 3D scan of the environment.

        Returns:
            cloud (list[list[float]]): A 3D point cloud array.
            num_points (int): The number of points in the cloud.
            duration_s (float): The time in seconds it took to complete the scan.
        """

        start_time_s: float = time.time()

        self.motor.set_dir("CW")

        cloud: list[list[float]] = []

        while self.motor.curr_angle < 180:
            self.lidar.open_serial()    # See cylindrical distortion error in documentation

            ring: list[list[float]] = self.lidar.capture_ring(motor_angle=self.motor.curr_angle)
            cloud.extend(ring)

            self.motor.turn(self.steps_per_ring)

            self.lidar.close_serial()

        self.motor.set_dir("CCW")
        self.motor.turn(self.motor.ms_res_denom * 100)

        num_points: int = len(cloud)

        duration_s: float = time.time() - start_time_s

        return cloud, num_points, duration_s

    def print_scan(self, cloud: list[list[float]], cartesian: bool = True) -> None:
        """
            Should this even exist?
        """

        for index, point in enumerate(math_utils.sph_to_cart_array(cloud) if cartesian else cloud):
            print(f"\t{index}: " + f"{' '.join([str(val) for val in point])}\n")

    def save_scan(self, cloud: list[list[float]], cartesian: bool = True, filename: str | None = None) -> str:
        """
        
        """

        if filename is None:
            filename = file_utils.get_timestamped_filename(
                save_path='.', prefix='cloud', ext='.txt')
        
        file_utils.write_points_to_file(
            filename = filename,
            points = math_utils.sph_to_cart_array(cloud) if cartesian else cloud
        )

        return filename


def test_scan(save: bool, verbose: bool) -> None:
    test_scanner = Scanner()
    test_scanner.set_rings_per_cloud(200)

    test_cloud, num_points, scan_time_s = test_scanner.capture_cloud()
    print(f"[RUNTIME] scan.py: Cloud captured in {scan_time_s} seconds ({num_points} points)!")

    if save:
        test_file: str = test_scanner.save_scan(test_cloud)
        print(f"[RUNTIME] scan.py: Cloud saved to {test_file}.")

    if verbose:
        print("[RUNTIME] scan.py: Printing cloud data...")
        test_scanner.print_scan(test_cloud)
        print("[RUNTIME] scan.py: Cloud data finished printing!")
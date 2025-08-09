'''
3D LiDAR scanner driver for AEGIS senior design. Version 2
Compatible with STL27L LiDAR scanner, A4988 motor driver, and NEMA17 stepper 
motor.
'''

import time                     # time()

from lidar import lidar
from lidar import motor
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
        self.lidar: lidar.Lidar = lidar.Lidar()
        self.motor: motor.Motor = motor.Motor(res_name="sixteenth", start_angle=0, speed=1)
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

    def capture_cloud(self) -> list[list[float]]:
        """
        Takes a 3D scan of the environment.

        Returns:
            cloud (list[list[float]]): A 3D point cloud array.
            num_points (int): The number of points in the cloud.
            duration_s (float): The time in seconds it took to complete the scan.
        """

        print("[RUNTIME] scan.py: Beginning cloud capture...")

        start_time_s: float = time.time()

        self.motor.set_dir("CW")

        cloud: list[list[float]] = []

        while self.motor.curr_angle < 180:
            self.lidar.open_serial()    # See cylindrical distortion error in documentation

            ring: list[list[float]] = self.lidar.capture_ring(motor_angle=self.motor.curr_angle)
            cloud.extend(ring)
            self.motor.turn("CW", self.steps_per_ring)

            self.lidar.close_serial()

        self.motor.set_dir("CCW")
        self.motor.turn("CCW", self.motor.ms_res_denom * 100)

        num_points: int = len(cloud)

        duration_s: float = time.time() - start_time_s
        duration_s = round(duration_s, 2)

        print(f"[RUNTIME] scan.py: Cloud captured in {duration_s} seconds ({num_points} points).")

        return cloud

    def print_scan(self, cloud: list[list[float]], cartesian: bool = True) -> None:
        """
            Should this even exist? Probably not.
        """

        print("[RUNTIME] scan.py: Printing cloud data...")

        for index, point in enumerate(math_utils.sph_to_cart_array(cloud) if cartesian else cloud):
            print(f"\t{index}: " + f"{' '.join([str(val) for val in point])}\n")

        print("[RUNTIME] scan.py: Cloud data finished printing!")

    def save_scan(self, cloud: list[list[float]], cartesian: bool = True, filename: str | None = None) -> str:
        """
        
        """

        if filename is None:
            filename = file_utils.get_timestamped_filename(
                save_path='.', prefix='cloud', ext='.txt')
            
        print(f"[RUNTIME] scan.py: Saving cloud to {filename}...")
        
        file_utils.write_points_to_file(
            filename = filename,
            points = math_utils.sph_to_cart_array(cloud) if cartesian else cloud
        )

        print(f"[RUNTIME] scan.py: Cloud saved to {filename}.")

        return filename


def test_scan(save: bool, verbose: bool) -> None:
    test_scanner = Scanner()
    test_scanner.set_rings_per_cloud(num_rings=200)

    test_cloud: list[list[float]] = test_scanner.capture_cloud()

    if save:
        test_file: str = test_scanner.save_scan(cloud=test_cloud)

    if verbose:
        test_scanner.print_scan(cloud=test_cloud)
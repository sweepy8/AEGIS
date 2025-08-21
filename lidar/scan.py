'''
3D LiDAR scanner driver for AEGIS senior design. Version 2
Compatible with STL27L LiDAR scanner, A4988 motor driver, and NEMA17 stepper 
motor.
'''

import time                     # time()
import random                   # seed(), sample()

from lidar import lidar
from lidar import motor
from utils import file_utils    # get_timestamped_filename()
from utils import math_utils    # sph_to_cart_array()


class Scanner():
    """
    The AEGIS 3D LiDAR scanner class.
    
    This class combines the STL27L LiDAR scanner and NEMA17 stepper motor as a 
    single 360 degree, 3D scanner with configurable angular resolution. It 
    provides methods that configure the resolution of, capture, print, and save 
    point cloud scans.

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
        Initializes a scanner object by combining an instance of the Lidar class
        and an instance of the Motor class. Configures the number of rings per
        cloud (400 by default) and related values.
        """
        self.lidar: lidar.Lidar = lidar.Lidar()
        self.motor: motor.Motor = motor.Motor(res_name="sixteenth", start_angle=0, speed=1)
        self.rings_per_cloud: int = 400
        self.steps_per_ring: int = int(100 * self.motor.ms_res_denom / self.rings_per_cloud)
        self.resolution: float = 180 / self.rings_per_cloud
    
    def set_rings_per_cloud(self, num_rings: int) -> None:
        '''
        Configures the angular resolution of the scanner by adjusting the number
        of rings taken per scan.
        
        Args:
            num_rings (int): The number of rings per scan. 180 degrees divided
                by this value gives the angular distance between rings.
        Raises:
            ValueError: If the selected resolution is too high for the currently
                selected stepper motor microstep resolution.
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
        Takes a 3D scan of the environment. This function is the powerhouse of 
        the cell.\n
        Performs the following steps:
            1. Sets direction of stepper motor to counterclockwise.
            2. Captures a ring's worth of points, extends a cloud array with the 
               points, and turns the motor a specified amount.
            3. Repeats step 2 until the motor angle is at least 180 degrees.
            4. Reverses direction of stepper motor and resets to starting 
               position.
            5. Prints information about size and duration of scan.
            6. Returns the captured cloud.

        Returns:
            cloud (list[list[float]]): A 3D point cloud array.
        """

        print("[RUNTIME] scan.py: Beginning cloud capture...")

        start_time_s: float = time.time()

        self.motor.set_dir("CCW")

        cloud: list[list[float]] = []

        while self.motor.curr_angle < 180:
            self.lidar.open_serial()    # See cylindrical distortion error in documentation

            ring: list[list[float]] = self.lidar.capture_ring(motor_angle=self.motor.curr_angle)
            cloud.extend(ring)
            self.motor.turn("CCW", self.steps_per_ring)

            self.lidar.close_serial()

        self.motor.set_dir("CW")
        self.motor.turn("CW", self.motor.ms_res_denom * 100)

        num_points: int = len(cloud)

        duration_s: float = time.time() - start_time_s
        duration_s = round(duration_s, 2)

        print(f"[RUNTIME] scan.py: Cloud captured in {duration_s} seconds ({num_points} points).")

        return cloud

    def print_scan(self, cloud: list[list[float]], cartesian: bool = True) -> None:
        """
            Should this even exist? Probably not. Don't use this.
        """

        print("[RUNTIME] scan.py: Printing cloud data...")

        for index, point in enumerate(math_utils.sph_to_cart_array(cloud) if cartesian else cloud):
            print(f"\t{index}: " + f"{' '.join([str(val) for val in point])}\n")

        print("[RUNTIME] scan.py: Cloud data finished printing!")

    def trim_scan(self, cloud: list[list[float]], nonfat_pct: float = 0.2) -> list[list[float]]:
        '''
        Downsamples a cloud to reduce resolution, file size, and load times.

        Args:
            cloud (list[list[float]]): A cloud of points to be trimmed.
            nonfat_pct (float): A percentage of points to retain (non-fat).
        Returns:
            out (list[list[float]]): The trimmed point cloud.
        '''
        random.seed()

        num_pts_untrimmed = len(cloud)
        num_pts_trimmed = int(num_pts_untrimmed * nonfat_pct)
        nonfat_cloud: list[list[float]] = random.sample(cloud, num_pts_trimmed)

        print(f"[RUNTIME] UART.py: Cloud trimmed to {nonfat_pct * 100}%, "
              f"removed {num_pts_untrimmed - num_pts_untrimmed} points.")
        
        return nonfat_cloud

    def save_scan(self,  
                  cloud: list[list[float]], 
                  cartesian: bool = True, 
                  filepath: str = '.') -> str:
        """
        Saves the cloud to a timestamped text file. Converts the points from 
        spherical (rho, theta, phi) representation to cartesian (x, y, z) 
        representation by default, but can be disabled to reduce scan time.

        Args:
            cloud (list[list[float]]): A cloud of points to be saved.
            cartesian (bool): Whether or not to perform coordinate transform.
                Defaults to True.
            filepath (str | None): Where to save the file. Defaults to the 
                current directory ('.').

        Returns:
            filename (str): The name and path of the saved .txt file. For
                example, './path/to/cloud_19690420_080085.txt'.
        """

        filename = file_utils.get_timestamped_filename(
            save_path=filepath,
            prefix='cloud', ext='.txt')
            
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
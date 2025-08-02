# Math Utilities
# Created on 6/26/2025

import numpy as np      # deg2rad(), cos(), sin()

SENSOR_OFFSET_MM = 80   # Any offset away from the motor shaft will skew scans. Measure this distance with calipers.

def pol_to_cart(rho: float, phi: float, intensity: float | None = None) -> list[float]:
    '''
    Converts coordinates of a point from polar to cartesian system.

    Args:
        rho (float): The radial distance from the origin.
        phi (float): The angular distance from zero degrees.
    Returns:
        The converted point.
    '''
    x = rho * np.cos(np.deg2rad(phi))
    y = rho * np.sin(np.deg2rad(phi))

    return [x, y, intensity] if intensity is not None else [x, y]


def pol_to_cart_array(points: list[list[float]]) -> list[list[float]]:
    '''
    Converts an array of polar (rho, theta) points to the cartesian (x, y) system.

    Args:
        points (list[list[float]]): A list of polar points to be converted.
    Returns:
        cartesian_points (list[list[float]]): A list of converted cartesian points.
    '''
    
    cartesian_points: list[list[float]] = [pol_to_cart(*point) for point in points]

    return cartesian_points


def sph_to_cart(rho: float, phi: float, theta: float, intensity: float | None = None) -> list[float]:
    """
    
    """

    dist: float = rho								    # radial distance rho in meters
    l_angle: float = np.deg2rad(phi)				    # lidar angle phi in radians
    m_angle: float = np.deg2rad(theta)				    # motor angle theta in radians
    
    x: float = dist*np.sin(l_angle)*np.cos(m_angle)	    # x = r*sin(phi)*cos(theta)
    y: float = dist*np.sin(l_angle)*np.sin(m_angle)	    # y = r*sin(phi)*sin(theta)
    z: float = dist*np.cos(l_angle)					    # z = r*cos(phi)
    
    x += SENSOR_OFFSET_MM*np.sin(m_angle)		# Correct for horizontal lidar offset
    y += SENSOR_OFFSET_MM*np.cos(m_angle)		# Correct for horizontal lidar offset

    return [x, y, z, intensity] if intensity is not None else [x, y, z]
    

def sph_to_cart_array(points: list[list[float]]) -> list[list[float]]:
    """
    
    """
    
    cartesian_points: list[list[float]] = [sph_to_cart(*point) for point in points]
        
    return cartesian_points
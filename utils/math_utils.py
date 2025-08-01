# Math Utilities
# Created on 6/26/2025

import numpy as np      # deg2rad(), cos(), sin()

def pol_to_cart(rho: float, phi: float) -> list[float]:
    '''
    Converts coordinates of a point from polar to cartesian system.

    Args:
        rho: A float representing the radial distance from the origin.
        phi: A float representing the angular distance from zero degrees.
    '''
    x = rho * np.cos(np.deg2rad(phi))
    y = rho * np.sin(np.deg2rad(phi))
    return [x, y]

def pol_to_cart_array(points: list[list[float]]) -> list[list[float]]:
    '''
    Converts an array of polar points to a cartesian coordinate system.
    Args:
        points: A list of points to be converted.
    Returns:
        A list of converted points.
    '''
    return [pol_to_cart(rho=point[0], phi=point[1]) for point in points]


# This file should include 3d conversion as well
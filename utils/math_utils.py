# Math Utilities
# Created on 6/26/2025

from numpy import cos, sin, deg2rad

def pol_to_cart(rho: float, phi: float, mantissa: int) -> list[float]:
    '''
    Converts coordunates of a point from polar to cartesian system.
    Takes radius rho and angle phi in degrees, and mantissa size for rounding.
    '''
    x = rho * cos(deg2rad(phi))
    y = rho * sin(deg2rad(phi))
    return [round(x, mantissa), round(y, mantissa)]


# This file should include 3d conversion as well
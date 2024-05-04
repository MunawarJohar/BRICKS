import numpy as np
from .utils import hwall_length

def max_relative_displacement(wallz, coords):
    n = len(coords)
    max_disp = 0
    for i in range(n):
        for j in range(i+1, n):
            x1, y1 = coords[i], wallz[i]
            x2, y2 = coords[j], wallz[j]
            if x2 != x1:  # Avoid division by zero
                m = (y2 - y1) / (x2 - x1)
                b = y1 - m * x1
                for k in range(min(i,j), max(i,j)+1):
                    xk, yk = coords[k], wallz[k]
                    line_y = m * xk + b
                    disp = abs(line_y - yk)
                    if disp > max_disp:
                        max_disp = disp

    return max_disp

def calculate_phi(wallz, coords):
    ind_min = np.argmin(wallz)
    wmin = wallz[ind_min]
    adjacent_indices = [ind_min - 1, ind_min + 1]
    adjacent_indices = [i for i in adjacent_indices if 0 <= i < len(wallz)]
    adjacent_values = wallz[adjacent_indices]
    x_adjacent = coords[np.isin(wallz, adjacent_values)]
    if len(x_adjacent) == 2:
        x_close = x_adjacent[np.argmax(np.abs(adjacent_values - wmin))]
        phi = np.arctan((wmin - max(adjacent_values)) / (np.abs(x_close - coords[ind_min]) * 1000))
    elif len(x_adjacent) == 1:
        phi = np.arctan((wmin - adjacent_values[0]) / (np.abs(x_adjacent[0] - coords[ind_min]) * 1000))
    else:
        phi = None
    return phi


def calculate_omega(wallz, x_coords):
    inflection_indices = np.where(np.diff(np.sign(np.diff(wallz))) != 0)[0] + 1
    if len(inflection_indices) < 2:
        omega = np.arctan(np.abs(np.diff(wallz)[0]) / ((x_coords[-1] - x_coords[0])*1000))
    else:
        distances = np.diff(inflection_indices)
        longest_period_index = np.argmax(distances)
        x_inflection = x_coords[inflection_indices]
        omega = np.arctan(np.abs(np.diff(wallz)[0]) / ((x_inflection[longest_period_index] - x_inflection[longest_period_index - 1])*1000))
    return omega


def compute_sri(house, wall_num, key):
    """
    Compute the Structural Reliability Index (SRI) for a given wall in a house.

    ## Parameters:
    - house (dict): A dictionary representing the house.
    - wall_num (int): The number of the wall to compute the SRI for.
    - key (str): The key to access the wall in the house dictionary.

    ## Returns:
    A dictionary containing the following SRI parameters:
    - 'Smax': The maximum absolute displacement of the wall.
    - 'dSmax': The difference between the minimum and maximum absolute displacements of the wall.
    - 'D/L': The ratio of dSmax to the length of the wall.
    - 'drat': The maximum relative displacement of the wall.
    - 'omega': The calculated omega parameter.
    - 'phi': The calculated phi parameter.
    - 'beta': The sum of phi and omega.

    """
    wall = house[key]
    wallz = wall['z'] - max(wall['z']) # Normalize displacements against each other  
    length = hwall_length(wall, wall_num+1) * 1000

    if (wall_num + 1) % 2 == 0:
        x = wall['x']
    else:
        x = wall['y']

    s_vmax = min(wallz) - max(wallz)
    d_deflection = max_relative_displacement(wallz, x)
    phi = calculate_phi(wallz, x)
    omega = calculate_omega(wallz, x)
    beta = abs(phi) + abs(omega)

    return {'Smax': abs(min(wall['z'])),
            'dSmax': abs(s_vmax),
            'D/L': abs(s_vmax)/length,
            'drat': abs(d_deflection),
            'omega': abs(omega),
            'phi': abs(phi),
            'beta': abs(beta)}

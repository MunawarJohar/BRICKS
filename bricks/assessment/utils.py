from numpy import array
from numpy import gradient
from numpy import exp
from scipy.interpolate import griddata

def interpolate_2d(x_boundary, y_boundary, z_boundary, x_values, y_values, method):
    Z_interpolation = griddata((x_boundary, y_boundary), z_boundary, (x_values, y_values), method=method)
    return Z_interpolation

def gaussian_shape(x, s_vmax, x_inflection):
    gauss_func = s_vmax * exp(-x**2/ (2*x_inflection**2))
    return gauss_func

def find_root_iterative(guess, parameters, tolerance, step):
    output = gaussian_shape(guess, parameters[0],parameters[1])
    while abs(output) > tolerance:
        guess += step 
        output = gaussian_shape(guess, *parameters)
    return guess

def get_range(wall, key):
    start = int(wall[key].min())*10
    stop = int(wall[key].max())*10

    if start == stop:
        if start != 100:
            stop += 1
        else:
            start -= 1
            stop += 1
            return [99]
    return list(range(start, stop))

def hwall_length(wall,i):
    if i % 2 == 0:  
        xi = wall['x'].min()
        xj = wall['x'].max()    
    else:  # Wall along x axis
        xi = wall['y'].min()
        xj = wall['y'].max()
    return xj - xi

# def sort_boundary(points):
# def unique_points(measurements):
#     seen = set()
#     unique = []
#     for point in points:
#         point_tuple = tuple(point)
#         if point_tuple not in seen:
#             seen.add(point_tuple)
#             unique.append(point)
#     return np.array(unique)

# def sort_vertices_clockwise(points):
#     centroid = points.mean(axis=0)
#     angles = np.arctan2(points[:, 1] - centroid[1], points[:, 0] - centroid[0])
#     return points[np.argsort(angles)]
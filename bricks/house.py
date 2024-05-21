import itertools
from collections import defaultdict

import numpy as np
from pandas import DataFrame
from scipy.interpolate import griddata
from scipy.optimize import curve_fit
from matplotlib.path import Path

from .assessment.utils import find_root_iterative, gaussian_shape, interpolate_2d 
from .assessment import compute_sri

class house:
    def __init__(self, measurements):
        """
        Initialize a House object with the given measurements.

        Parameters:
        measurements (dict): A dictionary containing the measurements of the house.

        Attributes:
        house (dict): The measurements of the house.
        soil (None): Placeholder for soil information.
        gaussian (None): Placeholder for Gaussian information.
        vertices (list): The vertices of the house walls.
        """ 
        self.house = measurements
        self.state = None
        self.process = {}
        self.soil = {}
        self.gaussian = {}
        self.assessment = {}
        
        self.vertices = self.process_vertices()
        self.dataframes = {}

    def interpolate(self, tolerance = 1e-1):
        """
        Interpolates the surface of the house using linear and cubic interpolation.

        This method creates a mesh grid based on the minimum and maximum x and y coordinates of the house walls.
        It then uses Delaunay triangulation to determine the points inside the convex hull of the house.
        The surface is interpolated using both linear and cubic interpolation methods.
        Values outside the convex hull are masked out.

        Returns:
            Assigns OBJECT.soil & OBJECT.process
        """
        x_boundary = np.concatenate([self.house[wall]["x"] for wall in self.house])
        y_boundary = np.concatenate([self.house[wall]["y"] for wall in self.house])
        z_boundary = np.concatenate([self.house[wall]["z"] for wall in self.house])

        x_min, x_max = np.min(x_boundary), np.max(x_boundary)
        y_min, y_max = np.min(y_boundary), np.max(y_boundary)

        definition = int(1/ tolerance*10) # Based on tolerance study on perimeter path in metres
        x_lin = np.linspace(x_min, x_max, definition)
        y_lin = np.linspace(y_min, y_max, definition)
        # -------------------------------- create mesh ------------------------------- #
        perimeter_path = Path(self.vertices['2D'])
        x_mesh, y_mesh = np.meshgrid(x_lin, y_lin)
        mesh_points = np.column_stack((x_mesh.ravel(), y_mesh.ravel()))

        inside_hull = perimeter_path.contains_points(mesh_points, radius=-tolerance)
        inside_hull = inside_hull.reshape(x_mesh.shape)
        # ---------------------------- Interpolate surface --------------------------- #
        z_lin = interpolate_2d(x_boundary, y_boundary, z_boundary, x_mesh, y_mesh, 'linear')
        z_qint = interpolate_2d(x_boundary, y_boundary, z_boundary, x_mesh, y_mesh, 'cubic')


        z_lin[~inside_hull] = np.nan
        z_qint[~inside_hull] = np.nan

        self.process['int'] = {}
        for wall in self.house:  #Store values on a per wall basis
            x_start, x_end = self.house[wall]['x'][0], self.house[wall]['x'][-1]
            y_start, y_end = self.house[wall]['y'][0], self.house[wall]['y'][-1]

            x_start_idx = np.argmin(np.abs(x_lin - x_start))
            x_end_idx = np.argmin(np.abs(x_lin - x_end)) + 1  
            y_start_idx = np.argmin(np.abs(y_lin - y_start))
            y_end_idx = np.argmin(np.abs(y_lin - y_end)) + 1

            if np.all(self.house[wall]['x'] == self.house[wall]['x'][0]):  # wall is along the y axis
                    z_lin_slice = z_lin[y_start_idx:y_end_idx, x_start_idx:x_end_idx].flatten()
                    z_qint_slice = z_qint[y_start_idx:y_end_idx, x_start_idx:x_end_idx].flatten()
                    ax = y_lin[y_start_idx:y_end_idx]
                    ax_rel = ax - y_lin[y_start_idx]   
                    self.process['int'][wall] = {'z_lin': z_lin_slice,
                                                    'z_q': z_qint_slice,
                                                    'ax': ax,
                                                    'ax_rel': ax_rel}
            else:  # wall is along the x axis
                z_lin_slice = z_lin[y_start_idx:y_end_idx, x_start_idx:x_end_idx].flatten()
                z_qint_slice = z_qint[y_start_idx:y_end_idx,x_start_idx:x_end_idx].flatten()
                ax = x_lin[x_start_idx:x_end_idx]
                ax_rel = ax - x_lin[x_start_idx]
                self.process['int'][wall] = {'z_lin': z_lin_slice,
                                                'z_q': z_qint_slice,
                                                'ax': ax,
                                                'ax_rel': ax_rel}

        self.soil = {'house': {'x': x_mesh,
                                'y': y_mesh,
                                'linear': z_lin,
                                'quadratic': z_qint}}

    def fit_function(self, i_guess, tolerance, step, function=gaussian_shape):
        """
        Fits Gaussian shapes to the data points of each wall in the house.

        Parameters:
        - i_guess (float): Initial guess for the root finding algorithm.
        - tolerance (float): Tolerance for the root finding algorithm.
        - step (float): Step size for the root finding algorithm.
        - function (function, optional): Function to fit the data points. Defaults to gaussian_shape.

        Returns:
        None
        """
        x_soil = []
        y_soil = []
        z_soil = []
        self.process["params"] = {}

        # ---------------------------- fit gaussian shapes --------------------------- #
        for i, wall in enumerate(self.house):
            x_data = self.process['int'][wall]["ax"]
            x_data_rel = self.process['int'][wall]["ax_rel"]
            y_data = self.process['int'][wall]["z_lin"]

            xmask = np.isnan(x_data)
            ymask = np.isnan(y_data)
            mask = xmask if sum(xmask) > sum(ymask) else ymask

            x_data = x_data[~mask]
            x_data_rel = x_data_rel[~mask]
            y_data = y_data[~mask]
            index = np.argmin(y_data)
                    
            if index == 0:
                y_normal = np.concatenate((y_data[index:][::-1], y_data[index:]))
                x_gauss = np.concatenate((-x_data_rel[index:][::-1], x_data_rel[index:]))
                x_data = np.concatenate((x_data[index] + (x_data[index] - x_data[index:]), x_data[index:]))
            else:
                y_normal = np.concatenate((y_data[:index + 1], y_data[:index][::-1]))
                x_gauss = np.concatenate((-x_data_rel[:index + 1][::-1], x_data_rel[:index]))
                x_data = np.concatenate((x_data[:index + 1], x_data[index] + x_data[:index + 1]))

            optimized_parameters, _ = curve_fit(f=gaussian_shape, xdata=x_gauss, ydata=y_normal)
            guess = find_root_iterative(i_guess, optimized_parameters, tolerance, step)

            x_gauss_2 = np.linspace(0, guess, 50)
            x_gauss = np.concatenate((-x_gauss_2[::-1], x_gauss_2))
            x_normal = np.concatenate((x_data[index] - x_gauss_2[::-1], x_data[index] + x_gauss_2))

            self.process['params'][wall] = params = {
                "s_vmax": optimized_parameters[0],
                "x_inflection": optimized_parameters[1],
                "x_gauss": x_gauss,
                "ax": x_normal
            }

            # ------------------------ interpolate gaussian shapes ----------------------- #
            wall = self.house[wall]
            xnormal = np.array(params['ax'])  # Ensure ax is a numpy array
            zi = gaussian_shape(params['x_gauss'], params['s_vmax'], params['x_inflection'])

            if i % 2 == 0:  # Wall is along the y axis
                y_soil.extend(np.linspace(xnormal.min(), xnormal.max(), 100).tolist())
                x_soil.extend(np.full(100, wall['x'].min()).tolist())
                z_soil.extend(zi)
            else:  # Wall is along the x axis
                x_soil.extend(np.linspace(xnormal.max(), xnormal.min(), 100).tolist())
                y_soil.extend(np.full(100, wall['y'].min()).tolist())
                z_soil.extend(zi)

        x, y, z = [np.array(x_soil), np.array(y_soil), np.array(z_soil)]
        X, Y = np.meshgrid(np.linspace(x.min(), x.max(), 100), np.linspace(y.min(), y.max(), 100))
        z_gaussian = griddata((x, y), z, (X, Y), method='cubic')
        self.soil['soil'] = {'x': X, 'y': Y, 'z': z_gaussian}
    
    def SRI(self):
        """
        Calculates the Settlement related intensity (SRI) values for each wall in the house.

        ## Returns:
            dict: The updated object with the SRI values stored in the `SRI` attribute.
        """
        self.soil['sri'] = {}
        self.soil['shape'] = {}

        for wall_num, key in enumerate(self.house):
            sri_data, infl_dict_ = compute_sri(self.house, wall_num, key)
            self.soil['sri'][key] = sri_data
            self.soil['shape'][key] = infl_dict_

    def process_dfs(self, curr_dic_list, names):
        """
        Turn list of dictionaries into their respective dataframes

        Args:
            curr_dic_list (list): List of dictionaries containing the data to be converted into dataframes
        """
        for i, curr_dic in enumerate(curr_dic_list):
            data_values = [list(inner_dict.values()) for inner_dict in curr_dic.values()]
            columns = list(curr_dic[next(iter(curr_dic))].keys())
            df = DataFrame(data_values, columns=columns)
            self.dataframes[names[i]] = df

    @staticmethod
    def arrange_vertices_contiguously(keys):
        """
        Arrange the vertices contiguously based on their coordinates. Only works for perpendicular cellular structures

        Args:
            keys (list): A list of keys representing the vertices.

        Returns:
            list: A list of keys representing the vertices arranged contiguously.
        """
        arranged_keys = []
        remaining_keys = keys[:]

        current_key = remaining_keys.pop(0)
        arranged_keys.append(current_key)
        
        while remaining_keys:
            last_key = arranged_keys[-1]
            next_key = None
            for key in remaining_keys:
                if key[0] == last_key[0]:
                    next_key = key
                    break 
            if next_key is None:
                for key in remaining_keys:
                    if key[1] == last_key[1]:
                        next_key = key
                        break
            if next_key:
                arranged_keys.append(next_key)
                remaining_keys.remove(next_key)
            else:
                next_key = remaining_keys.pop(0)
                arranged_keys.append(next_key)
        return arranged_keys

    def process_vertices(self):
        """
        Process the vertices of the house walls.

        ## Returns:
            dict: The updated object with the vertices stored in the `vertices` attribute.
        """
        vertices = [[self.house[wall]['x'].min() if x else self.house[wall]['x'].max(), 
                            self.house[wall]['y'].min() if y else self.house[wall]['y'].max(), 
                            z] 
                            for wall in self.house
                            for x, y, z in itertools.product([0,10], repeat=3)] + [[0,0,0]] # get all vertices of the walls
        vertices = list(set(tuple(vertex) for vertex in vertices))
        vertices = sorted(vertices, key=lambda x: (x[2], x[1], x[0]))
        grouped_vertices = defaultdict(list)
        for x, y, z in vertices:
            grouped_vertices[(x, y)].append((x, y, z))
        for key in grouped_vertices:
            grouped_vertices[key].sort(key=lambda v: v[2])

        sorted_keys = sorted(grouped_vertices.keys())
        arranged_keys = house.arrange_vertices_contiguously(sorted_keys) 

        return {'3D' :[vertex for key in arranged_keys for vertex in grouped_vertices[key]],
                                '2D' : [(key[0], key[1]) for key in arranged_keys] }

        

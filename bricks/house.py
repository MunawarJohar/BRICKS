import itertools

import numpy as np
from pandas import DataFrame
from scipy.interpolate import griddata
from scipy.optimize import curve_fit

from .utils import hwall_length, get_range, find_root_iterative, gaussian_shape, interpolate_2d 

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
        boundary (list): The boundary coordinates of the house.
        vertices (list): The vertices of the house walls.
        gshapes (None): Placeholder for gshapes information.
        dfltsm (None): Placeholder for dfltsm information.
        """ 
        self.house = measurements
        self.process = {}
        self.soil = {}
        self.gaussian = {}
        
        # --------------------------------- Geometry --------------------------------- #
        x_boundary = np.concatenate([self.house[wall]["x"] for wall in self.house])
        y_boundary = np.concatenate([self.house[wall]["y"] for wall in self.house])
        z_boundary = np.concatenate([self.house[wall]["z"] for wall in self.house])
        self.boundary = [x_boundary, y_boundary, z_boundary]
        vertices = [[self.house[wall]['x'].min() if x else self.house[wall]['x'].max(), 
                            self.house[wall]['y'].min() if y else self.house[wall]['y'].max(), 
                            z] 
                            for wall in self.house
                            for x, y, z in itertools.product([0,10], repeat=3)] + [[0,0,0]] # get all vertices of the walls
        vertices = list(set(tuple(vertex) for vertex in vertices))
        self.vertices = sorted(vertices, key=lambda x: (x[2], x[1], x[0]))
        
        # -------------------------------- Dataframes -------------------------------- #
        self.dataframes = {}

    def interpolate(self):
        """
        Interpolates the data points to create a mesh and perform interpolation.

        This method interpolates the data points of the house object to create a mesh and perform interpolation
        using linear and cubic interpolation methods. The interpolated values are then assigned to the respective
        walls of the house.

        Returns:
            None
        """
        for i, wall in enumerate(self.house):
            x_min = min(self.house[wall]["x"].min() for wall in self.house)
            x_max = max(self.house[wall]["x"].max() for wall in self.house)
            y_min = min(self.house[wall]["y"].min() for wall in self.house)
            y_max = max(self.house[wall]["y"].max() for wall in self.house)

        # -------------------------------- create mesh ------------------------------- #
        x_lin = np.linspace(x_min, x_max, 100)
        y_lin = np.linspace(y_min, y_max, 100)
        x_mesh, y_mesh = np.meshgrid(x_lin, y_lin)
        x_boundary, y_boundary, z_boundary = self.boundary
        # ------------------------------- Interpolation ------------------------------ #
        z_lin = interpolate_2d(x_boundary, y_boundary, z_boundary, x_mesh, y_mesh, 'linear')
        z_lin[int((36/70)*100):,int((89/108)*100):] = np.nan
        z_qint = interpolate_2d(x_boundary, y_boundary, z_boundary, x_mesh, y_mesh, 'cubic')
        z_qint[int((36/70)*100):,int((89/108)*100):] = np.nan
        # -------------------------- Repartition into walls -------------------------- #
        self.process['int'] = {}
        for i, wall in enumerate(self.house):
            list_x = get_range(self.house[wall], 'x')
            list_y = get_range(self.house[wall], 'y')
            if np.all(self.house[wall]['x'] == self.house[wall]['x'][0]):  # wall is along the y axis
                z_lin_flat = z_lin[:, list_x].flatten()
                mask = np.isnan(np.array(z_qint[:,list_x]).flatten())
                z_lin_flat[mask] = np.nan
                self.process['int'][wall] = { 'z_lin': np.array(z_lin_flat),
                                        'z_q': np.array(z_qint[:, list_x]).flatten(),
                                        'ax': y_mesh[:,0]}

            else:  # wall is along the x axis
                z_lin_flat = z_lin[list_y,:].flatten()
                mask = np.isnan(np.array(z_qint[list_y,:]).flatten())
                z_lin_flat[mask] = np.nan
                self.process['int'][wall] = { 'z_lin': np.array(z_lin_flat), 
                                        'z_q': np.array(z_qint[list_y,:]).flatten(),
                                        'ax': x_mesh[0,:] }
        self.soil = {'house':{'x':x_mesh,'y':y_mesh,'linear': z_lin, 'quadratic': z_qint}}
    
    def fit_gaussian(self, i_guess, tolerance, step):
        """
        Fits Gaussian shapes to the data points in the house object and interpolates the shapes.

        Parameters:
        - i_guess (float): Initial guess for the root finding algorithm.
        - tolerance (float): Tolerance for the root finding algorithm.
        - step (float): Step size for the root finding algorithm.

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
            y_data = self.process['int'][wall]["z_lin"]

            # Drop nan values
            mask = np.isnan(y_data)
            x_data = x_data[~mask]
            y_data = y_data[~mask]

            index = np.argmin(y_data)
            y_normal = np.concatenate((y_data[:index+1], y_data[:index][::-1]))
            x_gauss = np.concatenate((-x_data[:index+1][::-1], x_data[:index]))
            x_data = np.concatenate((x_data[:index+1], x_data[index] + x_data[:index+1]))

            optimized_parameters, params_cov = curve_fit(f= gaussian_shape, xdata=x_gauss, ydata=y_normal) 
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
        self.soil['soil'] = {'x': X , 'y': Y, 'z': z_gaussian}
    
    def SRI(self):
        """
        Calculates the Settlement related intensity (SRI) values for each wall in the house.

        ## Returns:
            dict: The updated object with the SRI values stored in the `SRI` attribute.
        """
        self.soil['sri'] = {} 
        x_coords = {}
        
        for wall_num, key in enumerate(self.house):
            wall = self.house[key]
            wallz = wall['z'] - max(wall['z']) #Normalise displacements against each other  
            
            w0 = wallz[0]
            w1 = wallz[-1]

            length = hwall_length(wall, wall_num+1)
            if (wall_num + 1) % 2 == 0:
                x_coords[wall_num] = wall['x']
            else:
                x_coords[wall_num] = wall['y']        

            x = x_coords[wall_num]
            x0 = x[0]
            xmin = x[np.argmin(wallz)]
            s_vmax = np.abs(min(wallz))

            d_deflection = 0
            for i,z in enumerate(wallz): # Find maximum relative displacement
                dx_svmax = np.abs(x[i] - x0)
                deltai = z - ((w1 - w0) / length) * dx_svmax
                deltai = round(deltai,3)
                d_deflection = deltai if deltai >= d_deflection else d_deflection

            wmin = np.min([w0, w1])
            wclose = wmin if np.abs(wmin) != s_vmax else np.max([w0, w1])
            ind = np.where(wallz == wclose)
            xclose = x_coords[wall_num][ind]
            phi = float(np.arctan((s_vmax - np.abs(wclose)) / np.abs(xclose - xmin)))

            omega = np.arctan((w0 - w1) / length)

            beta = phi + omega if d_deflection != 0 else 0

            self.soil['sri'][key] = {'Smax': abs(min(wall['z'])),
                                'dSmax': abs(s_vmax),
                                'D/L': abs(s_vmax)/length,
                                'drat': abs(d_deflection),
                                'omega': abs(omega),
                                'phi': abs(phi),
                                'beta': abs(beta)}  
    
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

        

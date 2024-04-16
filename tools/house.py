import itertools
import numpy as np
import pandas as pd
from scipy.interpolate import griddata, interp1d
from scipy.optimize import curve_fit

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
        self.datadf = {}

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
            list_x = self.get_range(self.house[wall], 'x')
            list_y = self.get_range(self.house[wall], 'y')
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
            guess = self.find_root_iterative(i_guess, optimized_parameters, tolerance, step)

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
        y_coords = {}
        
        for wall_num, key in enumerate(self.house):
            wall = self.house[key]
            w0 = wall['z'][0]
            w1 = wall['z'][-1]
            length = self.hwall_length(wall, wall_num)

            # Get coordinates dynamically based on wall number
            if wall_num % 2 == 0:
                x_coords[wall_num] = wall['y']
                y_coords[wall_num] = wall['x']
            else:
                x_coords[wall_num] = wall['x']
                y_coords[wall_num] = wall['y']
            # -------------------------- differential settlement ------------------------- #
            s_vmax = self.process['params'][key]['s_vmax']
            
            xmin = x_coords[wall_num][np.argmin(wall['z'])]
            x0 = x_coords[wall_num][0]
            
            x_svmax = xmin - x0
            d_deflection = s_vmax - (w0 - w1 / length) * x_svmax
            omega = np.arctan(d_deflection / length)
            
            # --------------------------------- rotation --------------------------------- #
            wclose = np.max([w0, w1])
            ind = np.where(wall['z'] == wclose)
            xclose = x_coords[wall_num][ind] if wall_num % 2 == 0 else y_coords[wall_num][ind]
            phi = float(s_vmax - w0 - w1 / length * xclose)
            
            # ---------------------------- angular distortion ---------------------------- #
            beta = phi + omega

            self.soil['sri'][key] = {'d_deflection': d_deflection,
                        'omega': omega,
                        'phi': phi,
                        'beta': beta}     


    def LTSM(self, limit_line,eg_rat):
        """
        Compute LTSM parameters and strain measures for a given wall.

        Parameters:
        - wall (int): The wall index.
        - limit_line (float): The limit line value.
        - height (float): The height of the wall.
        - eg_rat (float): The ratio of the wall's effective gauge length to its height.
        - i (int): The iteration index.
        - df (DataFrame): The input data.

        Returns:
        - X (array): The X values.
        - W (array): The W values.
        - x_inflection (float): The x_inflection value.
        - xnormal (float): The xnormal value.
        - x_limit (float): The x_limit value.
        - xi (float): The xi value.
        - xj (float): The xj value.
        - df (DataFrame): The input data.
        """
        self.process['ltsm'] = {'results': {}, 'values': {}, 'variables': {}}

        for wall_ in self.house:
            i = list(self.house.keys()).index(wall_)
            wall = self.house[wall_] 
            params = self.process['params'][wall_]
            length = self.hwall_length(wall,i)
            height = wall['height']
            
            W = gaussian_shape(params['x_gauss'], params['s_vmax'], params['x_inflection'])
            X = params['x_gauss']
            # -------------------------- Compute LTSM parameters ------------------------- #
            x_inflection = np.abs(params['x_inflection'])
            w_inflection = interp1d(X, W, kind = 'nearest')(x_inflection)
            w_current = interp1d(X, W, kind = 'nearest')(length)
            x_limit = np.abs(interp1d(W, X, kind = 'nearest')(limit_line))
            l_hogging = max((length - x_inflection) * 1e3, 0)
            lh_hogging = l_hogging / height
            dw_hogging = np.abs(w_current - w_inflection) ## location of building
            dl_hogging = 0 if l_hogging == 0 else dw_hogging / l_hogging

            l_sagging = length * 1e3 - l_hogging
            lh_sagging = l_sagging / (height / 2)
            dw_sagging = np.abs(W.min() + w_inflection) ## fix this
            dl_sagging = dw_sagging / l_sagging

            ratio = height/ 2*1e3
            uxy = (wall['phi'][-1] - wall['phi'][0])* 1000 * ratio
            e_horizontal = uxy / length*1e3
            # -------------------------- Compute strain measures ------------------------- #
            e_bending_hogg = dl_hogging * (3 * lh_hogging / (1 / 4 * lh_hogging ** 2 + 1.2 * eg_rat))
            e_shear_hogg = dl_hogging * (3 * eg_rat / ((0.5*lh_hogging**2) + 2 * 1.2 * eg_rat))

            e_bending_sagg = dl_sagging * (6 * lh_sagging / (lh_sagging ** 2 + 2 * eg_rat))
            e_shear_sagg = dl_sagging * (3 * lh_sagging / (2 * lh_sagging ** 2 + 2 * 1.2 * eg_rat))

            e_bending = np.max([e_bending_sagg, e_bending_hogg])
            e_shear = np.max([e_shear_sagg, e_shear_hogg])
            e_horizontal = 0  ## How do you calculate delta L

            e_bt = e_bending + e_horizontal
            e_dt = e_horizontal / (2 + np.sqrt((e_horizontal / 2) ** 2 + e_shear ** 2))
            e_tot = np.max([e_bt, e_dt])

            self.process['ltsm']['results'][wall_] = {'e_tot': e_tot,
                                 'e_bt': e_bt,
                                 'e_dt': e_dt,
                                 'e_bh': e_bending_hogg,
                                 'e_bs': e_bending_sagg,
                                 'e_sh': e_shear_hogg,
                                 'e_ss': e_shear_sagg,
                                 'e_h': e_horizontal,
                                 'l_h': l_hogging,
                                 'l_s': l_sagging,
                                 'dw_h': dw_hogging,
                                 'dw_s': dw_sagging,}
            
            self.process['ltsm']['values'][wall_] = {'x': X,
                                 'w': W,}
            
            self.process['ltsm']['variables'][wall_] = {
                                        'xinflection': x_inflection,
                                        'xlimit': x_limit,
                                        'limitline': limit_line,
                                        's_vmax': params['s_vmax']} 
    
    def find_root_iterative(self, guess, parameters, tolerance, step):
        output = gaussian_shape(guess, parameters[0],parameters[1])
        while abs(output) > tolerance:
            guess += step 
            output = gaussian_shape(guess, *parameters)
        return guess
    
    def hwall_length(self,wall,i):
        if i % 2 == 0:  # Wall along y axis
            xi = wall['y'].min()
            xj = wall['y'].max()    
        else:  # Wall along x axis
            xi = wall['x'].min()
            xj = wall['x'].max()
        return xj - xi

    def get_range(self, wall, key):
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
    
    def process_dfs(self, values):
        """
        Turn data dictionary into their respective dataframes

        Args:
            values = List of dictionaries containing the data to be converted into a dataframe

        """
        for variable, dictionary in enumerate(values):
            values = [round(values, 2) for values in dictionary.values()] 
            cols = dictionary.keys()
            df = pd.DataFrame([values], columns=cols)
            self.datadf[f'{variable}'] = df

def interpolate_2d(x_boundary, y_boundary, z_boundary, x_values, y_values, method):
    Z_interpolation = griddata((x_boundary, y_boundary), z_boundary, (x_values, y_values), method=method)
    return Z_interpolation

def gaussian_shape(x, s_vmax, x_inflection):
    gauss_func = s_vmax * np.exp(-x**2/ (2*x_inflection**2))
    return gauss_func

        

import traceback

import numpy as np
from scipy.interpolate import interp1d

from .empirical_limits import empirical_limits
from ..utils import gaussian_shape, hwall_length

def compute_damage_parameter(damage: dict = None, object = None) -> dict:
    """
    Calculate the damage parameters for a given set of damages and an object. Will compute 

    ## Args:
        damage (dict, optional): A dictionary containing the damage information. Defaults to None.
        object (object, optional): An object representing the damaged structure. Defaults to None.

    ## Returns:
        dict: A dictionary containing the calculated damage parameters.

    """
    dam_pw = {}
    test = object is not None 
    if test:
        walls = list(object.house.keys())
    else:
        id_list = [damage[crack]['wall_id'] for crack in damage.keys()]
        walls = list(set(id_list)) 

    for key in list(damage.keys()):
        dict_ = damage[key]
        damage[key]['c2_w'] = dict_['c_w']**2 * dict_['c_l'] 

    for wall in walls:
        if test:
            try:
                area = object.house[wall]['area']
            except KeyError as e:
                print(f"Error: Index ({wall}) is out of range.")
                print(f"Exception message: {str(e)}")
                continue
        else:
            area = damage[wall]['area']
            
        n_c = []
        c_w_n = []
        c_w_d = []
        rel_walls = [key for key in list(damage.keys()) if damage[key]['wall_id'] == wall]
        for key in rel_walls:
            param = damage[key]
            n_c += [key]
            c_w_n += [damage[key]['c2_w']]
            c_w_d += [param['c_w'] * param['c_l']]
        n_c = len(n_c)
        c_w = sum(c_w_n) / sum(c_w_d) if len(c_w_d) != 0 else 0

        psi = 2* n_c**0.15 * c_w**0.3
        mu = area * psi
        dam_pw[wall] =  {'area' : area,
                        'n_c' : n_c,
                        'c_w ': c_w,
                        'psi': psi}
        dam_pw[wall] = {key: round(value, 2) 
                        for key, value 
                        in {'area': area, 'n_c': n_c, 'c_w': c_w, 'psi': psi}.items()}

    num = 0
    den = 0
    for wall in dam_pw.keys():
        num += dam_pw[wall]['psi'] * dam_pw[wall]['area']
        den += dam_pw[wall]['area']

    psi_building = round(num/den, 2)

    return {'psi_building': psi_building,
            'psi_wall': dam_pw}

def evaluate_wall(wall_values, empirical_limits) -> list:
    """
    Evaluate the wall based on the given wall values and empirical limits.

    Args:
        wall_values (dict): A dictionary containing the values of different parameters for the wall.
        empirical_limits (dict): A dictionary containing the empirical limits for different parameters.

    Returns:
        list: A list of assessment reports for each parameter.

    """
    wall_report = {}
    for parameter, parameter_test in empirical_limits.items():
        param_report = []
        current_value = wall_values.get(parameter, None)
        
        if current_value is not None:
            for test in parameter_test:
                limits = test['limits']
                for i, limit in enumerate(limits):
                    if current_value <= limit:
                        description_index = i
                        break
                else:
                    description_index = len(limits) - 1
                try:
                    param_report.append({ 
                        'source': test['source'],
                        'assessment': test['description'][description_index - 1],
                        'value': current_value,
                        'limit': limits[description_index],
                        'DL': test['DL'][description_index - 1],
                        'comment': f"Assessment based on {parameter}"
                    })
                except IndexError as e:
                    tb_info = traceback.format_exc(limit=-1)  
                    print(f"Error: Index ({description_index}) is out of range. Param: {parameter}, test: {test['source']}.")
                    print(f"Exception message: {str(e)}")
                    print("Detailed traceback:")
                    print(tb_info)
                    print("Please verify in empirical_limits the number of limits, description and degrees are coherent\n")
                    continue  
        wall_report[parameter] = param_report 
    return wall_report

def EM(soil_data: dict, limits = None) -> dict:
    """
    Performs an assessment on the building through available Empirical methods.

    Parameters:
    soil_data (dict): A dictionary containing soil data which has the following structure
    soil_data -> (dict) = {'S_max': abs(min(wall['z'])),
                            'dS_max': abs(s_vmax),
                            'D/L': abs(s_vmax)/length,
                            'D_deflection': abs(d_deflection),
                            'omega': abs(omega),
                            'phi': abs(phi),
                            'beta': abs(beta)}  

    Returns:
    dict: A dictionary containing assessment reports for each wall ID.
    """
    all_reports = {}

    if limits is None:
        limits = empirical_limits()

    for wall_id, wall_values in soil_data.items():
        report = evaluate_wall(wall_values, limits)
        all_reports[wall_id] = report
    return all_reports


def LTSM(object, limit_line, eg_rat: int = 11, method: str = 'greenfield'):
    """
    Compute LTSM parameters and strain measures for a given wall.

    Parameters:
    - walls (dict): Dictionary witht the values for the building geometry and skew measurements
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
    dict_ = {'results': {}, 'values': {}, 'variables': {}}

    for wall_ in object.house:
        i = list(object.house.keys()).index(wall_) + 1
        wall = object.house[wall_] 
        length = hwall_length(wall,i)
        height = wall['height']
        
        # ----------------------------- Determine method ----------------------------- #
        if method == 'greenfield':
            params = object.process['params'][wall_]
            W = gaussian_shape(params['x_gauss'], params['s_vmax'], params['x_inflection'])
            X = params['x_gauss']
            x_inflection = np.abs(params['x_inflection'])
            w_inflection = interp1d(X, W, kind = 'nearest')(x_inflection)
    
        if method == 'measurements':
            W = object.process['int'][wall_]['ax']
            X = object.process['int'][wall_]['z_q']
            dW_dx = np.gradient(W, X)
            d2W_dx2 = np.gradient(dW_dx, X)
            ind = np.where(np.diff(np.sign(d2W_dx2)))[0]
            x_inflection = X[ind]
            w_inflection = W[ind] 

        # -------------------------- Compute LTSM parameters ------------------------- #
        w_current = interp1d(X, W, kind = 'nearest')(length)
        x_limit = np.abs(interp1d(W, X, kind = 'nearest')(limit_line))
        l_hogging = max((length - x_inflection) * 1e3, 0)
        lh_hogging = l_hogging / height
        dw_hogging = np.abs(w_current - w_inflection) ## location of building
        dl_hogging = 0 if l_hogging == 0 else dw_hogging / l_hogging

        l_sagging = length * 1e3 - l_hogging
        lh_sagging = l_sagging / (height / 2)
        dw_sagging = np.abs(W.min() + w_inflection)
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

            
        dict_['results'][wall_] = {'e_tot': e_tot,
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
        
        dict_['values'][wall_] = {'x': X,
                                'w': W,}
        
        dict_['variables'][wall_] = {'xinflection': x_inflection,
                                    'xlimit': x_limit,
                                    'limitline': limit_line,
                                    's_vmax': params['s_vmax']} 
    
    object.process['ltsm'] = dict_ 
            


import numpy as np
from scipy.interpolate import interp1d

from .empirical_limits import empirical_limits
from ..utils import gaussian_shape, hwall_length

def evaluate_wall(wall_values, empirical_data):
    """
    Evaluates the wall values against the empirical data and generates a report.

    Args:
        wall_values (dict): A dictionary containing the wall values.
        empirical_data (dict): A dictionary containing the empirical data.

    Returns:
        list: A list of dictionaries representing the assessment report. Each dictionary contains the following keys:
            - 'source': The source of the test.
            - 'assessment': The assessment result, either "Pass" or "Fail".
            - 'value': The current value being evaluated.
            - 'limit': The limit for the test.
            - 'comment': A comment describing the test.
    """
    report = []
    for key, tests in limits.items():
        current_value = wall_data[key]
        for test in tests:
            passed = current_value <= test['limit']
            result = {
                'source': test['source'],
                'assessment': "Pass" if passed else "Fail",
                'value': current_value,
                'limit': test['limit'],
                'comment': test['description']
            }
            report.append(result)
    return report

def EM(soil_data: dict, limits = empirical_limits) -> dict:
    """
    Perform EM assessment on soil data.

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
    for wall_id, wall_values in soil_data['sri'].items():
        report = evaluate_wall(wall_values, limits)
        all_reports[wall_id] = report
    return all_reports


def LTSM(object, limit_line, eg_rat = 11, save = False):
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
        params = object.process['params'][wall_]
        length = hwall_length(wall,i)
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
            


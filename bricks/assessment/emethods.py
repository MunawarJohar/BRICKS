from typing import List, Union, Dict

from .empirical_limits import ParameterLimits, empirical_limits

def evaluate_wall(wall_values: Dict[str, float], empirical_limits: ParameterLimits) -> Dict[str, List[Dict]]:
    """
    Evaluate the wall based on the given wall values and empirical limits.

    Args:
        wall_values (dict): A dictionary containing the values of different parameters for the wall.
        empirical_limits (ParameterLimits): An instance of ParameterLimits data class containing the empirical limits.

    Returns:
        dict: A dictionary with parameter names as keys and lists of assessment reports as values.
    """
    wall_report = {}
    limit_data = empirical_limits.__dict__  # Convert data class to a dictionary of lists for iteration

    for parameter, tests in limit_data.items():
        param_report = []
        current_value = wall_values.get(parameter, None)
        
        if current_value is not None:
            for test in tests:
                for i, limit in enumerate(test.limits):
                    if current_value <= limit:
                        description_index = i
                        break
                else:
                    description_index = len(test.limits) - 1
                param_report.append({
                    'source': test.source,
                    'assessment': test.description[max(0, description_index - 1)],
                    'value': current_value,
                    'limit': test.limits[min(description_index, len(test.limits) - 1)],
                    'DL': test.DL[max(0, description_index - 1)],
                    'comment': f"Assessment based on {parameter}"
                })
        wall_report[parameter] = param_report
    return wall_report

def EM(soil_data: Dict[str, Dict[str, float]], limits=None) -> Dict[str, Dict]:
    """
    Performs an assessment on the building through available empirical methods.

    Parameters:
    soil_data (dict): A dictionary containing soil data which has the following structure:
                      {'S_max': abs(min(wall['z'])),
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
        limits = empirical_limits()  # Assuming this creates an instance of the ParameterLimits data class

    for wall_id, wall_values in soil_data.items():
        report = evaluate_wall(wall_values, limits)
        all_reports[wall_id] = report
    return all_reports

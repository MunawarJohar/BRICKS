def process(coords, abs_disp, max_rate, rate_multiple):
    coords = coords - min(coords)
    rel_disp = np.insert(np.diff(abs_disp),0,0)

    rel_iter = find_iter(rel_disp, max_rate, rate_multiple)
    abs_iter = find_iter(abs_disp, max_rate, rate_multiple)
    print(rel_iter, abs_iter)
    dydt_abs = abs_disp//abs_iter
    dydt_rel = rel_disp//rel_iter

    dydx_abs = np.gradient(dydt_abs,coords)
    dydx_rel = np.gradient(dydt_rel,coords)
    
    return dydx_abs/dydx_rel

def find_iter(abs_disp, max_rate, rate_multiple = False):
    """
    Calculates the number of iterations based on the absolute displacement, maximum rate, and rate multiple.

    Parameters:
    abs_disp (list): A list of absolute displacements.
    max_rate (float): The maximum rate.
    rate_multiple (float): The rate multiple.

    Returns:
    int: The number of iterations.

    """
    iter = max(abs(abs_disp)) // max_rate
    if rate_multiple:
        iter = iter + rate_multiple - iter % rate_multiple
    return iter
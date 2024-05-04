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
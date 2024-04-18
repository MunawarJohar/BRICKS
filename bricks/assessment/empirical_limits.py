def empirical_limits():
    """
    This function defines the limits for different parameters that dictate the behavior and damage expected from subsiding masonry buildings.
    
    Returns:
    A dictionary containing the limits for different parameters:
    - angular_distortion - beta: Limits for angular distortion.
    - max_diff_settlement - dSmax: Limits for maximum differential settlement.
    - max_settlement - Smax: Limits for maximum settlement.
    - deflection_ratio - drat: Limits for deflection ratio.
    - vertical_tilt - omega: Limits for vertical tilt.
    - rotation - phi: Limits for rotation.
    
    Each parameter is associated with a list of dictionaries, where each dictionary contains the following keys:
    - 'limit': The limit value.
    - 'description': A description of the limit.
    - 'source': The source of the limit.
    """
    literature = {
        'beta': [
            {'source': 'Skempton & McDonald (1956)', 
                'limits': [0,
                           3.33e-3,
                           6.66e-3],
                'description': ['No damage',
                                'Structural damage in beams or columns',
                                'Cracking in wall panels']},
            {'source': 'Bjerrum (1963)', 
                'limits': [0,
                           2e-3,
                           3.33e-3,
                           6.66e-3],
                'description': ['No damage',
                                'Cracking',
                                'Severe cracking in panel walls',
                                'Serious cracking in panel walls and brick walls',]},
            {'source': 'Polshin & Tokar (1957)', 
                'limits': [0,
                           5e-3],
                'description': ['No damage',
                                'First visible cracking to no infill walls']},
            {'source': 'Wood (1958)', 
                'limits': [0,
                           2.2e-3],
                'description': ['No damage',
                                'First visible cracking to brick panels and walls']},
            {'source': 'Bozuzuk (1962)', 
                'limits': [0,
                           1e-3],
                'description': ['No damage',
                                'Cracking of clay brick units with mortar']},
            {'source': 'Meyerhof (1953)', 
                'limits': [0,
                           2.5e-3],
                'description': ['No damage',
                                'Cracking']},]
            
        # ],
        # 'max_diff_settlement': [
        #     {'limit': 0.032, 'description': "In sand (all types of foundation)", 'source': "Generic Source"},
        #     {'limit': 0.045, 'description': "In clay (all types of foundation)", 'source': "Generic Source"},
        # ],
        # 'max_settlement': [
        #     {'limit': 0.051, 'description': "Isolated foundations in sand soil", 'source': "Generic Source"},
        #     {'limit': 0.076, 'description': "Isolated foundations in clay soil", 'source': "Generic Source"},
        #     # Include other limits similarly
        # ],
        # 'drat': [
        #     {'limit': 0.0003, 'description': "for L/H ≤ 2 Sagging", 'source': "Polshin & Tokar (1957)"},
        #     {'limit': 0.001, 'description': "for L/H = 8 Sagging", 'source': "Polshin & Tokar (1957)"},
        # ],
        # 'omega': [
        #     {'limit': 166, 'description': "Good condition limit", 'source': "IGWR (2009), Rotterdam Municipality"},
        # ],
        # 'phi': [
        #     {'limit': 0.002, 'description': "No damage", 'source': "CUR (1996), Dutch regulations"},
        #     {'limit': 0.0033, 'description': "Structural Damage", 'source': "CUR (1996), Dutch regulations"},
        # ]
    }

    return literature

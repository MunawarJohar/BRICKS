def empirical_limits():
    """
    This function defines the limits for different parameters that dictate the behavior and damage expected from subsiding masonry buildings.
    
    Returns:
    A dictionary containing the limits for different parameters:
    - 'angular_distortion': Limits for angular distortion.
    - 'max_diff_settlement': Limits for maximum differential settlement.
    - 'max_settlement': Limits for maximum settlement.
    - 'deflection_ratio': Limits for deflection ratio.
    - 'vertical_tilt': Limits for vertical tilt.
    - 'rotation': Limits for rotation.
    
    Each parameter is associated with a list of dictionaries, where each dictionary contains the following keys:
    - 'limit': The limit value.
    - 'description': A description of the limit.
    - 'source': The source of the limit.
    """
    return {
        'angular_distortion': [
            {'limit': 6.66e-3, 'description': "Structural damage in beams or columns", 'source': "Skempton & McDonald (1956)"},
            {'limit': 3.33e-3, 'description': "Cracking in wall panels", 'source': "Skempton & McDonald (1956)"},
            {'limit': 10e-3, 'description': "First visible cracking", 'source': "Wood (1958)"},
            # Include other limits similarly
        ],
        'max_diff_settlement': [
            {'limit': 0.032, 'description': "In sand (all types of foundation)", 'source': "Generic Source"},
            {'limit': 0.045, 'description': "In clay (all types of foundation)", 'source': "Generic Source"},
        ],
        'max_settlement': [
            {'limit': 0.051, 'description': "Isolated foundations in sand soil", 'source': "Generic Source"},
            {'limit': 0.076, 'description': "Isolated foundations in clay soil", 'source': "Generic Source"},
            # Include other limits similarly
        ],
        'deflection_ratio': [
            {'limit': 0.0003, 'description': "for L/H ≤ 2 Sagging", 'source': "Polshin & Tokar (1957)"},
            {'limit': 0.001, 'description': "for L/H = 8 Sagging", 'source': "Polshin & Tokar (1957)"},
        ],
        'vertical_tilt': [
            {'limit': 166, 'description': "Good condition limit", 'source': "IGWR (2009), Rotterdam Municipality"},
        ],
        'rotation': [
            {'limit': 0.002, 'description': "No damage", 'source': "CUR (1996), Dutch regulations"},
            {'limit': 0.0033, 'description': "Structural Damage", 'source': "CUR (1996), Dutch regulations"},
        ]
    }

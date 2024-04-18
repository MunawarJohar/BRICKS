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
    return {
        'beta': [
            {'source': 'Boscardin & Cording (1989)', 
                'limits': [0,1e-3,1.5e-3,3.25e-3,6.5e-3,3e-3,1e3],
                'description': ['Negligible damage',
                                'Very slight',
                                'Slight',
                                'Moderate',
                                'Severe',
                                'Very severe'],
                'degree': [0,0.2,0.4,0.6,0.8,1]},

            {'source': 'Skempton & McDonald (1956)', 
                'limits': [0,3.33e-3,6.66e-3],
                'description': ['No damage',
                                'Structural damage in beams or columns',
                                'Cracking in wall panels'],
                'degree': [0,0.5,1.0,0.6,0.8,1]  },

            {'source': 'Bjerrum (1963)', 
                'limits': [0,2e-3,3.33e-3,6.66e-3],
                'description': ['No damage',
                                'Cracking',
                                'Severe cracking in panel walls',
                                'Serious cracking in panel walls and brick walls',],
                'degree': [0,0.75,1.0,1.0]},

            {'source': 'Polshin & Tokar (1957)', 
                'limits': [0,5e-3],
                'description': ['No damage',
                                'First visible cracking to no infill walls'],                                
                'degree': [0,0.5,]},

            {'source': 'Wood (1958)', 
                'limits': [0,2.2e-3],
                'description': ['No damage',
                                'First visible cracking to brick panels and walls'],
                'degree': [0,0.5,]},

            {'source': 'Bozuzuk (1962)', 
                'limits': [0,1e-3],
                'description': ['No damage',
                                'Cracking of clay brick units with mortar'],
                'degree': [0,0.5,]},

            {'source': 'Meyerhof (1953)', 
                'limits': [0,2.5e-3],
                'description': ['No damage',
                                'Cracking'],
                'degree': [0,1.0]},],
    
        'dSmax': [
            {'source': "Skemptom & McDonald (1956)", 
                'limits': [0,0.032], 
                'description': ['No damage', 'Damage in sand (all types of foundation)'],
                'degree': [0, 1.0]},
            {'source': "Skemptom & McDonald (1956)",
                'limits': [0,0.045],
                'description': ['No damage', 'Damage in clay (all types of foundation)'],
                'degree': [0, 1.0]}
                ],
        
        'phi': [
            {'source': "CUR (1996)", 
                'limits': [0,2e-3,3.3e-3,10e-3], 
                'description': ['No damage','Aesthetic damage','Structural damage','Risk for residents'],
                'degree': [0, 0.6,0.8,1.0]},
                ],

        'omega': [
            {'source': "IGWR (2009)", 
                'limits': [0,1/66,1/50,1/33], 
                'description': ['No damage','Acceptable damage','Small damage','Considerable damage'],
                'degree': [0, 0.35,0.5,0.75]},
                ],
    }

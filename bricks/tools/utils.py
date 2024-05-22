import numpy as np
from matplotlib.colors import LinearSegmentedColormap

def get_color_from_scale(level, scale, dlmax):
    scaled_level = level / dlmax
    return scale[int(scaled_level * (len(scale) - 1))]

def compute_param(strain_value):
    colors = ['#BBE3AB', '#FAFAB1', '#DF7E7D']  # Colors corresponding to thresholds
    thresholds = [0.5e-3, 1.67e-3, 3.33e-3]  # Thresholds
    cat = ['Negligible', 'Moderate', 'Severe']  # Categories

    ind = np.argmax([t - strain_value for t in thresholds if t <= strain_value])

    cmap = LinearSegmentedColormap.from_list("", [(0, colors[0]), (0.5, colors[1]), (1, colors[2])])
    normalized_strain = (strain_value - min(thresholds)) / (max(thresholds) - min(thresholds))
    
    rgba_color = cmap(normalized_strain)
    r, g, b, _ = rgba_color  # Extract RGB values from RGBA tuple
    r_int = int(r * 255)  # Convert float to integer in range [0, 255]
    g_int = int(g * 255)
    b_int = int(b * 255)
    hex_color = "#{:02X}{:02X}{:02X}".format(r_int, g_int, b_int)
    return hex_color, cat[ind]

def prepare_report(report: dict, wall: str)-> list:
    """
    Prepare a report for analysis.

    Args:
        report (dict): A dictionary containing the report data.

    Returns:
        tuple: A tuple containing the following elements:
            - data_matrix (numpy.ndarray): A 2D array of data values.
            - wall_param_labels (list): A list of labels for wall parameters.
            - sources (list): A sorted list of data sources.
            - description_annotations (list): A 2D list of description annotations.

    """
    all_sources = set()
    all_sources = {src['source'] for wall in report for param in report[wall] for src in report[wall][param]}
    sources = sorted(all_sources)
    parameters = list(next(iter(report.values())).keys())
    
    data_matrix = []
    wall_param_labels = []
    description_annotations = []  
    for parameter in parameters:
        row = []
        d_row = []
        current_data = {item['source']: (item['DL'], item['assessment']) for item in report[wall][parameter]}
        for source in sources:
            value, description = current_data.get(source, (np.nan, ""))  # Use np.nan for missing values
            row.append(value)
            d_row.append(description)
        data_matrix.append(row)
        description_annotations.append(d_row)
        wall_param_labels.append(f"{parameter}")  

    data_matrix = np.array(data_matrix, dtype=np.float32)  
    
    ## Why not?
    # annotations = []
    # for desc_row, yd in zip(description_annotations, wall_param_labels):
    #     for desc, xd in zip(desc_row, sources):
    #         annotations.append(dict(showarrow=False, text=f"<b>{desc}</b>", x=xd, y=yd, font=dict(color="black")))
    
    return data_matrix, wall_param_labels, sources, description_annotations
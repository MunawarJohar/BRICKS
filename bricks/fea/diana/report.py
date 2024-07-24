#%% Import Modules
import os
import shutil

#%% Walk
import os

def setup_analysis(base_path, config):
    """
    Setup analysis folders and generate scripts.

    Args:
        base_path (str): The base directory path to search for files.
        config (dict): Configuration dictionary containing results and script settings.
        
    Example of config:
        config = {
            'results': [
                {
                    'component': 'TDtY',
                    'result': 'Displacements',
                    'type': 'Node',
                    'limits': [-35, -28, -24, -20, -16, -12, -8, -4, 0]
                },
                {
                    'component': 'E1',
                    'result': 'Total Strains',
                    'type': 'Element',
                    'location': 'mappedintpnt',
                    'limits': [-0.004, -0.002, 0, 0.001, 0.0025, 0.005, 0.0075, 0.01, 0.02, 0.08]
                },
                {
                    'component': 'S1',
                    'result': 'Cauchy Total Stresses',
                    'type': 'Element',
                    'location': 'mappedintpnt',
                    'limits': [-3.5, -2, -1, -0.05, -0.01, 0, 0.01, 0.05, 1, 3, 61]
                },
                {
                    'component': 'Ecw1',
                    'result': 'Crack-widths',
                    'type': 'Element',
                    'location': 'mappedintpnt',
                    'limits': [0, 1, 2, 3, 4, 5, 10, 15, 20]
                }
            ],
            'script': {
                'analysis': "NLA",
                'load_cases': ['Building', 'Sub Deformation'],
                'load_steps': [30, 720],
                'load_factors_init': [0.0330000, 0.00138800],
                'snapshots': 6,
                'view_settings': {
                    'view_point': [0, 0, 25.0, 0, 1, 0, 5.2, 3.1, 5.5e-17, 19, 3.25],
                    'legend_font_size': 34,
                    'annotation_font_size': 28
                }
            }
        }
    """
    analysis_folder = os.path.join(base_path, 'analysis')
    plots_folder = os.path.join(analysis_folder, 'plots')

    os.makedirs(analysis_folder, exist_ok=True)
    os.makedirs(plots_folder, exist_ok=True)

    for result in config['results']:
        component_name = result['component']
        result_folder = os.path.join(plots_folder, component_name)
        os.makedirs(result_folder, exist_ok=True)

    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.dnb'):
                file_path = os.path.join(root, file)
                generate_scripts(file_path, plots_folder, config['results'], config['script'])


#%% Walk
def generate_scripts(file_path, plots_folder, results, script_config):
    """
    Generate Python scripts for analysis based on results.

    Args:
        file_path (str): Path to the .dnb file.
        plots_folder (str): Path to the plots folder.
        results (list): List of result dictionaries containing component and type.
        script_config (dict): Dictionary containing configuration for the script.

    Example of script_config:
        script_config = {
            'analysis': "NLA",
            'load_cases': ['Building', 'Sub Deformation'],
            'load_steps': [30, 720],
            'load_factors_init': [0.0330000, 0.00138800],
            'snapshots': 6,
            'view_settings': {
                'view_point': [0, 0, 25.0, 0, 1, 0, 5.2, 3.1, 5.5e-17, 19, 3.25],
                'legend_font_size': 34,
                'annotation_font_size': 28
            }
        }
    """
    analysis = script_config['analysis']
    load_cases = script_config['load_cases']
    load_steps = script_config['load_steps']
    load_factors_init = script_config['load_factors_init']
    snapshots = script_config['snapshots']
    view_settings = script_config['view_settings']

    steps = []
    load_factors = []

    for i in range(len(load_steps)): # Loop not to use numpy
        if i == 0:
            steps.append(load_steps[i])
            load_factor = load_steps[i] * load_factors_init[i]
            load_factors.append(load_factor)
        else:
            val = (snapshots - 1) // (len(load_steps) - 1)
            step_interval = (load_steps[i]) / val
            for j in range(1, val + 1):
                delta = sum(load_steps[:i]) + j * step_interval
                steps.append(int(delta))
                load_factor = (j * step_interval) * load_factors_init[i]
                load_factors.append(round(load_factor, 5))

    results_str = f"""
from diana import *
import os

results_str = {repr(results)}
    """

    script_content = f"""
# File path and export folder
file_name = r'{file_path}'
path_exp = r'{plots_folder}'

# Analysis and load cases
an = "{analysis}"
lc = {load_cases}
ls = {load_steps}
lfis = {load_factors_init}
snapshots = {snapshots}

steps = {steps}
load_factors = {load_factors}

# Define View setting in case it doesn't exist
try:
    addViewSetting("PY")
    setActiveViewSetting("PY")
    saveViewPoint("plot_vp", {view_settings['view_point']})
    setViewPoint("plot_vp")
except Exception as e:
    print(f'View Setting already exists: {{e}}')

# Iterate through results and steps
for result, limit in results_str:
    for i, step in enumerate(steps):
        step_name = f"Load-step {{step}}"
        lf = load_factors[i]
        lf_name = f"Load-factor {{lf:.5f}}"
        lc_name = lc[0] if i == 0 else lc[1]

        if result['type'] == 'Node':
            out = 'Output Diana'
        elif result['type'] == 'Element':
            out = 'Monitor Diana'
        
        last = step_name + ', ' + lf_name + ', ' + lc_name
        setResultCase([an, out, last])
        selectResult(result) # Select result has to go after setResultCase
        
        # Legend & annotations 
        setViewSettingValue("PY", "RESULT/TITLE/RANGE", "VISIBLE")
        setViewSettingValue("PY", "RESULT/TITLE/POSIT", "0.0100000 0.990000")
        setViewSettingValue("PY", "RESULT/TITLE/BORDER/BACK", False)
        setViewSettingValue("PY", "RESULT/TITLE/BORDER/FRAME", False)
        setViewSettingValue("PY", "RESULT/TITLE/FONT/SIZE", {view_settings['legend_font_size']})
        setViewSettingValue("PY", "RESULT/LEGEND/LBLFMT", "AUTO")
        setViewSettingValue("PY", "RESULT/LEGEND/LBLPRC", 2)
        setViewSettingValue("PY", "RESULT/LEGEND/FONT/FAMILY", "ARIAL")
        setViewSettingValue("PY", "RESULT/LEGEND/FONT/SIZE", {view_settings['legend_font_size']})
        setViewSettingValue("PY", "RESULT/LEGEND/ANNOTA", "RELFRQ")
        setViewSettingValue("PY", "RESULT/LEGEND/ANNFNT/SIZE", {view_settings['annotation_font_size']})
        setViewSettingValue("PY", "RESULT/LEGEND/FONT/COLOR", [31, 30, 29, 255])
        setViewSettingValue("PY", "RESULT/LEGEND/ANNFNT/COLOR", [68, 68, 68, 255])
        setViewSettingValue("PY", "RESULT/LEGEND/BORDER/BACK", False)
        setViewSettingValue("PY", "RESULT/LEGEND/BORDER/FRAME", False)

        # Set show max and minimum
        setViewSettingValue("PY", "RESULT/LABEL/EXTREM/LEVEL", "OFF")

        # Deformation settings
        setViewSettingValue("PY", "RESULT/EDGES/RENDEF", "FRE")
        setViewSettingValue("PY", "RESULT/DEFORM/MODE", "ABSOLU")
        setViewSettingValue("PY", "RESULT/DEFORM/ABSOLU/FACTOR", 5)
        setViewSettingValue("PY", "RESULT/DEFORM/DEFX", True)
        setViewSettingValue("PY", "RESULT/DEFORM/DEFY", True)
        setViewSettingValue("PY", "RESULT/DEFORM/DEFZ", True)
        setViewSettingValue("PY", "RESULT/CONTOU/BNDCLR/MAXCLR", [255, 0, 255, 255])
        setViewSettingValue("PY", "RESULT/CONTOU/BNDCLR/MINCLR", [0, 255, 255, 255])

        # Result-specific settings
        values = limit['limits']
        setViewSettingValue("PY", "RESULT/CONTOU/LEVELS", "SPECIF")
        setViewSettingValue("PY", "RESULT/CONTOU/LEGEND", "DISCRE")
        setViewSettingValue("PY", "RESULT/CONTOU/SPECIF/VALUES", values)
        setViewSettingValue("PY", "RESULT/CONTOU/AUTRNG", "LIMITS")
        setViewSettingValue("PY", "RESULT/CONTOU/LIMITS/MAXVAL", values[-1])
        setViewSettingValue("PY", "RESULT/CONTOU/LIMITS/MINVAL", values[0])
        setViewSettingValue("PY", "RESULT/CONTOU/LIMITS/BOUNDS", "CLAMP")

        # Save image
        image_path = os.path.join(path_exp, result['component'], f"{{step}}.png")
        if os.path.exists(image_path):
            os.remove(image_path)
        saveImage(image_path, 1800, 1100, 1)
    """

    script_path = os.path.join(plots_folder, "run_analysis.py")
    with open(script_path, 'w') as script_file:
        script_file.write(f"{results_str}\n" + script_content)

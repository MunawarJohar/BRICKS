#%% Import Modules
import os
import shutil

#%% Walk
def setup_analysis(base_path, results):

    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.dnb'):
                file_path = os.path.join(root, file)
                analysis_folder = os.path.join(root, 'analysis')
                plots_folder = os.path.join(root, 'plots')

                if not os.path.exists(analysis_folder):
                    os.makedirs(analysis_folder)

                if not os.path.exists(plots_folder):
                    os.makedirs(plots_folder)

                for result,_ in results:
                    result_folder = os.path.join(plots_folder, result['component'])
                    if not os.path.exists(result_folder):
                        os.makedirs(result_folder)

                generate_scripts(file_path, plots_folder, results)

#%% Walk
def generate_scripts(file_path, plots_folder, results):
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
an = "NLA"
lc = ['Building', 'Sub Deformation']
ls = [30, 720]
lfis = [0.0330000,0.00138800] 
snapshots = 6

# Initialize lists for steps and load factors
steps = []
load_factors = []

for i in range(len(ls)): # Loop not to use numpy
    if i == 0:
        steps.append(ls[i])
        load_factor = ls[i] * lfis[i] 
        load_factors.append(load_factor)  # Load factor for the first step
    else:
        val = (snapshots - 1) // (len(ls) - 1)
        step_interval = (ls[i]) / (val)  # Calculate step interval
        for j in range(1,val+1):
            delta = sum(ls[:i]) + j * step_interval
            steps.append(int(delta))
            load_factor = (j * step_interval)* lfis[i] 
            load_factors.append(round(load_factor, 5))

# Define View setting in case it doesn't exist
try:
    addViewSetting("PY")
    setActiveViewSetting( "PY" )
    
    #saveViewPoint("plot_vp2", [4.851194, 2.8778655, 19.878839, 0, 1, 0, 4.851194, 2.8778655, 5.5511151e-17, 18.595745, 3.1891839])
    saveViewPoint("plot_vp", [4.851194, 2.8778655, 19.878839, 0, 1, 0, 4.851194, 2.8778655, 5.5511151e-17, 19, 3.25])
    setViewPoint( "plot_vp" )

except Exception as e:
    print(f'View Setting already exists: {{e}}') 

for result,limit in results_str:
    
    for i,step in enumerate(steps):
        
        step_name = f"Load-step {{step}}"
        lf = load_factors[i]
        lf_name = f"Load-factor {{lf:.5f}}"
        lc_name = lc[0] if i == 0 else lc[1]
        
        if result['type'] == 'Node': 
            out = 'Output Diana'
        if result['type'] == 'Element': 
            out = 'Monitor Diana'
        
        last = step_name +', ' + lf_name + ', ' + lc_name
        setResultCase([an, out, last])
        selectResult(result) # Select result has to go after setResultCase
        
        # Legend & annotations 
        setViewSettingValue( "PY", "RESULT/TITLE/RANGE", "VISIBLE" )
        setViewSettingValue( "PY", "RESULT/TITLE/POSIT", "0.0100000 0.990000" )
        setViewSettingValue( "PY", "RESULT/TITLE/BORDER/BACK", False )
        setViewSettingValue( "PY", "RESULT/TITLE/BORDER/FRAME", False )
        setViewSettingValue( "PY", "RESULT/TITLE/FONT/SIZE", 34)
        setViewSettingValue( "PY", "RESULT/LEGEND/LBLFMT", "AUTO" )
        setViewSettingValue( "PY", "RESULT/LEGEND/LBLPRC", 2 )
        setViewSettingValue( "PY", "RESULT/LEGEND/FONT/FAMILY", "ARIAL" )
        setViewSettingValue( "PY", "RESULT/LEGEND/FONT/SIZE", 32)
        setViewSettingValue( "PY", "RESULT/LEGEND/ANNOTA", "RELFRQ" )
        setViewSettingValue( "PY", "RESULT/LEGEND/ANNFNT/SIZE", 28 )
        setViewSettingValue( "PY", "RESULT/LEGEND/FONT/COLOR", [ 31, 30, 29, 255 ] )
        setViewSettingValue( "PY", "RESULT/LEGEND/ANNFNT/COLOR", [ 68, 68, 68, 255 ] )
        setViewSettingValue( "PY", "RESULT/LEGEND/BORDER/BACK", False )
        setViewSettingValue( "PY", "RESULT/LEGEND/BORDER/FRAME", False )

        # Set show max and minimum
        setViewSettingValue( "PY", "RESULT/LABEL/EXTREM/LEVEL", "OFF" )
        # setViewSettingValue( "PY", "RESULT/LABEL/EXTREM/LEVEL", "GLOBAL" )
        # setViewSettingValue( "PY", "RESULT/LABEL/EXTREM/MINMAX", "BOTH" )
        # setViewSettingValue( "PY", "RESULT/LABEL/FONT/SIZE", 21 )
        # setViewSettingValue( "PY", "RESULT/LABEL/FONT/FAMILY", "ARIAL" )

        # Deformation settings
        setViewSettingValue("PY", "RESULT/EDGES/RENDEF", "FRE")
        setViewSettingValue("PY", "RESULT/DEFORM/MODE", "ABSOLU")
        setViewSettingValue("PY", "RESULT/DEFORM/ABSOLU/FACTOR", 5)
        setViewSettingValue("PY", "RESULT/DEFORM/DEFX", True)
        setViewSettingValue("PY", "RESULT/DEFORM/DEFY", True)
        setViewSettingValue("PY", "RESULT/DEFORM/DEFZ", True)
        setViewSettingValue("PY", "RESULT/CONTOU/BNDCLR/MAXCLR", [255, 0, 255, 255])
        setViewSettingValue( "PY", "RESULT/CONTOU/BNDCLR/MINCLR", [ 0, 255, 255, 255 ] )

        # Result-specific settings
        if result['component'] == 'Ecw1':
            values = limit['limits']
            setViewSettingValue( "PY", "RESULT/LEGEND/LBLFMT", "FLOAT" )
        elif result['component'] == 'TDtY':
            values = limit['limits']
            setViewSettingValue( "PY", "RESULT/LEGEND/LBLFMT", "FLOAT" )
        elif result['component'] == 'E1':
            values = limit['limits']
            setViewSettingValue( "PY", "RESULT/LEGEND/LBLFMT", "AUTO" )
        elif result['component'] == 'S1':
            values = limit['limits']
            setViewSettingValue( "PY", "RESULT/LEGEND/LBLFMT", "AUTO" )

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
            os.remove(image_path)  # Remove existing image if it exists
        saveImage(image_path, 1800, 1100, 1)
    """

    script_path = os.path.join(plots_folder, "run_analysis.py")
    with open(script_path, 'w') as script_file:
        script_file.write( f"{results_str}\n" + script_content)

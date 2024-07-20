import re
import os
import time
from datetime import datetime

import numpy as np
from matplotlib.pyplot import close

from ..plots.plots import plotconvergence, merge_plots

# ----------------------------- Model information ---------------------------- #
def calculate_runtime(filename):
        
    start_time = end_time = None
    pattern_start = r"/DIANA/AP/NL41\s+(\d{2}:\d{2}:\d{2})"
    pattern_end = r"/DIANA/DC/END\s+(\d{2}:\d{2}:\d{2})"

    with open(filename, 'r') as file:
        for line in file:
            match_start = re.search(pattern_start, line)
            if match_start:
                time_str = match_start.group(1)
                start_time = datetime.strptime(time_str, "%H:%M:%S")
            
            match_end = re.search(pattern_end, line)
            if match_end:
                time_str = match_end.group(1)
                end_time = datetime.strptime(time_str, "%H:%M:%S")

    if start_time and end_time:
        difference = end_time - start_time
        runtime = time.strftime('%H:%M:%S', time.gmtime(difference.total_seconds()))
    else:
        runtime = 'NaN'

    return runtime

def write_to_txt(directory, data):
    # Save some information in a txt file in the 'analysis' directory
    info_path = os.path.join(directory, 'info.txt')
    
    if os.path.exists(info_path):
        os.remove(info_path)  # remove the file if it already exists
    
    with open(info_path, 'w') as file:
        model_name = data['Model'][0]
        print(f'MODEL ANALYSIS information for model: {model_name.capitalize()}', file=file)
        print('----------------------------------------------------------\n', file=file)
        
        # Write headers
        headers = '\t'.join(data.keys())
        print(headers, file=file)
        
        # Find the maximum number of rows in the data
        max_rows = max(len(value) for value in data.values())
        
        # Write the data rows
        for i in range(max_rows):
            row = []
            for key in data.keys():
                if i < len(data[key]):
                    row.append(data[key][i])
                else:
                    row.append('')  # Empty string if there is no value for this column
            print('\t'.join(row), file=file)

    return file

def model_info(file_path,directory):
    runtime = calculate_runtime(file_path)
    subdirectories = directory.split(os.sep)
    model_name = subdirectories[-1]

    data = {
        'Model': [model_name],
        'Run time': [runtime],
    }
    return data

# ----------------------------- Model analysis ------------------------------ #
def read_file(filepath):
    with open(filepath, "r") as fileOUT:
        lines = fileOUT.readlines()
    return lines

def parse_lines(lines):
    Iterations = {}
    NoConvergenceSteps = []
    CurrentStepIndex = 0
    TotalStepIndex = 0
    ener_norm_temp = 0.0
    force_norm_temp = 0.0
    disp_norm_temp = 0.0

    PhaseYN = 0
    # Check that lines contains information
    for line in lines:
        fileOUT_string = line.split()

        if len(fileOUT_string) == 0:
            continue

        if (fileOUT_string[0] == '/DIANA/AP/PH40') and (fileOUT_string[5] == 'BEGIN'):
            # Turn on the flag and read the Phase number in the next row
            PhaseYN = 1

        # Check if the current row contains the start of a PHASE
        if (fileOUT_string[0] == 'PHASE') and (PhaseYN == 1):
            #Save phase number and make dictionary for the phase
            Temporary = fileOUT_string[1]
            KeyLabel = 'Phase ' 
            CurrentPhase = KeyLabel
            Iterations[KeyLabel] = {'Plastic_int': [], 'Crack_points': [], 'no_iter': [],
                                    "force_norm": [], "disp_norm": [], "energy_norm": [],
                                    "force_limit": 0, "disp_limit": 0, "energy_limit": 0}

        # Check for step initiation
        if (fileOUT_string[0] == 'STEP') and (fileOUT_string[2] == 'INITIATED:'):
            if PhaseYN == 0:
                KeyLabel = 'Phase '
                CurrentPhase = KeyLabel
                Iterations[KeyLabel] = {'Plastic_int': [], 'Crack_points': [], 'no_iter': [],
                                        "force_norm": [], "disp_norm": [], "energy_norm": [],
                                        "force_limit": 0, "disp_limit": 0, "energy_limit": 0}
                PhaseYN = 2

            CurrentStepIndex = int(fileOUT_string[1])
            TotalStepIndex += 1
            NoDisplConv = False
            NoForceConv = False
            NoEnerConv = False

        if len(fileOUT_string) > 7:
            if (fileOUT_string[3] == 'DISPLACEMENT') and (fileOUT_string[7] == 'TOLERANCE'):
                Expctd_displ_norm = float(fileOUT_string[9])
                Iterations[KeyLabel]["disp_limit"] = Expctd_displ_norm

            if (fileOUT_string[3] == 'FORCE') and (fileOUT_string[7] == 'TOLERANCE'):
                Expctd_force_norm = float(fileOUT_string[9])
                Iterations[KeyLabel]["force_limit"] = Expctd_force_norm

            if (fileOUT_string[3] == 'ENERGY') and (fileOUT_string[7] == 'TOLERANCE'):
                Expctd_ener_norm = float(fileOUT_string[9])
                Iterations[KeyLabel]["energy_limit"] = Expctd_ener_norm

        if (fileOUT_string[0] == 'RELATIVE') and (fileOUT_string[1] == 'DISPLACEMENT'):
            displ_norm = float(fileOUT_string[4])
            if Expctd_displ_norm < displ_norm:
                NoDisplConv = True
            else:
                disp_norm_temp = displ_norm

        if (fileOUT_string[0] == 'RELATIVE') and (fileOUT_string[1] == 'OUT'):
            force_norm = float(fileOUT_string[6])
            if Expctd_force_norm < force_norm:
                NoForceConv = True
            else:
                force_norm_temp = force_norm

        if (fileOUT_string[0] == 'RELATIVE') and (fileOUT_string[1] == 'ENERGY'):
            ener_norm = float(fileOUT_string[4])
            if Expctd_ener_norm < ener_norm:
                NoEnerConv = True
            else:
                ener_norm_temp = ener_norm

        if (fileOUT_string[0] == 'TOTAL' and fileOUT_string[1] == 'MODEL'):
            Temporary = int(fileOUT_string[2])
            if len(fileOUT_string) <= 8:
                Iterations[CurrentPhase]["Plastic_int"].append(Temporary)
            else:
                Iterations[CurrentPhase]["Crack_points"].append(Temporary)

        if (fileOUT_string[0] == 'STEP') and (fileOUT_string[2] == 'TERMINATED,'):
            if fileOUT_string[3] == 'NO':
                n_iter = re.findall(r'\d+', fileOUT_string[5])
                Temporary = int(n_iter[0])
                NoConvergenceSteps.append(CurrentStepIndex)
                with open("Convergence.txt", "a") as a_file:
                    a_file.write(f"Non-converged step number: {CurrentStepIndex}\n\n")
                    if NoDisplConv:
                        a_file.write("No displacement convergence found\n")
                        a_file.write(f"Relative displacement variation at non-convergence: {displ_norm}\n")
                        Iterations[CurrentPhase]["energy_norm"].append(displ_norm)
                    if NoForceConv:
                        a_file.write("No Force convergence found\n")
                        a_file.write(f"Relative Out-of-Balance force at non-convergence: {force_norm}\n")
                        Iterations[CurrentPhase]["energy_norm"].append(force_norm)
                    if NoEnerConv:
                        a_file.write("No Energy convergence found\n")
                        a_file.write(f"Relative Energy variation at non-convergence: {ener_norm}\n\n")
                        Iterations[CurrentPhase]["energy_norm"].append(ener_norm)
            else:
                Temporary = int(fileOUT_string[5])
                Iterations[CurrentPhase]["energy_norm"].append(ener_norm_temp)
                Iterations[CurrentPhase]["disp_norm"].append(disp_norm_temp)
                Iterations[CurrentPhase]["force_norm"].append(force_norm_temp)
            Iterations[CurrentPhase]["no_iter"].append(Temporary)

    return Iterations, NoConvergenceSteps

# ----------------------------------- Main ----------------------------------- #

def model_convergence(dir, minfo, merge=None):
    """
    This function reads a .OUT file, parses the lines, and plots the results.
    Optionally merges specified plots.

    Args:
        dir (str): Path to the .OUT file.
        minfo (dict): Dictionary containing model information.
        merge (dict): Dictionary specifying plots to merge.

    Returns:
        figures (list): List of figure objects.
    """
    directory = os.path.dirname(dir)

    lines = read_file(dir)
    iter, ncsteps = parse_lines(lines)
    
    figures, figures_titles, axes = plotconvergence(iter, ncsteps, minfo)
    
    if merge:
        merge_titles = merge.get('Titles')
        if merge_titles:
            indices_to_merge = [i for i, title in enumerate(figures_titles) if title in merge_titles]
            if indices_to_merge:
                merged_fig = merge_plots(
                    figures_titles, axes, indices_to_merge,
                    merge.get('x_label', "Load factor $\lambda$"), 
                    merge.get('y_label', "Norm values"), 
                    merge.get('title', "Merged Plot")
                )
                figures.append(merged_fig)
                figures_titles.append(merge.get('title', "Merged Plot"))
    
    return figures, figures_titles

def single_out_analysis(file_path,minfo, **kwargs):
    
    directory = os.path.dirname(file_path)
    analysis_dir = os.path.join(directory, 'analysis/convergence')
    os.makedirs(analysis_dir, exist_ok=True)

    # Write model information
    minfo_ = model_info(file_path,directory)
    minfo.update(minfo_)
    #write_to_txt(analysis_dir, minfo)
    
    # Perform the analysis
    merge = kwargs.get('merge', False)
    figures, titles = model_convergence(file_path, minfo, merge=merge)    
    
    # Save the figures
    for i, fig in enumerate(figures, start=1): 
        fig_path = os.path.join(analysis_dir, f'{titles[i-1]}.png')
        if os.path.exists(fig_path):
            os.remove(fig_path)  
        fig.savefig(fig_path)
        close()






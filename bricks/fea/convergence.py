import re
import os
import time
from datetime import datetime

import numpy as np
from matplotlib.pyplot import close

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

def write_to_txt(directory, model_name, data):
    # Save some information in a txt file in the 'analysis' directory
    info_path = os.path.join(directory, 'info.txt')
    
    if os.path.exists(info_path):
        os.remove(info_path)  # remove the file if it already exists
    
    with open(info_path, 'w') as file:
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
    ind = subdirectories.index('Models')
    mask_subd = subdirectories[ind+1:]
    model_name = '-'.join(mask_subd)

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

def model_convergence(dir):
    """
    This function prompts the user to enter the full path of a .OUT file,
    reads the file, parses the lines, and plots the results.

    Args:
        None

    Returns:
        None
    """
    lines = read_file(dir)
    iter, ncsteps = parse_lines(lines)
    figures = plot_results(iter, ncsteps)
    return figures

def single_model_analysis(file_path):
    
    directory = os.path.dirname(file_path)
    analysis_dir = os.path.join(directory, 'analysis')
    os.makedirs(analysis_dir, exist_ok=True)

    # Perform the analysis
    figures, titles = model_convergence(file_path)    
    for i, fig in enumerate(figures, start=1): # Save the figures
        fig_path = os.path.join(analysis_dir, f'{titles[i-1]}.png')
        if os.path.exists(fig_path):
            os.remove(fig_path)  # remove the file if it already exists
        fig.savefig(fig_path)
        close()

    # Write model information
    minfo = model_info(file_path,directory)
    write_to_txt(analysis_dir, minfo['Model'][0], minfo)

def analyse_models(modelling_directory):
    failed_files = []
    for root, _ , files in os.walk(modelling_directory):
        for file in files:
            if file.endswith('.out'):
                file_path = os.path.join(root, file)
                try:
                    single_model_analysis(file_path)
                except Exception as e:
                    failed_files.append(file_path)
                    print(f"Error processing file {file_path}: {e}")
    
    if failed_files:
        print("\nThe following files could not be processed:")
        for failed_file in failed_files:
            print(failed_file)



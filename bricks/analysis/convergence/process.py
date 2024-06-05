import re
import csv
from datetime import datetime

import numpy as np

# ----------------------------- Model information ---------------------------- #

def calculate_runtime(filename):
    start_time = end_time = None
    pattern = r"/DIANA/AP/NL41\s+(\d{2}:\d{2}:\d{2})"

    with open(filename, 'r') as file:
        for line in file:
            match = re.search(pattern, line)
            if match:
                time_str = match.group(1)
                time = datetime.strptime(time_str, "%H:%M:%S")
                if start_time is None:
                    start_time = time
                else:
                    end_time = time

    if start_time and end_time:
        runtime = end_time - start_time
        return runtime
    else:
        return None

def write_to_txt(directory,filename, data):
    filepath = os.path.join(directory, filename)

    with open(filepath, 'w') as file:
        print('\t'.join(data.keys()), file=file)

        for values in zip(*data.values()):
            print('\t'.join(map(str, values)), file=file)


def model_info(filename,direcotry):
    runtime = calculate_runtime(filename)
    
    subdirectories = direcotry.split(os.sep)
    model_name = '-'.join(subdirectories)

    info = {
        'Model': [model_name],
        'Run time': [runtime],
    }

    return info

def get_files(directory, extension):
    """
    Walks through a directory and returns all files with a specific extension.

    Args:
        directory (str): The directory to walk through.
        extension (str): The file extension to look for.

    Returns:
        list: A list of file paths that match the extension.
    """
    return [os.path.join(root, file)
            for root, dirs, files in os.walk(directory)
            for file in files
            if file.endswith(extension)]

# ----------------------------- Model analysis ------------------------------ #
def read_file(filepath):
    with open(filepath, "r") as fileOUT:
        lines = fileOUT.readlines()
    return lines

def parse_lines(lines,phase):
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
            KeyLabel = 'Phase ' + str(phase)
            CurrentPhase = KeyLabel
            Iterations[KeyLabel] = {'Plastic_int': [], 'Crack_points': [], 'no_iter': [],
                                    "force_norm": [], "disp_norm": [], "energy_norm": [],
                                    "force_limit": 0, "disp_limit": 0, "energy_limit": 0}

        # Check for step initiation
        if (fileOUT_string[0] == 'STEP') and (fileOUT_string[2] == 'INITIATED:'):
            if PhaseYN == 0:
                KeyLabel = 'Phase ' + str(phase)
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
                Temporary = int(fileOUT_string[6])
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

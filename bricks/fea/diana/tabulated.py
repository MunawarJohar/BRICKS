import os
import traceback
import numpy as np
import pandas as pd
from matplotlib.pyplot import close

from .utils import compute_damage_parameter, find_mean_cw, find_max_cw
from ..plots.plots import plot_analysis

def process_data_row(data_string):
    """
    Process a data row string and convert it into a list of floating-point values.

    Args:
        data_string (str): The input data string to be processed.

    Returns:
        list: A list of floating-point values extracted from the data string.

    Raises:
        ValueError: If the string cannot be converted to a float.

    """
    count = 0
    values = []

    while count < len(data_string):
        string = data_string[count:count+10]
        string = string.strip()
        if string:
            try:
                value = float(string)
            except ValueError as e:
                print(f"Error converting string to float: {string} - {e}")
                value = np.nan
        else:
            value = np.nan
        values.append(value)
        count += 11  # Move past the 10 spaces and the character after it

    return values

def read_file(filepath):
    with open(filepath, "r") as file:
        lines = file.readlines()
    return lines

def process_tb(file_path):
    """
    Process a tabulated file and return a pandas DataFrame.

    Args:
        file_path (str): The path to the tabulated file.

    Returns:
        pandas.DataFrame: The processed data as a DataFrame.

    Raises:
        Exception: If an error occurs during processing.

    """
    data_list = []
    info = {}
    errors = []

    step_n = None
    nodes = None
    intpnt = None
    values = False
    coordinates = False

    lines = read_file(file_path)

    for lin_num, line in enumerate(lines):
        try:
            words = line.split()

            if not words:  # Skip empty lines
                values = False
                coordinates = False
                continue    

            if words[:2] == ['Analysis', 'type']:  # Extract analysis type
                atype = words[-1]
                info['Analysis type'] = atype

                if lines[lin_num+1].split()[:2] == ['Step', 'nr.']:
                    step_n = lines[lin_num+1].split()[-1]
                    info['Step nr.'] = int(step_n)
                if lines[lin_num+2].split()[:2] == ['Load', 'factor']:
                    lf = lines[lin_num+2].split()[-1]
                    info['Load factor'] = float(lf)    
                continue

            if words[:2] == ['Elmnr', 'Intpt']: 
                coord = ['X0','Y0','Z0']
                if words[-3:] == coord:
                    variables = words[2:-3]
                    coordinates = True
                    ncoord = len([equal for equal in words if equal in set(coord)])
                else: 
                    variables = words[2:]
                values = True
                intpnt = True
                nodes = False
                continue
            elif words[0] == 'Nodnr':
                coord = ['X0','Y0']
                if words[-2:] == coord:
                    variables = words[1:-2]
                    coordinates = True
                    ncoord = len([equal for equal in words if equal in set(coord)])
                else: 
                    variables = words[1:]
                values = True 
                nodes = True
                intpnt = False
                continue

            if values and intpnt:  # Improve implementation not very resilient
                
                if line[1:6].strip().isdigit():
                    elmn_n = int(line[1:6])
                nodn_n = int(line[7:12])
                
                vals = {'Element': elmn_n, 'Integration Point': nodn_n}

                if coordinates:
                    count = ncoord*10 + (ncoord-1) + 3
                    data_string = line[15:-count]
                else:
                    data_string = line[15:]
                data = process_data_row(data_string)
                for j, var in enumerate(variables):
                    vals[var] = float(data[j])

                coord_val = line[-count+1:]
                x,y,z,_ = process_data_row(coord_val)
                coord_vals = {'X0': x, 'Y0': y,'Z0': z}

                record = {**info,**coord_vals,**vals}
                data_list.append(record)
                continue

            if values and nodes:  # Improve implementation not very resilient
                nodn_n = int(line[1:6])

                if coordinates:
                    count = ncoord*10 + (ncoord-1) + 3
                    data_string = line[9:-count]
                else:
                    data_string = line[9:]

                data = process_data_row(data_string)
                vals = {'Node': nodn_n}
                for j, var in enumerate(variables):
                    vals[var] = float(data[j])
                
                coord_val = line[-count+1:]
                x,y,_ = process_data_row(coord_val)
                coord_vals = {'X0': x, 'Y0': y}

                record = {**info, **coord_vals, **vals}
                data_list.append(record)
                continue
            
        except Exception as e:
            errors.append((lin_num, str(e)))
            traceback.print_exc()
            if len(errors) >= 1:
                print("Error limit reached, stopping processing.")
                return errors

    df = pd.DataFrame(data_list)
    # col = df.pop('Node')
    # insert = df.columns.get_loc('Element') + 1
    # df.insert(insert, 'Node', col)
    return df

def analyse_tabulated(df, analysis_info):
    """
    Analyzes tabulated data based on the given analysis information.

    Args:
        df (pandas.DataFrame): The tabulated data to be analyzed.
        analysis_info (dict): Information about the analysis to be performed.

    Returns:
        dict: A dictionary containing the analysis results for each analysis type.

    """
    data = {}
    for analysis in analysis_info:
        vals = []
        
        if 'Relative' in analysis:
            for node in analysis_info[analysis]['Node Nr']:
                u = df[df['Node'] == node][['Step nr.', 'TDtY']]
                vals.append(u)
        
        if 'Mutual' in analysis:
            sets = analysis_info[analysis]['Node Nr']
            typos = analysis_info[analysis]['Reference']
            for set,type in zip(sets, typos):
                merged_df = pd.DataFrame(df['Step nr.'].unique(), columns=['Step nr.'])
                for node,axis in zip(set,type):
                    temp_df = df[df['Node'] == node][['Step nr.',axis]].copy()
                    temp_df.rename(columns={'TDtY': f'{axis} Node {node}'}, inplace=True)
                    merged_df = pd.merge(merged_df, temp_df, on='Step nr.', how='left')
                merged_df.drop(columns=['Step nr.'], inplace=True)
                vals.append(merged_df)

        if 'Crack' in analysis:
            for EOI in analysis_info[analysis]['EOI']:
                vals.append(find_max_cw(EOI, df))

        if 'Damage' in analysis:
            for param in analysis_info[analysis]['parameters']:
                if param == 'cracks':
                    for crack_set in analysis_info[analysis]['parameters'][param]: 
                        c_w = compute_damage_parameter(df, crack_set)
                        vals.append(c_w)
        
        data[analysis] = vals
    return data

def single_tb_analysis(file_path, analysis_info, plot_settings):
    """
    Perform tabulated analysis on a single file.

    Args:
        file_path (str): The path to the tabulated file.
        analysis_info (dict): Information about the analysis.
        plot_settings (dict): Settings for plotting the analysis.

    Returns:
        tuple: A tuple containing two elements:
            - minfo (dict): Information about the analysis results, including the number of elements and nodes.
            - data (dict): The analyzed data.

    """
    directory = os.path.dirname(file_path)
    analysis_dir = os.path.join(directory, 'analysis/results')
    os.makedirs(analysis_dir, exist_ok=True)

    # Perform the analysis
    df = process_tb(file_path)
    data = analyse_tabulated(df, analysis_info)
    figures, titles = plot_analysis(data, analysis_info, plot_settings)

    for i, fig in enumerate(figures, start=1): # Save the figures
        fig_path = os.path.join(analysis_dir, f'{titles[i-1]}.png')
        if os.path.exists(fig_path):
            os.remove(fig_path)  # remove the file if it already exists
        fig.savefig(fig_path)
        close()
        
    minfo = {
        'N Elements': [len(df['Element'].unique())],
        'N Nodes':  [len(df['Node'].unique())]
    }
    return minfo, data


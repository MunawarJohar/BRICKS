import os
import re
from datetime import datetime

from .process import *
from .plots import plot_results

def model_convergence(dir,multiple = False):
    """
    This function prompts the user to enter the full path of a .OUT file,
    reads the file, parses the lines, and plots the results.

    Args:
        None

    Returns:
        None
    """
    if multiple:
        iter = {}
        ncsteps = []
        out_files = get_files(dir, '.out')
        for phase,item in enumerate(out_files):
            lines = read_file(item)
            iterations, noconvergencesteps = parse_lines(lines, phase+1 )
            iter.update(iterations)
            ncsteps += noconvergencesteps

    else:
        out_files = get_files(dir, '.out')
        lines = read_file(out_files)
        iter, ncsteps = parse_lines(lines)
    
    figures = plot_results(iter, ncsteps)
    return figures

def single_model_analysis(directory, filename):
    # Perform the analysis
    figures = convergence_analysis(filename)

    # Create a new directory called 'analysis' in the current directory if not exists
    analysis_dir = os.path.join(directory, 'analysis')
    os.makedirs(analysis_dir, exist_ok=True)

    # Save the figures in the 'analysis' directory
    for i, fig in enumerate(figures, start=1):
        fig_path = os.path.join(analysis_dir, f'Convergence_figure_{i}.png')
        if os.path.exists(fig_path):
            os.remove(fig_path)  # remove the file if it already exists
        fig.savefig(fig_path)

    # Save some information in a txt file in the 'analysis' directory
    info_path = os.path.join(analysis_dir, 'info.txt')
    if os.path.exists(info_path):
        os.remove(info_path)  # remove the file if it already exists
    with open(info_path, 'w') as f:
        model_info = model_info(filename,directory)
        write_to_txt(directory,'model_data', model_info)

def main(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.OUT'):
                single_model_analysis(root, os.path.join(root, file))


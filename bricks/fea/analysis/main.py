import os

from .processing.main import *
from .plots.plots import plot_combined

def analyse_models(modelling_directory, analysis_info=None, plot_settings=None, **kwargs):
    
    """
    Analyzes model files in the specified directory by first processing `.tb` files
    and then `.out` files. The function collects information from the `.tb` files 
    and uses it for the analysis of the `.out` files. It handles any errors encountered
    during processing and logs the failed files.

    Parameters:
    -----------
    modelling_directory : str
        The path to the directory containing the model files to be analyzed.
    analysis_info : dict, optional
        Additional information for the analysis. This parameter is passed to the 
        `single_tb_analysis` function.
    plot_settings : dict, optional
        Settings for plotting. This parameter is passed to the `single_tb_analysis` function.

    Returns:
    --------
    list
        A list of file paths that could not be processed due to errors.

    Notes:
    ------
    - The function processes `.tb` files first to gather necessary information before
      processing `.out` files.
    - If an error occurs while processing a file, the file path is added to the `failed_files`
      list and an error message is printed.
    - The `minfo` dictionary, obtained from `.tb` files, is used in the analysis of `.out` files.

    Examples:
    ---------
    >>> failed_files = analyse_models("/path/to/modelling_directory")
    >>> if failed_files:
    >>>     print("The following files could not be processed:")
    >>>     for failed_file in failed_files:
    >>>         print(failed_file)
    """
    failed_files = []

    tb_files = []
    out_files = []
    data_l = []
    # Separate .tb .out files
    for root, _, files in os.walk(modelling_directory):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith('.tb'):
                tb_files.append(file_path)
            elif file.endswith('.out'):
                out_files.append(file_path)

    # Process .tb files first
    for file_path in tb_files:
        try:
            minfo, data = single_tb_analysis(file_path, analysis_info, plot_settings)
            data_l.append(data)
        except Exception as e:
            failed_files.append(file_path)
            print(f"Error processing file {file_path}: {e}")

    # Process .out files
    for file_path in out_files:
        try:
            merge = kwargs.get('merge', False)
            single_out_analysis(file_path,minfo, merge=merge)
        except Exception as e:
            failed_files.append(file_path)
            print(f"Error processing file {file_path}: {e}")
    
    if failed_files:
        print("\nThe following files could not be processed:")
        for failed_file in failed_files:
            print(failed_file)

    return data_l

def compare_models(plot_data_list):
    """
    Plot the analysis results and merge the plots for different plot types from multiple models.

    Args:
        plot_data_list (list): List of dictionaries, each containing the analysis info, plot settings, and data directory for a model.

    Returns:
        list: A list of matplotlib figure objects representing the combined plots for each type of analysis.
    """
    combined_figures = {}

    # Analyze data for each model in the list
    for plot_data in plot_data_list:
        minfo, data_analysis = single_tb_analysis(plot_data['dir'], plot_data['analysis_info'], plot_data['plot_settings'])
        plot_data['minfo'] = minfo
        plot_data['data_analysis'] = data_analysis

    # Iterate over all possible analysis info keys
    for plot_key in plot_data_list[0]['analysis_info'].keys():
        
        fig = plot_combined(plot_data_list, plot_key)
        combined_figures[plot_key] = fig

    return combined_figures
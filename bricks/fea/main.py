import os

from .analysis.tabulated import single_tb_analysis
from .analysis.out import single_out_analysis

def analyse_models(modelling_directory, analysis_info=None, plot_settings=None):
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
            minfo = single_tb_analysis(file_path, analysis_info, plot_settings)
        except Exception as e:
            failed_files.append(file_path)
            print(f"Error processing file {file_path}: {e}")

    # Process .out files
    for file_path in out_files:
        try:
            single_out_analysis(file_path,minfo)
        except Exception as e:
            failed_files.append(file_path)
            print(f"Error processing file {file_path}: {e}")
    
    if failed_files:
        print("\nThe following files could not be processed:")
        for failed_file in failed_files:
            print(failed_file)

    return failed_files
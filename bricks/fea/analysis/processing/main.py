from .out import *
from .tabulated import *
from .utils import *
from ..plots.plots import plot_analysis

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
                        c_w = compute_damage_parameter_manual(df, crack_set)
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

def single_out_analysis(file_path,minfo, **kwargs):
    
    directory = os.path.dirname(file_path)
    analysis_dir = os.path.join(directory, 'analysis/convergence')
    os.makedirs(analysis_dir, exist_ok=True)

    # Write model information
    minfo_ = model_info(file_path,directory)
    minfo.update(minfo_)
    
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

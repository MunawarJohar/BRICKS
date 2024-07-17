import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

from .style import *

def plotconvergence(iterations, noconvergencesteps, minfo):
    """
    Plot the results of the analysis.

    Args:
        iterations (dict): A dictionary containing the analysis results for each phase.
            The keys are the phase names and the values are dictionaries containing the analysis data.
        noconvergencesteps (list): A list of steps where no convergence was achieved.

    Returns:
        None

    Prints the phases analyzed up to the last one in the `iterations` dictionary,
    the number of no convergence steps found, and the titles of the plots.

    For each phase in the `iterations` dictionary, plots the analysis data using matplotlib.
    The type of plot and the data to be plotted depend on the keys and values in the phase dictionary.
    """
    figures = []
    figures_titles = []
    axes = []
    ylabels = [
        "Nº of plastic IP's", "Nº of cracks $n_c$",
        "Nº of solver iterations $n_{iter}$", r"Force norm $|\Delta_f|$",
        r"Displacement norm $|\Delta_u|$", r"Energy norm $|\Delta_E|$"
    ]
    
    titles = [
        "Plastic integration points", "Crack progression",
        "Solver iteration steps", "Force norm",
        "Displacement norm", "Energy norm"
    ]

    traces = [
        "PIP's", "Nº Cracks", "Converged steps",
        "Force norm", "Displacement norm", "Energy norm"
    ]

    first_phase_key = next(iter(iterations))
    for item_count, (key, items) in enumerate(iterations[first_phase_key].items()):
        if not items or not isinstance(items, list):
            continue

        fig, ax = plt.subplots(figsize=(5, 3))
        figures.append(fig)
        axes.append(ax)
        title = titles[item_count]
        figures_titles.append(title)  # Append the corresponding title

        for phase in iterations:
            phase_data = iterations[phase]
            disp_limit = phase_data.get("disp_limit")
            force_limit = phase_data.get("force_limit")
            energy_limit = phase_data.get("energy_limit")

            x_max = len(items)
            load_factor = np.arange(1, len(items) + 1)/x_max

            if key in ["Plastic_int", "Crack_points"]:
                y = [items[0]] + [items[j] - items[j - 1] for j in range(1, len(items))]
            else:
                y = items

            ax.plot(load_factor, y, label=traces[item_count], 
                    marker='s', markerfacecolor='none')
            
            if title == "Solver iteration steps":
                ax.plot(
                    [noconvergencesteps[i]/x_max for i in range(len(noconvergencesteps))],
                    [y[i-1] for i in noconvergencesteps],
                    linewidth=0.5, markersize=3, marker='s', markerfacecolor='none', linestyle='None',
                    label='Non-converged steps', color = 'red'
                )
                ax.legend(loc='best')
                plt.ylim(0, max(y) * 1.3)

            y_lim = None
            legend_labels = []
            if key == "disp_norm" and disp_limit is not None:
                y_lim = np.full((len(items)), disp_limit)
                legend_labels = ["Disp variation", "Disp Tolerance"]
            elif key == "force_norm" and force_limit is not None:
                y_lim = np.full((len(items)), force_limit)
                legend_labels = ["Out of Balance Force", "Force Tolerance"]
            elif key == "energy_norm" and energy_limit is not None:
                y_lim = np.full((len(items)), energy_limit)
                legend_labels = ["Energy Variation", "Energy Tolerance"]
            if y_lim is not None:
                ax.plot(load_factor, y_lim, "-", label='Out of balance threshold', linewidth=0.5, color = 'red')
                ax.legend(legend_labels, loc='best')
                y_max = max(max(y_lim),np.max(y))
                plt.ylim(0, y_max * 1.3)
            ax.annotate(f"Model: {minfo['Model'][0]}\nSolution time: {minfo['Run time'][0]} [hh:mm:ss]\nNº Elements: {str(minfo['N Elements'][0])}  Nº Nodes: {str(minfo['N Nodes'][0])}",
                    xy=(0.04, 0.96), xycoords='axes fraction',  
                    va='top', ha='left', fontsize=8, color='black',
                    bbox=dict(facecolor='white', edgecolor='none', alpha=0.7),
                    annotation_clip=True  
                )

        ax.set_xlabel(r'Load factor $\lambda$')
        ax.set_ylabel(ylabels[item_count])
        
    return figures, figures_titles, axes

def merge_plots(figures_titles, axes, indices_to_merge, x_label, y_label, title):
    """
    Merge specific plots into one plot.

    Args:
        figures (list): List of figure objects.
        figures_titles (list): List of figure titles.
        axes (list): List of axes objects.
        indices_to_merge (list): List of indices of the plots to merge.
        x_label (str): Label for the x-axis.
        y_label (str): Label for the y-axis.
        title (str): Title for the merged plot.

    Returns:
        merged_fig (Figure): The merged figure object.
    """
    merged_fig, merged_ax = plt.subplots(figsize=(5, 3))
    
    for index in indices_to_merge:
        original_ax = axes[index]
        lines = original_ax.get_lines()
        for line in lines:
            if 'threshold' in line.get_label():
                merged_ax.plot(line.get_xdata(), line.get_ydata(), label=f"{figures_titles[index]}: {line.get_label()}",
                               color = line.get_color(), linestyle = line.get_linestyle())
            else:
                merged_ax.plot(line.get_xdata(), line.get_ydata(), label=f"{figures_titles[index]}: {line.get_label()}")

    merged_ax.set_xlabel(x_label)
    merged_ax.set_ylabel(y_label)
    merged_ax.set_title(title)
    merged_ax.legend(loc='best')
    
    return merged_fig

def add_shaded_areas_cw(ax, max_y):
    DL = [0, 1, 2, 3, 4, 5]
    Name = ['Negligible', 'Very slight', 'Slight', 'Moderate', 'Severe', 'Very severe']
    CW = [0, 1, 5, 15, 25, max(25, max_y)]
    
    for i in range(len(CW) - 1):
        if CW[i] < max_y:
            upper_limit = min(CW[i + 1], max_y*1.1)
            alpha_value = 0.03 + 0.04 * i 
            ax.axhspan(CW[i], upper_limit, facecolor='gray', alpha=alpha_value)
            ax.text(ax.get_xlim()[1], (CW[i] + upper_limit) / 2, f'DL{DL[i]} {Name[i]}',
                    va='center', ha='right', fontsize=8, color='black',
                    bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))
    
    # Set y-axis upper limit to ensure all annotations are visible
    current_ylim = ax.get_ylim()
    ax.set_ylim(current_ylim[0], max_y * 1.1)
            
def add_shaded_areas_psi(ax, max_psi):
    psilim = [0, 1, 1.5, 2.5, 3.5, float('inf')]
    DL = [0, 1, 2, 3, 4, 5]
    Name = ['Negligible', 'Very slight', 'Slight', 'Moderate', 'Severe', 'Very severe']
    
    for i in range(len(psilim) - 1):
        if psilim[i] < max_psi:
            upper_limit = min(psilim[i + 1], max_psi*1.1)
            alpha_value = 0.03 + 0.04 * i 
            ax.axhspan(psilim[i], upper_limit, facecolor='gray', alpha=alpha_value)
            ax.text(ax.get_xlim()[1], (psilim[i] + upper_limit) / 2, f'DL{DL[i]} {Name[i]}',
                    va='center', ha='right', fontsize=8, color='black',
                    bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))
    
    current_ylim = ax.get_ylim()
    ax.set_ylim(current_ylim[0], max_psi * 1.1)

def plotanalysis(data, analysis_info, plot_settings):
    """
    Plot the analysis results based on the provided data.

    Args:
        data (list of DataFrames): The data to be plotted. Each DataFrame should represent a specific trace.
        **kwargs: Additional settings for the plot and analysis information. Supported keys include:
            - analysis_info (dict, optional): Additional information for analysis. It should be a dictionary with the following keys:
                - 'plot_type' (list): A list of plot types to be generated.
                - 'Node Nr' (list): A list of the nodes to include in the analysis.
            - plot_settings (dict, optional): Additional settings for the plot. It should be a dictionary with the following keys:
                - 'traces' (list or str): A list of trace names for each variable or a single trace name for all variables.
                - 'labels' (list): A list of labels for the x-axis and y-axis.
                - 'titles' (str): A title for the plot.
                - 'scientific' (bool): Whether to use scientific notation for the y-axis.

    Returns:
        list: A list of matplotlib figure objects representing the generated plots.
        list: A list of titles for the generated plots.
    """
    figures = []
    figures_titles = []

    for plot_key, info in analysis_info.items():
        fig, ax = plt.subplots(figsize=(5, 3))
        figures.append(fig)
        figures_titles.append(plot_settings[plot_key]['titles'])

        if 'Crack' in plot_key:  # Crack width development plot
            max_y = max([data[plot_key][i][data[plot_key][i].columns[1]].max() 
                         for i in range(len(plot_settings[plot_key].get('traces', [])))])
            add_shaded_areas_cw(ax, max_y)
        
        if 'Damage' in plot_key:  # Damage development plot
            max_psi = 0
            for vals in data[plot_key]:
                max_psi = max(max_psi, vals['psi'].max())
            add_shaded_areas_psi(ax, max_psi)
        
        if 'Mutual' in plot_key:
            max_ = 0
            for i,vals in enumerate(data[plot_key]): 
                max_ = max(max_, abs(data['Mutual'][i]).max().max())
                data[plot_key][i] *=  -1
            vals = np.linspace(0,max_,10)
            ax.plot(vals,vals, linestyle=':', label = 'Equality')

        plot_traces(ax, data, plot_settings, plot_key)

    if not analysis_info:  # Individual analysis
        fig, ax, _ = individual_plot(data, plot_settings)
        
    return figures, figures_titles

def plot_traces(ax, data, plot_settings, plot_key):
    """
    Plot traces on the given axes with specified plot settings.

    Parameters:
    - ax: The matplotlib axes object.
    - data: The data dictionary containing DataFrames.
    - plot_settings: The dictionary containing plot settings.
    - plot_key: The specific key in plot_settings to access settings for the current plot.
    """
    for i, trace in enumerate(plot_settings[plot_key].get('traces', [])):
        x_val = data[plot_key][i][data[plot_key][i].columns[0]].values
        if x_val.min() >= 1:  # In terms of load factor or not
            x_val = np.arange(1, len(x_val) + 1) / max(x_val)
        y_val = data[plot_key][i][data[plot_key][i].columns[1]].values
        ax.plot(x_val, y_val, label=trace, marker=None)

    if 'labels' in plot_settings[plot_key]:
        ax.set_xlabel(plot_settings[plot_key]['labels'][0])
        ax.set_ylabel(plot_settings[plot_key]['labels'][1])

    cond = True if abs(y_val).max() > 1e3 else False
    if plot_settings[plot_key].get('scientific', False) and cond:
        ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))

    ax.legend(loc='best')

def individual_plot(data, plot_settings):
    """
    Plot the given data with the specified plot settings.

    Parameters:
    - data: numpy array, where each column represents a variable and each row represents a data point.
    - plot_settings: dict, contains settings for the plot including labels, title, scientific notation, and traces.

    Returns:
    - fig: The matplotlib figure object.
    - ax: The matplotlib axes object.
    - title: The title of the plot, if specified.
    """
    fig, ax = plt.subplots(figsize=(6, 4))
    
    x_val = data[:, 0]
    if x_val.min() >= 1:  # In terms of load factor or not
        load_factor = np.arange(1, len(x_val) + 1) / max(x_val)
    else:
        load_factor = data[:, 0]

    if plot_settings:
        if 'labels' in plot_settings:
            x_label, y_label = plot_settings['labels']
            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)

        if 'scientific' in plot_settings and plot_settings['scientific']:
            ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
            ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))  # Use scientific notation

        if 'titles' in plot_settings:
            title = plot_settings['titles']
            ax.set_title(title)
        else:
            title = None

        for i in range(1, data.shape[1]):
            values = data[:, i]
            trace = None
            if 'traces' in plot_settings:
                if isinstance(plot_settings['traces'], list):
                    trace = plot_settings['traces'][i - 1] if i - 1 < len(plot_settings['traces']) else None
                else:
                    trace = plot_settings['traces']

            ax.plot(load_factor, values, '-', label=trace, linewidth=0.5, marker=None)

        if 'traces' in plot_settings:
            ax.legend(loc='best')

    return fig, ax, title

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import scienceplots

plt.style.use(['science', 'ieee'])

def plotConvergence(iterations, noconvergencesteps):
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
    ylabels = [
        "Nº of plastic IP's", "Nº of cracks",
        "Nº of solver iterations", r"Out of balance force norm $|\Delta_f|$",
        r"Out of balance displacement norm $|\Delta_u|$", r"Out of balance energy norm $|\Delta_E|$"
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

    # Get the first key to extract the items
    first_phase_key = next(iter(iterations))

    for item_count, (key, items) in enumerate(iterations[first_phase_key].items()):
        if not items or not isinstance(items, list):
            continue

        fig, ax = plt.subplots(figsize=(6, 4))
        figures.append(fig)
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

            ax.plot(load_factor, y, '-', label=traces[item_count], linewidth=0.5, markersize=2, marker='s', markerfacecolor='none')
            
            if title == "Solver iteration steps":
                ax.plot(
                    [noconvergencesteps[i]/x_max for i in range(len(noconvergencesteps))],
                    [y[i-1] for i in noconvergencesteps],
                    linewidth=0.5, markersize=2, marker='s', markerfacecolor='none', linestyle='None',
                    label='Non-converged steps'
                )
                ax.legend(loc='best')
                plt.ylim(0, max(y) * 1.2)

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
                ax.plot(load_factor, y_lim, "-", label='Out of balance threshold', linewidth=0.5)
                ax.legend(legend_labels, loc='best')
                y_max = max(max(y_lim),np.max(y)) * 1.2
                plt.ylim(0, y_max)

        ax.set_xlabel(r'Load factor $\lambda$')
        ax.set_ylabel(ylabels[item_count])
        
    return figures, figures_titles

def plotAnalysis(data, **kwargs):
    '''
    Plot the analysis results based on the provided data.

    ## Args:
        data (ndarray): The data to be plotted. It should be a 2D array where each column represents a variable and each row represents a data point.
        **kwargs: Additional settings for the plot and analysis information. Supported keys include:
            - analysis_info (dict, optional): Additional information for analysis. It should be a dictionary with the following keys:
                - 'plot_type' (list): A list of plot types to be generated.
                - 'Node Nr' (list): A list of the nodes to include in the analysis.
                - 'Element Nr' (list): A list of the Elements to include in the analysis.
            - plot_settings (dict, optional): Additional settings for the plot. It should be a dictionary with the following keys:
                - 'traces' (list or str): A list of trace names for each variable or a single trace name for all variables.
                - 'labels' (list): A list of labels for the x-axis and y-axis.
                - 'titles' (str): A title for the plot.
                - 'scientific' (bool): Whether to use scientific notation for the y-axis.

    ## Returns:
        list: A list of matplotlib figure objects representing the generated plots.
        list: A list of titles for the generated plots.
    '''
    figures = []
    figures_titles = []

    analysis_info = kwargs.get('analysis_info', None)
    plot_settings = kwargs.get('plot_settings', None)

    if analysis_info:  # Analysis from processing of tabulated data
        for plot_type in analysis_info['plot_type']:
            fig, ax = plt.subplots(figsize=(6, 4))
            figures.append(fig)
            figures_titles.append(analysis_info['plot_type'][plot_type]['titles'][0])
            
            for trace in analysis_info['plot_type'][plot_type]['trace_list']:
                x_val = data[:, 0]
                if x_val.min() < 0:
                    load_factor = np.arange(1, len(x_val) + 1) / max(x_val)
                else:
                    load_factor = data[:, 0]

                values = data[:, 1:]
                ax.plot(load_factor, values, '-', linewidth=0.5, markersize=2, marker='s', markerfacecolor='none')
                ax.legend(loc='best')
                ax.set_xlabel(analysis_info['plot_type'][plot_type]['labels'][0])
                ax.set_ylabel(analysis_info['plot_type'][plot_type]['labels'][1])
                ax.set_title(analysis_info['plot_type'][plot_type]['titles'][0])

    if not analysis_info:  # Individual analysis
        fig, ax = plt.subplots(figsize=(6, 4))
        figures.append(fig)

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
                figures_titles.append(title)
            
            for i in range(1, data.shape[1]):
                values = data[:, i]
                trace = None
                if 'traces' in plot_settings:
                    if isinstance(plot_settings['traces'], list):
                        trace = plot_settings['traces'][i - 1] if i - 1 < len(plot_settings['traces']) else None
                    else:
                        trace = plot_settings['traces']

                ax.plot(load_factor, values, '-', label=trace, linewidth=0.5, markerfacecolor='none')

            if 'traces' in plot_settings:
                #title = plot_settings['traces'].split()[1].capitalize() 
                ax.legend(loc='best')

    return figures

            
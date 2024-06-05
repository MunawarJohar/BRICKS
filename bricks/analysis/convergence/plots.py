import numpy as np
import matplotlib.pyplot as plt
import scienceplots

plt.style.use(['science','ieee'])

def plot_results(iterations, noconvergencesteps):
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
    ylabel = ["Total number of plastic IPs", "Total number of cracks", "Number of Iterations", "Out of balance norm", "Out of balance norm", "Out of balance norm"]
    title = ["Number of plastic integration points", "Crack progression plot", "Number of iterations", "Force norm", "Displacement norm", "Energy norm"]

    # Get the first key to extract the items
    first_phase_key = next(iter(iterations))

    for item_count, (key, items) in enumerate(iterations[first_phase_key].items()):
        if not items or not isinstance(items, list):
            continue

        fig, ax = plt.subplots()
        figures.append(fig)
        
        for i,phase in enumerate(iterations):
            phase_data = iterations[phase]
            disp_limit = phase_data.get("disp_limit")
            force_limit = phase_data.get("force_limit")
            energy_limit = phase_data.get("energy_limit")
            
            x = np.arange(1, len(items) + 1)

            if key == "Plastic_int" or key == "Crack_points":
                y = [items[0]] + [items[j] - items[j-1] for j in range(1, len(items))]
            else:
                y = items

            ax.plot(x, y, '.-', label=f'LC {i+1}')
            if key == "disp_norm" and disp_limit is not None:
                y_lim = np.full((len(items)), disp_limit)
                ax.plot(x, y_lim, "-")
                ax.legend(["Disp variation", "Disp Tolerance"])
            elif key == "force_norm" and force_limit is not None:
                y_lim = np.full((len(items)), force_limit)
                ax.plot(x, y_lim, "-")
                ax.legend(["Out of Balance Force", "Force Tolerance"])
            elif key == "energy_norm" and energy_limit is not None:
                y_lim = np.full((len(items)), energy_limit)
                ax.plot(x, y_lim, "-")
                ax.legend(["Energy Variation", "Energy Tolerance"])

        ax.set_title(title[item_count])
        ax.set_xlabel('Load step')
        ax.set_ylabel(ylabel[item_count])
        ax.legend()

    plt.show()
    return figures

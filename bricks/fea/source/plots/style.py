import matplotlib.pyplot as plt
from itertools import product
from cycler import cycler
from random import shuffle
import scienceplots

plt.style.use(['science', 'ieee'])

# Set random default combination of traces
colors = ['black', '#333333', '#292929']
line_styles = ['solid', 'dashed', 'dashdot']
markers = ['o', 's', '+', 'D', 'x']

combinations = list(product(colors, line_styles))
#shuffle(combinations)
shuffled_colors, shuffled_lines = zip(*combinations)
custom_cycler = (cycler(color=shuffled_colors) +
                 cycler(linestyle=shuffled_lines))

plt.rcParams.update({
    'text.usetex': True,
    'font.family': 'sans-serif',  
    'font.serif': ['Arial'],
    'axes.prop_cycle': custom_cycler,
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'xtick.minor.size': 0,
    'ytick.minor.size': 0,
    'axes.grid': False,
    'lines.linewidth': 0.7 ,
    'axes.labelcolor': '#333333',  
    'axes.labelweight': 'semibold',
    'xtick.labelcolor': '#333333',  
    'ytick.labelcolor': '#333333',   
    'axes.titlecolor': '#333333',   
})
import matplotlib.pyplot as plt
from itertools import product
from cycler import cycler
from random import shuffle
import scienceplots

plt.style.use(['science', 'ieee'])

# Define initial colors, line styles, and markers
colors = ['#333333','#5F5F5F']
extra_colors = ['#0C2340', '#00A6D6','#FFFF99' ,'#A50034', '#0076C2']  # Additional colors
line_styles = ['solid', 'dashed', 'dashdot']
markers = ['o', 's', '+', 'D', 'x']

# Create the initial combinations
combinations = list(product(colors, line_styles))

# In case all initial combinations are used
extended_combinations = combinations + list(product(extra_colors, line_styles))

shuffled_colors, shuffled_lines = zip(*extended_combinations)
custom_cycler = (cycler(color=shuffled_colors) + cycler(linestyle=shuffled_lines))


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
    'lines.linewidth': 0.5 ,
    'lines.markersize': 2,
    'lines.markeredgewidth': 0.5, 
    'axes.labelcolor': '#333333',  
    'axes.labelweight': 'semibold',
    'xtick.labelcolor': '#333333',  
    'ytick.labelcolor': '#333333',   
    'axes.titlecolor': '#333333',   
})
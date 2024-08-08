import matplotlib.pyplot as plt
from itertools import product
from cycler import cycler

import scienceplots

plt.style.use(['science', 'ieee'])

# plt.rcParams.update({
#     'figure.figsize': (5, 3),
#     'figure.dpi': 600,
#     'figure.autolayout': True,
    
#     # Font Settings
#     'font.size': 8,
#     'font.family': 'sans-serif',
#     'font.serif': ['Arial'],  
    
#     # Color Line Style Settings
#     'lines.linewidth': 0.5,
#     'lines.markersize': 2,
#     'lines.markeredgewidth': 0.5,
#     'axes.labelweight': 'semibold',
#     'axes.labelcolor': '#333333',
#     'xtick.labelcolor': '#333333',
#     'ytick.labelcolor': '#333333',
#     'axes.titlecolor': '#333333',
    
#     # Grid and Ticks
#     'axes.grid': False,
#     'xtick.direction': 'in',
#     'ytick.direction': 'in',
#     'xtick.minor.size': 0,
#     'ytick.minor.size': 0,
    
#     # Legend Settings
#     'legend.frameon': False,
#     'legend.framealpha': 0.7,
#     'legend.fancybox': False,
#     'legend.numpoints': 1,
    
#     # Saving Figures
#     'savefig.bbox': 'tight',
#     'savefig.pad_inches': 0.05,
    
#     # LaTeX Settings 
#     'text.usetex': True,
#     #'text.latex.preamble': r'\usepackage{amsmath} \usepackage{amssymb} \usepackage{sfmath}',
#     'mathtext.fontset': 'dejavusans',
# })

plt.rcParams.update({
    'text.usetex': True,
    'font.family': 'sans-serif',  
    'font.serif': ['Arial'],
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


# Custom color and linestyle cycler
colors = ['#333333', '#5F5F5F', '#999999', '#B0B0B0']
line_styles = ['solid', 'dashed', 'dashdot', 'dotted']
extra_line_styles = ['dashed', 'dashdot', 'dotted', (0, (5, 10)), (0, (3, 5, 1, 5))]

combinations = list(product(colors, line_styles))
extended_combinations = combinations + list(product(colors, extra_line_styles))
shuffled_colors, shuffled_lines = zip(*extended_combinations)
custom_cycler = cycler(color=shuffled_colors) + cycler(linestyle=shuffled_lines)

plt.rcParams['axes.prop_cycle'] = custom_cycler

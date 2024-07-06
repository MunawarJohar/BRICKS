from .plots.plots import plotconvergence, plotanalysis
from .analysis.tabulated import analyse_tabulated

def analysis(df, analysis_info, plot_settings):

    data = analyse_tabulated(df, analysis_info)
    figures, _ = plotanalysis(data, analysis_info, plot_settings)

    return figures
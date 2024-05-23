import numpy as np
from dash import Dash, dcc, html
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.colors import get_colorscale

from ..utils import prepare_report, compute_param, get_color_from_scale

def LTSM_plot(object):
    house = object.house
    app = Dash(__name__)
    
    assess_types = list(object.assessment['ltsm'].keys())
    all_assessment_tabs = []

    tab_style = {'fontFamily': 'Arial, sans-serif', 'color': '#3a4d6b'}
    
    for assessment in assess_types:
        try:
            figs = []
            wltsm = object.assessment['ltsm'][assessment]
            for i, wall in enumerate(house):
                # ---------------------------------- Process --------------------------------- #
                h = object.house[wall]['height']
                int = object.process['int'][wall]

                strain = wltsm['results'][wall]['e_tot']
                if assessment == 'greenfield':
                    ltsm_params = wltsm['variables'][wall]
                    ltsm_values = wltsm['values'][wall]

                param = [ltsm_params, ltsm_values]
                for dict_ in param:
                    for key, value in dict_.items():
                        globals()[key] = value

                # ---------------------------------- Display --------------------------------- #
                fig = make_subplots(rows=2, cols=1,
                                    vertical_spacing=0.1,
                                    shared_xaxes=True,
                                    shared_yaxes=True,
                                    x_title='Length [m]',
                                    y_title='Profile & Height [mm]',
                                    subplot_titles=('Relative Wall position', 'Subsidence profile'))

                # -------------------- Custom measurements functionalities ------------------- #
                if assessment == 'measurements':
                    z_measurement = int["z_lin"]
                    x_measurement = int["ax_rel"]
                    fig.add_trace(go.Scatter(x=x_measurement,
                                            y= z_measurement,
                                            mode='lines',
                                            name='Subsidence profile'),
                                row=2, col=1)
                    
                    infl_list = object.soil['shape'][wall]['gradient_inflection_coord']
                    for infl in infl_list:
                        fig.add_trace(go.Scatter(x= [infl,infl], y=[0, h], mode='lines', name='Inflection point',
                                                line=dict(color='black', width=1, dash='dash')), row=1, col=1)

                        fig.add_trace(go.Scatter(x= [infl,infl], y=[min(z_measurement), max(z_measurement)], mode='lines', name='Inflection point',
                                                line=dict(color='black', width=1, dash='dash')), row=2, col=1)

                # --------------------- Custom greenfield functionalities -------------------- #
                if assessment == 'greenfield':
                    fig.add_trace(go.Scatter(x=x,
                                            y=w,
                                            mode='lines',
                                            name='Gaussian profile approximation'),
                                row=2, col=1)
                    
                    # Inflection traces
                    for z in [-xinflection, xinflection]:
                        fig.add_trace(go.Scatter(x=[z, z], y=[0, h], mode='lines', name='Inflection point',
                                                line=dict(color='black', width=1, dash='dash')), row=1, col=1)

                        fig.add_trace(go.Scatter(x=[z, z], y=[w.min(), w.max()], mode='lines', name='Inflection point',
                                                line=dict(color='black', width=1, dash='dash')), row=2, col=1)

                    for influence in [-xlimit, xlimit]:
                        fig.add_trace(go.Scatter(x=[influence, influence], y=[0, h], mode='lines', name='Influence area',
                                                line=dict(color='black', width=1, dash='dashdot')), row=1, col=1)

                        fig.add_trace(go.Scatter(x=[influence, influence], y=[w.min(), w.max()], mode='lines', name='Influence area',
                                                line=dict(color='black', width=1, dash='dashdot')), row=2, col=1)
                    fig.add_trace(go.Scatter(x=x,
                                            y=np.full(len(x), limitline),
                                            mode='lines', name=f'Limit Line [{limitline} mm]',
                                            line=dict(color='black', dash='dash', width=1)),
                                row=2, col=1)

                # -------------------------- Evaluation and building ------------------------- #
                if i % 2 == 0:  # Wall is along the y axis
                    xi = object.house[wall]['y'].max()
                    xj = object.house[wall]['y'].min()
                else:
                    xi = object.house[wall]['x'].max()
                    xj = object.house[wall]['x'].min()
                
                # Plot wall shape
                if object.assessment['ltsm'][assessment]['report']:
                    report = object.assessment['ltsm'][assessment]['report']
                    data_matrix, wall_param_labels, sources, description_annotations = prepare_report(report, wall)
                    
                    comments = description_annotations[0]
                    assessments = data_matrix.flatten()
                    
                    colorscale = 'RdYlGn_r'
                    colors = get_colorscale(colorscale)
                    dlmax = 5 ## Find better way than hard coding
                    color_matrix = [get_color_from_scale(damage, colors, dlmax) for damage in assessments]
                    segment_width = (xi - xj) / len(assessments)

                    for i, (color, assess_i, comment,source) in enumerate(zip(color_matrix, assessments, comments,sources)):
                        fig.add_shape(
                            type="rect",
                            x0= i * segment_width,
                            y0= 0 ,
                            x1= (i + 1) * segment_width,
                            y1=h,
                            fillcolor= color[1],
                            opacity=0.7,
                            line=dict(width=0),  # Remove borders if not needed
                            row=1, col=1
                        )
                        fig.add_trace(go.Scatter(
                            x=[(i + 0.5) * segment_width],
                            y=[h / 2],
                            text=f"Assessment: {source}<br>DL: {assess_i}<br>Comment: {comment}",
                            mode='markers',
                            showlegend=False,
                            marker=dict(size=0.1, color='rgba(0,0,0,0)'),
                            hoverinfo='text'
                        ))
                    
                    fig.add_shape(type="rect",
                                    x0=0,
                                    y0=0,
                                    x1=xi - xj,
                                    y1=h,
                                    fillcolor='rgba(49,50,51,0)',  # No fill color
                                    line=dict(color='black', width=2),  # Black border with width 2
                                    row=1, col=1)

                else:          
                    try: # Use Boscardin & Cording (1989) if no report exists
                        ecolor, cat = compute_param(strain)
                    except: # If assessment has been tampered place grey
                        ecolor = 'rgba(49,50,51,0)'
                        cat = 'No assessment'
                    fig.add_shape(
                    type="rect",
                    x0= 0, y0=0,
                    x1=xi - xj, y1=h,
                    fillcolor=ecolor,
                    row=1, col=1 )
                
                ind = np.argmax(assessments)
                cat = comments[ind]
                fig.update_layout(title=f'LTSM {wall} | e_tot = {strain:.2e} DL = {cat}',
                                legend=dict(traceorder="normal"),
                                template='plotly_white')
                # Suppose 'condition' is your condition

                if assessment == 'measurements':
                    valr2 = x_measurement.max() * 1.5 
                    x_range = [-valr2, valr2]
                    
                    fig.update_xaxes(range= x_range, row=1, col=1)
                    fig.update_xaxes(range= x_range, row=2, col=1)

                # Remove duplicate legend labels
                names = set()
                fig.for_each_trace(
                    lambda trace:
                    trace.update(showlegend=False)
                    if (trace.name in names) else names.add(trace.name))
                figs.append(fig)
        
        except Exception as e: # Dont break individual plots
            print(f'{e} for assessment {assessment}')
            continue

        wall_tabs = [dcc.Tab(label=f"Wall {i+1}", children=[dcc.Graph(figure=fig)], style= tab_style, selected_style= tab_style ) for i, fig in enumerate(figs)]
        assessment_tab = dcc.Tab(label=f"{assessment.capitalize()} assessment", children=[dcc.Tabs(children=wall_tabs)], style=tab_style, selected_style= tab_style)
        all_assessment_tabs.append(assessment_tab)

    app.layout = html.Div([
        dcc.Tabs(children=all_assessment_tabs)
    ])

    return app




















# def LTSM_plot(object):
#     """
#     Generates a Dash app with tabs for different LTSM assessments and wall plots.

#     Parameters:
#     object (Object): An object containing house data and LTSM assessment results.

#     Returns:
#     Dash app: A Dash app instance with the generated plots.
#     """
    
#     def process_ltsm_results(wltsm, wall, assessment):
#         """
#         Process LTSM results for a given wall and assessment type.
        
#         Parameters:
#         wltsm (dict): LTSM results for the given assessment.
#         wall (str): Wall identifier.
#         assessment (str): Type of assessment.
        
#         Returns:
#         tuple: Processed parameters and values.
#         """
#         h = object.house[wall]['height']
#         strain = wltsm['results'][wall]['e_tot']
        
#         if assessment == 'greenfield':
#             ltsm_params = wltsm['variables'][wall]
#             ltsm_values = wltsm['values'][wall]
#         else:
#             ltsm_params, ltsm_values = {}, {}

#         return h, strain, ltsm_params, ltsm_values

#     def create_plot(wall, h, strain, ltsm_params, ltsm_values, assessment):
#         """
#         Create a plotly figure for the given wall and assessment type.

#         Parameters:
#         wall (str): Wall identifier.
#         h (float): Height of the wall.
#         strain (float): Strain value.
#         ltsm_params (dict): LTSM parameters.
#         ltsm_values (dict): LTSM values.
#         assessment (str): Type of assessment.

#         Returns:
#         go.Figure: A Plotly figure.
#         """
#         fig = make_subplots(
#             rows=2, cols=1, vertical_spacing=0.1, shared_xaxes=True, 
#             shared_yaxes=True, x_title='Length [m]', y_title='Height [m,mm]',
#             subplot_titles=('Relative Wall position', 'Subsidence profile')
#         )

#         if assessment == 'measurements':
#             int_data = object.process['int'][wall]
#             fig.add_trace(go.Scatter(x=int_data['ax_rel'][::-1], y=int_data["z_lin"], mode='lines', name='Subsidence profile'), row=2, col=1)
        
#         elif assessment == 'greenfield':
#             x = ltsm_params.get('x', [])
#             w = ltsm_params.get('w', [])
#             fig.add_trace(go.Scatter(x=x, y=w, mode='lines', name='Gaussian profile approximation'), row=2, col=1)

#             add_inflection_and_influence_lines(fig, x, w, h, ltsm_values)

#         return fig

#     def add_inflection_and_influence_lines(fig, x, w, h, ltsm_values):
#         """
#         Add inflection and influence lines to the plot.

#         Parameters:
#         fig (go.Figure): The plotly figure to update.
#         x (array): X values for the plot.
#         w (array): W values for the plot.
#         h (float): Height of the wall.
#         ltsm_values (dict): LTSM values.
#         """
#         xinflection = ltsm_values.get('xinflection', 0)
#         xlimit = ltsm_values.get('xlimit', 0)
#         limitline = ltsm_values.get('limitline', 0)

#         for z in [-xinflection, xinflection]:
#             fig.add_trace(go.Scatter(x=[z, z], y=[0, h], mode='lines', name='Inflection point', line=dict(color='black', width=1, dash='dash')), row=1, col=1)
#             fig.add_trace(go.Scatter(x=[z, z], y=[w.min(), w.max()], mode='lines', name='Inflection point', line=dict(color='black', width=1, dash='dash')), row=2, col=1)

#         for influence in [-xlimit, xlimit]:
#             fig.add_trace(go.Scatter(x=[influence, influence], y=[0, h], mode='lines', name='Influence area', line=dict(color='black', width=1, dash='dashdot')), row=1, col=1)
#             fig.add_trace(go.Scatter(x=[influence, influence], y=[w.min(), w.max()], mode='lines', name='Influence area', line=dict(color='black', width=1, dash='dashdot')), row=2, col=1)

#         fig.add_trace(go.Scatter(x=x, y=np.full(len(x), limitline), mode='lines', name=f'Limit Line [{limitline} mm]', line=dict(color='black', dash='dash', width=1)), row=2, col=1)

#     def add_wall_shape(fig, wall, h, strain, assessment):
#         """
#         Add wall shape to the plot based on assessment.

#         Parameters:
#         fig (go.Figure): The plotly figure to update.
#         wall (str): Wall identifier.
#         h (float): Height of the wall.
#         strain (float): Strain value.
#         assessment (str): Type of assessment.
#         """
#         if assessment['report']:
#             report = assessment['report']
#             data_matrix, wall_param_labels, sources, description_annotations = prepare_report(report, wall)

#             comments = description_annotations[0]
#             assessments = data_matrix.flatten()

#             colorscale = 'RdYlGn_r'
#             colors = get_colorscale(colorscale)
#             dlmax = 5
#             color_matrix = [get_color_from_scale(damage, colors, dlmax) for damage in assessments]
#             segment_width = (object.house[wall]['y'].max() - object.house[wall]['y'].min()) / len(assessments)

#             for i, (color, assess_i, comment, source) in enumerate(zip(color_matrix, assessments, comments, sources)):
#                 fig.add_shape(type="rect", x0=i * segment_width, y0=0, x1=(i + 1) * segment_width, y1=h, fillcolor=color[1], line=dict(width=0))
#                 fig.add_trace(go.Scatter(x=[(i + 0.5) * segment_width], y=[h / 2], text=f"Assessment: {source}<br>DL: {assess_i}<br>Comment: {comment}", mode='markers', marker=dict(size=0.1, color='rgba(0,0,0,0)'), hoverinfo='text'))
            
#             ind = np.argmax(assessments)
#             cat = comments[ind]
#         else:
#             ecolor, cat = compute_param(strain)
#             fig.add_shape(type="rect", x0=0, y0=0, x1=object.house[wall]['y'].max() - object.house[wall]['y'].min(), y1=h, fillcolor=ecolor)
        
#         fig.update_layout(title=f'LTSM {wall} | e_tot = {strain:.2e} DL = {cat}', legend=dict(traceorder="normal"), template='plotly_white')
#         remove_duplicate_legend_labels(fig)

#     def remove_duplicate_legend_labels(fig):
#         """
#         Remove duplicate legend labels from the figure.

#         Parameters:
#         fig (go.Figure): The plotly figure to update.
#         """
#         names = set()
#         fig.for_each_trace(lambda trace: trace.update(showlegend=False) if (trace.name in names) else names.add(trace.name))

#     house = object.house
#     app = Dash(__name__)
#     assess_types = list(object.assessment['ltsm'].keys())
#     all_assessment_tabs = []
#     tab_style = {'fontFamily': 'Arial, sans-serif', 'color': '#3a4d6b'}

#     for assessment in assess_types:
#         try:
#             figs = []
#             wltsm = object.assessment['ltsm'][assessment]
#             for wall in house:
#                 h, strain, ltsm_params, ltsm_values = process_ltsm_results(wltsm, wall, assessment)
#                 fig = create_plot(wall, h, strain, ltsm_params, ltsm_values, assessment)
#                 add_wall_shape(fig, wall, h, strain, wltsm)
#                 figs.append(fig)
        
#         except Exception as e:
#             print(f'{e} for assessment {assessment}')
#             continue

#         wall_tabs = [dcc.Tab(label=f"Wall {i+1}", children=[dcc.Graph(figure=fig)], style=tab_style, selected_style=tab_style) for i, fig in enumerate(figs)]
#         assessment_tab = dcc.Tab(label=f"{assessment.capitalize()} assessment", children=[dcc.Tabs(children=wall_tabs)], style=tab_style, selected_style=tab_style)
#         all_assessment_tabs.append(assessment_tab)

#     app.layout = html.Div([dcc.Tabs(children=all_assessment_tabs)])
#     return app
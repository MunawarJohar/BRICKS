import dash
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from dash import dcc
from dash import html
from plotly.subplots import make_subplots

def subsidence(OBJECT):
    house = OBJECT.house
    fig = go.Figure()
    color = ['black','#EC6842','#00B8C8']

    x_mesh, y_mesh, z_lin, z_qint = OBJECT.soil['house'].values()
    z_min = -min(OBJECT.house[wall]["z"].min() for wall in OBJECT.house)/100
    z_rat = z_min / x_mesh.max()
    y_rat = y_mesh.max() / x_mesh.max()

    for i, wall in enumerate(house):
        wall = house[wall]
        if np.all(wall['x'] == wall['x'][0]):  # Wall is along the y axis
            y_lin = np.linspace(wall["y"].min() , wall["y"].max() , 100)
            interp_vals = np.interp(y_lin, wall['y'], wall['z'])
            x = np.full_like(y_lin, wall['x'][0])  # Xcoord constant
            fig.add_trace(go.Scatter3d(x=x, y=y_lin, 
                                    z=interp_vals, 
                                    mode='lines', 
                                    name='Wall',
                                    line = dict(color=color[0])))
            
            fig.add_trace(go.Scatter3d(x=np.full_like(wall['y'], wall['x'][0]), 
                                        y=wall['y'], 
                                        z= wall['z'],
                                        mode='markers', 
                                        marker=dict(size=4, color=color[0]),
                                        showlegend=False))
            #fig.add_trace(go.Scatter3d(x=x, y=y_lin, 
            #                         z= np.zeros_like(interp_vals),
            #                         mode='lines',
            #                         line=dict(color=color[2], dash='dash'),
            #                         showlegend=False))
            
            # fig.add_trace(go.Scatter3d(x=np.full_like(wall['y'], wall['x'][0]), 
            #                             y=wall['y'], 
            #                             z= np.zeros_like(wall['z']),
            #                             mode='markers',
            #                             marker=dict(size=2, color=color[2]),
            #                             showlegend=False))
        else:  # Wall is along the x axis
            x_lin = np.linspace(wall["x"].min() , wall["x"].max() , 100)
            interp_vals = np.interp(x_lin, wall['x'], wall['z'])
            y = np.full_like(x_lin, wall['y'][0])  # Ycoord constant
            fig.add_trace(go.Scatter3d(x=x_lin, 
                                            y=y, 
                                            z=interp_vals, 
                                            mode='lines',
                                            name='Wall',
                                            line = dict(color=color[0])))
            # 
            fig.add_trace(go.Scatter3d(x= wall['x'],
                                            y=np.full_like(wall['x'], 
                                            wall['y'][0]), 
                                            z=wall['z'], 
                                            mode='markers',
                                            marker=dict(size=4, color=color[0]),
                                            showlegend=False))
            # fig.add_trace(go.Scatter3d(x=x_lin, 
            #                                 y=y, 
            #                                 z=np.zeros_like(interp_vals),
            #                                 mode='lines',
            #                                 line=dict(color=color[2], dash='dash'),
            #                                 showlegend=False))
            # fig.add_trace(go.Scatter3d(x= wall['x'],
            #                                 y=np.full_like(wall['x'], 
            #                                 wall['y'][0]), 
            #                                 z= np.zeros_like(wall['z']),
            #                                 mode='markers',
            #                                 marker=dict(size=2, color=color[2]),
            #                                 showlegend=False))
    # --------------------------- plot gaussian shapes --------------------------- #
    x_x =[]
    x_y =[]
    y_x = []
    y_y = []
    for i, wall in enumerate(house):
        wall = house[wall]
        w_param = wall['params']
        
        xnormal = w_param['ax']
        x = w_param['x_gauss']
        svmax = w_param['s_vmax']
        xinflection = w_param['x_inflection']
        z_curr = OBJECT.gaussian_shape(x,svmax,xinflection)

        if i % 2 == 0:  # Wall is along the y axis
            y_y += [xnormal.min(),xnormal.max()]
            y_x += [wall['x'].min()]*2
            x_const = np.full(xnormal.shape[0], wall['x'].min())
            fig.add_trace(go.Scatter3d(x=x_const,
                                            y= xnormal,
                                            z=z_curr,
                                            mode='lines',
                                            name='Approximated subsidence profile',
                                            line=dict(color=color[0], dash='dash')))
        
        else:  # Wall is along the x axis
            x_x += [xnormal.max(),xnormal.min()]
            x_y += [wall['y'].min()]*2
            y_const = np.full(xnormal.shape[0], wall['y'].min())
            fig.add_trace(go.Scatter3d(x= xnormal,
                                        y=y_const,
                                        z=z_curr,
                                        mode='lines',
                                        name='Approximated subsidence profile',
                                        line=dict(color=color[0], dash='dash')))
    # ------------------------------- plot surfaces ------------------------------ #
    fig.add_trace(
        go.Surface(x=x_mesh,
                y=y_mesh, 
                z=z_qint, 
                colorscale='solar', 
                opacity=0.8,
                showscale=False,
                )
    )

    int_soil = OBJECT.soil['soil']
    for key, value in int_soil.items():
        globals()[key] = value

    x = OBJECT.soil['soil']['x']
    y = OBJECT.soil['soil']['y']
    z = OBJECT.soil['soil']['z']

    fig.add_trace(
        go.Surface(x=x, 
                    y=y,
                    z=z,
                    colorscale='blackbody',
                    opacity=0.5,
                    contours = {
                        "z": {"show": True},},
                    showscale=True,
                        ),
    )
    fig.update_layout(
        title='Approximated subsidence surface',
        scene=dict(
            xaxis_title='X [m]',
            yaxis_title='Y [m]',
            zaxis_title='Z [mm]',
            aspectmode="manual",
            aspectratio=dict(x=1*2, y=y_rat*3, z=z_rat*0.8),
        ),
        margin=dict(r=5, b=5, l=5, t=0),  # Adjust the margins as needed
        coloraxis_colorbar=dict(title = 'Disp Uz [mm]', yanchor= "top",x=0.2),
        template = 'plotly_white',
        width = 1800,
        height = 750

    )
    names = set()
    fig.for_each_trace(
        lambda trace:
            trace.update(showlegend=False)
            if (trace.name in names) else names.add(trace.name))
    fig.show()

def compute_param(strain_value):
    colors = ['#BBE3AB', '#FAFAB1', '#DF7E7D']  # Colors corresponding to thresholds
    thresholds = [0.5e-3, 1.67e-3, 3.33e-3]  # Thresholds
    cat = ['Negligible', 'Moderate', 'Severe']  # Categories

    ind = np.argmax([t - strain_value for t in thresholds if t <= strain_value])

    cmap = LinearSegmentedColormap.from_list("", [(0, colors[0]), (0.5, colors[1]), (1, colors[2])])
    normalized_strain = (strain_value - min(thresholds)) / (max(thresholds) - min(thresholds))
    
    rgba_color = cmap(normalized_strain)
    r, g, b, _ = rgba_color  # Extract RGB values from RGBA tuple
    r_int = int(r * 255)  # Convert float to integer in range [0, 255]
    g_int = int(g * 255)
    b_int = int(b * 255)
    hex_color = "#{:02X}{:02X}{:02X}".format(r_int, g_int, b_int)
    return hex_color, cat[ind]
    

def LTSM_plot(OBJECT):        
        house = OBJECT.house
        app = dash.Dash(__name__)
        figs = []
        h = 5
        for wall in house:
            strain = house[wall]['ltsm']['variables']['e_tot']
            ecolor, cat = compute_param(strain)
            ltsm_params = house[wall]['ltsm']['params']
            for key, value in ltsm_params.items():
                globals()[key] = value
            # ----------------------------------- PLOTS ---------------------------------- #
            fig = make_subplots(rows=2, cols=1,
                                vertical_spacing=0.1,
                                shared_xaxes=True,
                                shared_yaxes=True,
                                x_title='Length [m]',
                                y_title='Height [m,mm]',
                                subplot_titles=('Relative Wall position', 'Subsidence profile'))
            fig.add_trace(go.Scatter(x=x, 
                                    y=w, 
                                    mode='lines', 
                                    name='Subsidence profile'), 
                                    row=2, col=1)
            fig.add_trace(go.Scatter(x=x, 
                                    y=np.full(len(x), limitline), 
                                    mode='lines', name=f'Limit Line [{limitline} mm]',
                                    line=dict(color='black', dash='dash', width=1)), 
                                    row=2, col=1)
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
          
            fig.add_shape(
                type="rect",
                x0= 0 , y0=0,
                x1= xj - xi, y1=h,
                fillcolor= ecolor,
                row=1, col=1
            )
            fig.update_layout(title=f'LTSM {wall} | e_tot = {strain:.2e} DL = {cat}',
                            legend=dict(traceorder="normal"), 
                            template='plotly_white')
            # ---------------------- Remove duplicate legend entries --------------------- #
            names = set()
            fig.for_each_trace(
                lambda trace:
                    trace.update(showlegend=False)
                    if (trace.name in names) else names.add(trace.name))
            figs.append(fig)

        tab_heading_style = {
                'fontFamily': 'Arial, sans-serif', 
                'color': '#3a4d6b'  
            }
        tabs_content = [dcc.Tab(label=f"Wall {i+1}", children=[dcc.Graph(figure=figs[i])], style=tab_heading_style, selected_style=tab_heading_style)  for i in range(len(house))]
        app.layout = html.Div([
            dcc.Tabs(children=tabs_content)
        ])

        return app
        
import numpy as np
import dash
from dash import dcc
from dash import html
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from house import gaussian_shape, interpolate_2d

def plot_surface(x_mesh, y_mesh, z_lin, z_qint):

    fig = make_subplots(rows=1, cols=2,
                        specs=[[{'type': 'surface'}, {'type': 'surface'}]],
                        subplot_titles=('Through differential settlements 1st order interpolation', 'Through sagging-hogging soil profile 2nd order interpolation'),
                        )
    
    fig.add_trace(
        go.Surface(x=x_mesh, y=y_mesh, z=z_lin, colorscale='solar', opacity=0.8),
        row=1, col=1
    )
    fig.add_trace(
        go.Surface(x=x_mesh, y=y_mesh, z=z_qint, colorscale='solar', opacity=0.8),
        row=1, col=2
    )

    fig.update_traces(contours_z=dict(show=True, usecolormap=False))
    fig.update_layout(
        scene=dict(
            xaxis=dict(title='X [m]', color='black'),
            yaxis=dict(title='Y [m]',color='black'),
            zaxis=dict(title='Z [mm]',color='black'),
            camera_eye=dict(x=0.5, y=1.2, z=0.4),
            aspectratio=dict(x= 2, y= 3, z= 0.5),
        ),
        scene2=dict(
            xaxis=dict(title='X [m]',color='black'),
            yaxis=dict(title='Y [m]',color='black'),
            zaxis=dict(title='Z [mm]',color='black'),
            camera_eye=dict(x=0.5, y=1.2, z=0.4),
            aspectratio=dict(x= 2, y= 3, z= 0.5),
        ),
        title='Aproximated subsidence surface',
        template='plotly_white',
    )

    fig.show()

def wall_displacement(OBJECT):
    fig = go.Figure()
    colors = ['#3182bd', '#6baed6', '#9ecae1', '#c6dbef', '#eff3ff']  
    line_types = ['solid', 'dash']
    house = OBJECT.house

    for i, wall in enumerate(house):
        color_index = i % len(colors)
        fig.add_trace(go.Scatter(x= house[wall]['int']['ax'], 
                                y= house[wall]['int']["z_lin"], 
                                mode='lines',
                                line=dict(color=colors[color_index], dash=line_types[0]),
                                name=f'Wall {i+1} Linear'))
        fig.add_trace(go.Scatter(x= house[wall]['int']['ax'], 
                                y= house[wall]['int']['z_q'], 
                                mode='lines',
                                line=dict(color=colors[color_index], dash=line_types[1]),
                                name=f'Wall {i+1} Quadratic'))

    fig.update_layout(title='Approximation of Different Walls',
                    xaxis_title='X-Axis',
                    yaxis_title='Z-Axis',
                    legend=dict(x=1.05, y=1, traceorder="normal"), 
                    template='plotly_white',)
    fig.show()


def building_traces(OBJECT):
    
    x_bound = []
    y_bound = []
    wall_val = OBJECT.house.values()

    for wall in wall_val:
        x = np.concatenate([wall['x'], wall['x'][::-1]])   
        x_bound += [wall['x'].min(), wall['x'].max()] 
        x = np.vstack([x,x])

        y = np.concatenate([wall['y'], wall['y'][::-1]])
        y = np.vstack([y,y])
        y_bound += [wall['y'].min(), wall['y'].max()]

        z = np.empty((2,len(wall)))
        z[0,:] = np.full((1,len(wall)), fill_value= 0)
        z[1,:] = np.full((1,len(wall)), fill_value = wall['height'])
        
        x_bound = np.array(x_bound) # Floor and roof
        y_bound = np.array(y_bound)
        z0 = np.zeros(x_bound.shape)
        z1 = np.full(x_bound.shape, wall['height'])
        h = [z0,z1]

        return {'walls': {'x:': x,
                          'y': y,
                          'h': h,},
                'floors': {'x': x_bound,
                           'y': y_bound,
                           'h': h}}

def subsidence(OBJECT, building = False, soil = False, deformation = True) -> go.Figure():
    """
    Plot subsidence data.

    ## Args:
        OBJECT: The object containing the subsidence data.
        building (bool): Whether to plot building data. Default is False.
        soil (bool): Whether to plot soil data. Default is False.
        deformation (bool): Whether to plot deformation data. Default is True.

    ## Returns:
        go.Figure: The plotly figure object.
    """    
    fig = go.Figure()
    x_mesh, y_mesh, z_lin, z_qint = OBJECT.soil['house'].values()

    if deformation: #Plot estimation of measured deformation surface
        
        fig.add_trace(
            go.Surface(x=x_mesh,
                    y=y_mesh, 
                    z=z_qint, 
                    colorscale='solar', 
                    opacity=0.8,
                    showscale=False,)
        )

        house = OBJECT.house  
        color = ['black','#EC6842','#00B8C8']
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
    
    if building:
        # ------------------------------------ FIX ----------------------------------- #
        bwalls, bfloors = building_traces(OBJECT).values()
        x, y, z = bwalls.values()
        x_bound, y_bound, h = bfloors.values()

        wcolor = []
        if OBJECT.dfltsm != None:
            for z in z:strain = house[wall]['ltsm']['variables']['e_tot']
            ecolor, cat = compute_param(strain)
            wcolor.append(ecolor)
            
        fig.add_trace(go.Surface(x=x,
                             y=y,
                             z=z,
                             colorscale=[[0, ecolor], [1, ecolor]],
                             showscale=False))
        for z in h:
            fig.add_trace(go.Surface(x= x_bound,
                                    y= y_bound,
                                    z=z,
                                    colorscale=[[0, 'rgba(0,0,255,0.5)'], [1, 'rgba(0,0,255,0.5)']], 
                                    showscale=False))

    if soil:
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
            z_curr = gaussian_shape(x,svmax,xinflection)

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
    
    

    # ------------------------ Handle plot functionalities ----------------------- #
    z_min = -min(OBJECT.house[wall]["z"].min() for wall in OBJECT.house)/100
    z_rat = z_min / x_mesh.max()
    y_rat = y_mesh.max() / x_mesh.max()

    fig.update_layout(
        title='Approximated subsidence surface',
        scene=dict(
            xaxis_title='X [m]',
            yaxis_title='Y [m]',
            zaxis_title='Z [mm]',
            aspectmode="manual",
            aspectratio=dict(x=1*2, y=y_rat*3, z=z_rat*0.8)
        ),
        coloraxis_colorbar=dict(
            title='Disp Uz [mm]', 
            yanchor="bottom", 
            y=1, 
            x=0,
            len=0.5,  # 70% of the plot area
            ticks="inside"
        ),
        showlegend = False,
        # legend=dict(
        #     yanchor="top",
        #     y=0.3
        # ),
        template='plotly_white'
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


        
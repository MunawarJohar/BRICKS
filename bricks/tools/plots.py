
import numpy as np
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.colors import get_colorscale

from dash import Dash, dcc, html
from plotly.subplots import make_subplots


from .utils import prepare_report, compute_param, get_color_from_scale
from ..assessment.utils import gaussian_shape

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

    return fig

def wall_displacement(OBJECT):
    fig = go.Figure()
    colors = ['#00a6d6', '#A50034', '#FFB81C', '#0076c2', '#EC6842']  
    line_types = ['solid', 'dash']
    process = OBJECT.process

    for i, wall in enumerate(OBJECT.house):
        color_index = i % len(colors)
        fig.add_trace(go.Scatter(x= process['int'][wall]['ax_rel'], 
                                y= process['int'][wall]["z_lin"], 
                                mode='lines',
                                line=dict(color=colors[color_index], dash=line_types[0]),
                                name=f'Wall {i+1} Linear'))
        fig.add_trace(go.Scatter(x= process['int'][wall]['ax_rel'], 
                                y= process['int'][wall]['z_q'], 
                                mode='lines',
                                line=dict(color=colors[color_index], dash=line_types[1]),
                                name=f'Wall {i+1} Quadratic'))

    fig.update_layout(title='Displacement profile of different Walls',
                    xaxis_title='Wall length [m]',
                    yaxis_title='Displacement W[mm]',
                    legend=dict(x=1.05, y=1, traceorder="normal"), 
                    template='plotly_white',)
    return fig

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

def subsidence(OBJECT, building = False, soil = False, deformation = False) -> go.Figure():
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
    
    # if building:
    #     # ------------------------------------ FIX ----------------------------------- #
    #     bwalls, bfloors = building_traces(OBJECT).values()
    #     x, y, z = bwalls.values()
    #     x_bound, y_bound, h = bfloors.values()

    #     wcolor = []
    #     if OBJECT.dfltsm != None:
    #         for z in z:strain = wltsm['results']['e_tot']
    #         ecolor, cat = compute_param(strain)
    #         wcolor.append(ecolor)
            
    #     fig.add_trace(go.Surface(x=x,
    #                          y=y,
    #                          z=z,
    #                          colorscale=[[0, ecolor], [1, ecolor]],
    #                          showscale=False))
    #     for z in h:
    #         fig.add_trace(go.Surface(x= x_bound,
    #                                 y= y_bound,
    #                                 z=z,
    #                                 colorscale=[[0, 'rgba(0,0,255,0.5)'], [1, 'rgba(0,0,255,0.5)']], 
    #                                 showscale=False))

    if soil:
        x_x =[]
        x_y =[]
        y_x = []
        y_y = []
        for i, key in enumerate(house):
            wall = house[key]
            w_param = OBJECT.process['params'][key]
            
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
        template='plotly_white'
    )

    names = set()
    fig.for_each_trace(
        lambda trace:
            trace.update(showlegend=False)
            if (trace.name in names) else names.add(trace.name))
    return fig

def subsurface(ijsselsteinseweg, *params):
    app = Dash(__name__)

    figures_info = [
        ('Wall Displacement', wall_displacement(ijsselsteinseweg)),
        ('Plot Surface', plot_surface(*params)),
        ('Subsidence', subsidence(ijsselsteinseweg, building=False, soil=True, deformation=True))
    ]
    tab_style = {
        'fontFamily': 'Arial, sans-serif',
        'color': '#3a4d6b'
    }

    # Create tabs dynamically
    tabs = [
        dcc.Tab(label=label, children=[
            dcc.Graph(figure=figure),],
            style=tab_style, selected_style= tab_style)
            for label, figure in figures_info
    ]

    app.layout = html.Div([
        dcc.Tabs(tabs)
    ])

    if __name__ == '__main__':
        app.run_server(debug=False)

    return app

def EM_plot(report):
    """
    Generate an annotated heatmap plot for empirical assessment.

    Args:
        report (dict): A dictionary containing the empirical assessment report.

    Returns:
        app (Dash): The Dash application object.

    """    
    app = Dash(__name__)
    walls = list(report.keys())
    
    figs = []  
    for wall in walls:
        data_matrix, wall_param_labels, sources, description_annotations = prepare_report(report, wall)
        heatmap = go.Heatmap(z=data_matrix,
                                x=sources,
                                y=wall_param_labels,
                                    colorscale='RdYlGn_r',  
                                zmin=0,
                                zmax=5,
                                colorbar=dict(title='Damage<br> Level'),
                                hoverongaps=False,
                                hoverinfo='text',
                                text=np.vectorize(lambda desc: f"{desc}")(description_annotations),
                                customdata=np.array(description_annotations))

        layout = go.Layout(
            title=f'{wall.capitalize()} empirical assessment',
            xaxis=dict(title='Literature Source', side='bottom', showgrid=True),
            yaxis=dict(title='SRI Parameter', showgrid=True, autorange='reversed'),
            template='plotly_white'
        )

        fig = go.Figure(data=heatmap, layout=layout)
        figs.append(fig)

    tab_heading_style = {
        'fontFamily': 'Arial, sans-serif',
        'color': '#3a4d6b'
    }
    tabs_content = [dcc.Tab(label=f"{wall.capitalize()}", children=[dcc.Graph(figure=fig)], style=tab_heading_style, selected_style=tab_heading_style) for wall, fig in zip(walls, figs)]
    app.layout = html.Div([
        dcc.Tabs(children=tabs_content)
    ])
    if __name__ == '__main__':
        app.run_server(debug=False)
    return app

def LTSM_plot(object):
    house = object.house
    app = Dash(__name__)
    
    assess_types = list(object.assessment['ltsm'].keys())
    all_assessment_tabs = []

    tab_style = {'fontFamily': 'Arial, sans-serif', 'color': '#3a4d6b'}
    
    for assessment in assess_types:
        figs = []
        wltsm = object.assessment['ltsm'][assessment]
        for i, wall in enumerate(house):
            # ---------------------------------- Process --------------------------------- #
            h = object.house[wall]['height']
            int = object.process['int'][wall]

            strain = wltsm['results'][wall]['e_tot']
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
                                y_title='Height [m,mm]',
                                subplot_titles=('Relative Wall position', 'Subsidence profile'))

            # Subsidence profile trace
            if assessment == 'measurements':
                fig.add_trace(go.Scatter(x=int['ax_rel'][::-1],
                                         y=int["z_lin"],
                                         mode='lines',
                                         name='Subsidence profile'),
                              row=2, col=1)
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
            try:
                if object.assessment['ltsm'][assessment]['report']:
                    report = object.assessment['ltsm'][assessment]['report']
                    data_matrix, wall_param_labels, sources, description_annotations = prepare_report(report, wall)
                    
                    comments = description_annotations[0]
                    assessments = data_matrix.flatten()
                    
                    colorscale = 'RdYlGn_r'
                    colors = get_colorscale(colorscale)
                    dlmax = data_matrix.flatten().max()
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
                            line=dict(width=0),  # Remove borders if not needed
                            row=1, col=1
                        )
                        fig.add_trace(go.Scatter(
                            x=[(i + 0.5) * segment_width],
                            y=[h / 2],
                            text=f"Assessment: {source}<br>DL: {assess_i}<br>Comment: {comment}",
                            mode='markers',
                            marker=dict(size=0.1, color='rgba(0,0,0,0)'),
                            hoverinfo='text'
                        ))
                    
                    ind = np.argmax(assessments)
                    cat = comments[ind]
            except Exception as e: # Use Boscardin & Cording (1989) as default         
                ecolor, cat = compute_param(strain)
                fig.add_shape(
                type="rect",
                x0= 0, y0=0,
                x1=xi - xj, y1=h,
                fillcolor=ecolor,
                row=1, col=1 )
            
            fig.update_layout(title=f'LTSM {wall} | e_tot = {strain:.2e} DL = {cat}',
                              legend=dict(traceorder="normal"),
                              template='plotly_white')

            # Remove duplicate legend labels
            names = set()
            fig.for_each_trace(
                lambda trace:
                trace.update(showlegend=False)
                if (trace.name in names) else names.add(trace.name))
            figs.append(fig)

        wall_tabs = [dcc.Tab(label=f"Wall {i+1}", children=[dcc.Graph(figure=fig)], style= tab_style, selected_style= tab_style ) for i, fig in enumerate(figs)]
        assessment_tab = dcc.Tab(label=f"{assessment.capitalize()} assessment", children=[dcc.Tabs(children=wall_tabs)], style=tab_style, selected_style= tab_style)
        all_assessment_tabs.append(assessment_tab)

    app.layout = html.Div([
        dcc.Tabs(children=all_assessment_tabs)
    ])

    return app


        
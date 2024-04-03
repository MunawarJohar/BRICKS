import dash
import numpy as np
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
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
                                    name=f'Wall {i+1}',
                                    line = dict(color=color[0])))
            fig.add_trace(go.Scatter3d(x=x, y=y_lin, 
                                    z= np.zeros_like(interp_vals),
                                    mode='lines',
                                    line=dict(color=color[2], dash='dash')))
            fig.add_trace(go.Scatter3d(x=np.full_like(wall['y'], wall['x'][0]), 
                                        y=wall['y'], 
                                        z= wall['z'],
                                        mode='markers', 
                                        marker=dict(size=4, color=color[0]),
                                        showlegend=False))
            fig.add_trace(go.Scatter3d(x=np.full_like(wall['y'], wall['x'][0]), 
                                        y=wall['y'], 
                                        z= np.zeros_like(wall['z']),
                                        mode='markers',
                                        marker=dict(size=2, color=color[2]),
                                        showlegend=False))
        else:  # Wall is along the x axis
            x_lin = np.linspace(wall["x"].min() , wall["x"].max() , 100)
            interp_vals = np.interp(x_lin, wall['x'], wall['z'])
            y = np.full_like(x_lin, wall['y'][0])  # Ycoord constant
            fig.add_trace(go.Scatter3d(x=x_lin, 
                                            y=y, 
                                            z=interp_vals, 
                                            mode='lines',
                                            name=f'Wall {i+1}',
                                            line = dict(color=color[0])))
            fig.add_trace(go.Scatter3d(x=x_lin, 
                                            y=y, 
                                            z=np.zeros_like(interp_vals),
                                            mode='lines',
                                            line=dict(color=color[2], dash='dash')))
            fig.add_trace(go.Scatter3d(x= wall['x'],
                                            y=np.full_like(wall['x'], 
                                            wall['y'][0]), 
                                            z=wall['z'], 
                                            mode='markers',
                                            marker=dict(size=4, color=color[0]),
                                            showlegend=False))
            fig.add_trace(go.Scatter3d(x= wall['x'],
                                            y=np.full_like(wall['x'], 
                                            wall['y'][0]), 
                                            z= np.zeros_like(wall['z']),
                                            mode='markers',
                                            marker=dict(size=2, color=color[2]),
                                            showlegend=False))
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
                                            name=f'Profile W{i+1}',
                                            line=dict(color=color[0], dash='dash')))
        
        else:  # Wall is along the x axis
            x_x += [xnormal.max(),xnormal.min()]
            x_y += [wall['y'].min()]*2
            y_const = np.full(xnormal.shape[0], wall['y'].min())
            fig.add_trace(go.Scatter3d(x= xnormal,
                                        y=y_const,
                                        z=z_curr,
                                        mode='lines',
                                        name=f'Profile W{i+1}',
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
                    showscale=False,
                        ),
    )
    fig.update_layout(
        scene=dict(
            xaxis_title='X [m]',
            yaxis_title='Y [m]',
            zaxis_title='Z [mm]',
            aspectmode="manual",
            aspectratio=dict(x=1*2, y=y_rat*3, z=z_rat*0.8),
        ),
        margin=dict(r=5, b=10, l=5, t=10),  # Adjust the margins as needed
        #legend=dict(traceorder='normal'),
        #showlegend=False,
        template = 'plotly_white',
        width=1400,
        height=600,
    )
    fig.show()


def LTSM_plot(OBJECT):        
        house = OBJECT.house
        app = dash.Dash(__name__)
        figs = []

        for wall in house:

            ltsm_params = house[wall]['ltsm']['params']
            for key, value in ltsm_params.items():
                globals()[key] = value
            # ----------------------------------- PLOTS ---------------------------------- #
            fig = make_subplots(rows=2, cols=1,
                                shared_xaxes=True, vertical_spacing=0.1,
                                subplot_titles=('Subsidence Profile', 'Legend'))
            fig.add_trace(go.Scatter(x=x, 
                                    y=w, 
                                    mode='lines', 
                                    name='Subsidence profile'), 
                                    row=2, col=1)
            fig.add_trace(go.Scatter(x=x, 
                                    y=np.full(len(x), limitline), 
                                    mode='lines', name='Limit Line',
                                    line=dict(color='black', dash='dash', width=1)), 
                                    row=2, col=1)
            height /= 1e3
            for z in [-xinflection, xinflection]:
                fig.add_trace(go.Scatter(x=[z, z], y=[0, height], mode='lines', name='Inflection point',
                                        line=dict(color='black', width=1, dash='dash')), row=1, col=1)
                
                fig.add_trace(go.Scatter(x=[z, z], y=[w.min(), w.max()], mode='lines', name='Inflection point',
                                        line=dict(color='black', width=1, dash='dash')), row=2, col=1)

            for influence in [-xlimit, xlimit]:
                fig.add_trace(go.Scatter(x=[influence, influence], y=[0, height], mode='lines', name='Influence area',
                                        line=dict(color='black', width=1, dash='dashdot')), row=1, col=1)
                
                fig.add_trace(go.Scatter(x=[influence, influence], y=[w.min(), w.max()], mode='lines', name='Influence area',
                                        line=dict(color='black', width=1, dash='dashdot')), row=2, col=1)
          
            fig.add_shape(
                type="rect",
                x0=xi, y0=0,
                x1=xj, y1=height,
                fillcolor="rgba(0,0,0,0.1)",
                row=1, col=1
            )
            fig.update_layout(title='LTSM problem scheme for wall',
                            xaxis_title='X-Axis',
                            yaxis_title='Z-Axis',
                            legend=dict(traceorder="normal"), 
                            template='plotly_white')
            figs.append(fig)

        tab_heading_style = {
                'fontFamily': 'Arial, sans-serif', 
                'color': '#3a4d6b'  
            }
        tabs_content = [dcc.Tab(label=f"Wall {i+1}", children=[dcc.Graph(figure=figs[i])], style=tab_heading_style, selected_style=tab_heading_style)  for i in range(len(house))]
        app.layout = html.Div([
            dcc.Tabs(children=tabs_content)
        ])
        if __name__ == '__main__':
            app.run_server(debug=True)
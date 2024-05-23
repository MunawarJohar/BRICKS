from dash import Dash, dcc, html
import plotly.graph_objects as go
import numpy as np
from ..utils import prepare_report

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

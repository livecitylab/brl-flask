from app import app
import dash
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
import plotly.graph_objs as go
from app.utils import fetch_rental_list

dash_app = dash.Dash(
    __name__,
    server=app,
    routes_pathname_prefix='/dash-price-per-floor-level/'
)

def make_graph():
    query = """query MyQuery {
      rental {
        district
        balcony
        cellar
        floor_level
        area
        kaltmiete
      }
    }
    """
    rental_list = fetch_rental_list(query)
    df = pd.DataFrame(rental_list)

    # create floor dataset and group by floor_level and calculate average kaltmiete
    floor_level_10 = df[df.groupby('floor_level')['floor_level'].transform('size') >= 10]
    floor = floor_level_10.groupby("floor_level")["kaltmiete"].mean().to_frame()

    # create bar chart
    data = [go.Bar(
        x=floor.index,
        y=floor.kaltmiete,
        marker={'colorscale': 'RdBu'})]

    my_layout = ({
        "yaxis": {"title": "Average Rent (€)"},
        "xaxis": {"type": "category", "title": "Floor Level"},
        "showlegend": False})

    fig = go.FigureWidget(data=data, layout=my_layout)
    fig.update_layout(barmode='stack')

    return fig

dash_app.layout = html.Div(style={"position":"relative", "width": "100%", "height": "100%"}, children=[
    dcc.Graph(
        id='price_per_floor_level',
        figure=make_graph(),
        responsive=True,
        style={
            "position": "absolute",
            "top": "0",
            "bottom": "0",
            "left": "0",
            "right": "0"
        }
    ),
])
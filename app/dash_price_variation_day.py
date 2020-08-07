from app import app
import dash
import dash_html_components as html
import dash_core_components as dcc
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from app.utils import fetch_rental_list
from app.utils import convert_date

dash_app = dash.Dash(
    __name__,
    server=app,
    routes_pathname_prefix='/dash-price-variation-day/'
)

def make_graph():
    # query of graphql database
    query = """
            query AllRentals {
              rental (where: {property_type: {_eq: "Wohnung"}}) {
                created_at
                preis_qm_kalt
              }
            }
        """
    rental_list = fetch_rental_list(query)
    df = pd.DataFrame(rental_list)
    df['date'] = df.apply(lambda x: convert_date(x['created_at']).strftime('%Y-%m-%d'), axis=1)
    df_by_date = df.groupby(["date"])['preis_qm_kalt'].agg([np.mean, np.max, np.min]).reset_index()

    # print(df_by_date.head())
    fig = px.line(df_by_date, x="date", y="mean")
    fig.update_layout(xaxis_tickangle=-45, showlegend=False)
    
    return fig


dash_app.layout = html.Div(style={"position":"relative", "width": "100%", "height": "100%"}, children=[
    dcc.Graph(
        id='graph_price_variation',
        figure=make_graph(),
        responsive=True,
        config={
            "scrollZoom": False,
            "displayModeBar": False
        },
        style={
            "position": "absolute",
            "top": "0",
            "bottom": "0",
            "left": "0",
            "right": "0"
        }
    ),
])
from app import app
import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
import pandas as pd
from app.utils import fetch_rental_list

dash_app = dash.Dash(
    __name__,
    server=app,
    routes_pathname_prefix='/dash-new-rentals-day/'
)

def make_graph():
    query = """query AllRentals {
          rental {
            created_at
          }
        }
        """

    rental_list = fetch_rental_list(query)
    df = pd.DataFrame(rental_list)

    # extract the days of the created date and create a new df
    df["date"] = df["created_at"].str[:10]
    df["date"] = pd.to_datetime(df["date"])

    df["days"] = df["date"].dt.dayofweek

    day_index = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}

    df["days"] = df["days"].map(day_index)

    day_groups = df.groupby(df["days"])["days"].count()

    day_groups = day_groups.to_frame()

    day_groups.columns = ["Count"]

    day_groups.reset_index(inplace=True)

    # create bar chart
    data = [go.Bar(
        x=day_groups.days,
        y=day_groups.Count,
        marker={
            'color': day_groups.Count,
            'colorscale': 'Viridis'})]

    my_layout = ({
                  "yaxis": {"title": "Count"},
                  "xaxis": {"title": "Days"},
                  "showlegend": False})

    fig = go.FigureWidget(data=data, layout=my_layout)
    fig.update_layout(barmode='stack', xaxis={'categoryorder': 'total descending'})

    return fig

dash_app.layout = html.Div(style={"position":"relative", "width": "100%", "height": "100%"}, children=[
    dcc.Graph(
        id='graph_rentals_per_day',
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
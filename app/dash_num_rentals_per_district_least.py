from app import app
import json
import os
import requests  # used to connect to GraphQL
import pandas as pd
import plotly.graph_objs as go
import dash
import dash_html_components as html
import dash_core_components as dcc

dash_app = dash.Dash(
    __name__,
    server=app,
    routes_pathname_prefix='/dash-rentals-per-district-least/'
)

def fetch_rental_list():
    """
    Querys the database and gets the latest rental information to feed the map
    """

    # graphql database query
    query = """query MyQuery {
  districts_berlin(order_by: {district: asc, postcode: asc}, distinct_on: district) {
    id
    postcode
    district
    rentals_aggregate {
      aggregate {
        count
      }
    }
  }
}
    """
    url = os.environ.get('GRAPHQL_URL')
    r = requests.post(url, json={'query': query})
    print(r.status_code)
    json_data = json.loads(r.text)
    rental_list = json_data["data"]["districts_berlin"]
    return rental_list


def num_rentals_per_district_least():
    """
    Districts with Least Rentals. Districts are shown in the format "District [Zipcode]" to
    achieve uniqueness in district definitions.
    """

    rental_list = fetch_rental_list()

    # build custom dataframe for plotly
    d = []
    for r in rental_list:
        d.append(
            {
                'district': r['district'] + ' [' + str(r['postcode']) + ']',
                'numrentals': r['rentals_aggregate']['aggregate']['count']
            }
        )
    dfInit = pd.DataFrame(d)
    df = dfInit.sort_values(by=['numrentals'], ascending=True)
    dfleast = df[df['numrentals'] > 0]
    # print(dfleast.head())
    # get top 5
    districts = dfleast.district[:5]
    rentals = dfleast.numrentals[:5]
    print(districts)

    # build and return the graph
    data = [
        go.Bar(
            x=districts,
            y=rentals,
            marker={'color': rentals, 'colorscale': 'Viridis'})
    ]
    layout = ({
        "yaxis": {"title": "Number of Rentals"},
        "xaxis": {"title": "District"},
        "showlegend": False})
    fig = go.Figure(data, layout)
    fig.update_layout(barmode='stack', title_x=0.5, height=500, width=400, yaxis=dict(
        showgrid=True,
        zeroline=True,
        showline=True,
        showticklabels=True,
        gridwidth=1,
        dtick=1
    ))
    return fig


dash_app.layout = html.Div(style={"position": "relative", "width": "100%", "height": "100%"}, children=[
    dcc.Graph(
        id='num_rentals_per_district_least',
        figure=num_rentals_per_district_least(),
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

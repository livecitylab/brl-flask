from app import app
import json
import os
import requests  # used to connect to GraphQL
import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
import pandas as pd


dash_app = dash.Dash(
    __name__,
    server=app,
    routes_pathname_prefix='/dash-rentals-per-district-all/'
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

def num_rentals_per_district_all():
    """
    Rental Offers By District. Districts are shown in the format "District [Zipcode]" to
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
    df = dfInit.sort_values(by=['numrentals'], ascending=False)

    # get top 20
    districts = df.district[:20]
    rentals = df.numrentals[:20]

    # build and return the graph
    labels = districts
    values = rentals

    # Use hole property to create a donut-like pie chart
    fig = px.pie(
        df,
        values=values,
        names=labels,
        labels={'district': 'District'},
        color_discrete_sequence=px.colors.sequential.Viridis, hole=.3)
    fig.update_layout(title_x=0.5, height=500, width=400)
    return fig

dash_app.layout = html.Div(style={"position":"relative", "width": "100%", "height": "100%"}, children=[
    dcc.Graph(
        id='num_rentals_per_district',
        figure=num_rentals_per_district_all(),
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
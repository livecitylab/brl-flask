from app import app
import dash
import dash_html_components as html
import dash_core_components as dcc
from urllib.request import urlopen
import plotly.express as px
import json  # used to parse GraphQL data
import requests  # used to connect to GraphQL
import pandas as pd
from datetime import datetime, timedelta
from app.utils import fetch_rental_list

dash_app = dash.Dash(
    __name__,
    server=app,
    routes_pathname_prefix='/dash-map/'
)

def make_map():

    # open geojson map of Berlin postcodes
    # with urlopen('https://tsb-opendata.s3.eu-central-1.amazonaws.com/plz/plz.geojson') as response:
    #     berlin = json.load(response)

    # get local geojson file which contains the district names
    with open('app/plz_districts.geojson') as json_file:
        berlin = json.load(json_file)

    # query of graphql database - copied from Daniels code
    query = """query AllRentals {
      rental {
        postcode
        preis_qm_kalt
        district
        created_at
      }
    }
    """
    rental_list = fetch_rental_list(query)
    df = pd.DataFrame(rental_list)

    # add column showing the offer date in the format Year-Month-Day
    df['Date'] = pd.to_datetime(df['created_at'])
    df['Date'] = df['Date'].dt.tz_localize(None)
    df2 = df.drop('created_at', axis=1)
    df2['Date'] = pd.to_datetime(df['Date']).dt.normalize()

    # create new dataframe with all rows of data from june
    june = df2.set_index('Date')['2020-06-01':'2020-06-30']
    # calculate mean of kaltmiete for each postcode
    grouped = june.groupby(['postcode', 'district'])
    june = grouped.mean()
    june = june.reset_index()
    # add column TimeFrame
    june['Time Frame'] = 'June'

    # create new dataframe with all rows of data from july
    july = df2.set_index('Date')['2020-07-01':'2020-07-31']
    # calculate mean of kaltmiete for each postcode
    grouped = july.groupby(['postcode', 'district'])
    july = grouped.mean()
    july = july.reset_index()
    # add column TimeFrame
    july['Time Frame'] = 'July'

    # select date 14 days ago and remove hours from date
    last14d = pd.to_datetime(datetime.now() - timedelta(days=14)).normalize()
    # select date of today and remove hours from date
    today = pd.to_datetime(datetime.now()).normalize()

    # create new dataframe with all rows of data from last 14 days
    mask_last14d = (df2['Date'] > last14d) & (df2['Date'] < today)
    last14d = df2.loc[mask_last14d]
    # drop column date as not needed anymore
    last14d = last14d.drop('Date', axis=1)
    # calculate mean of kaltmiete for each postcode
    grouped = last14d.groupby(['postcode', 'district'])
    last14d = grouped.mean()
    last14d = last14d.reset_index()
    # add column TimeFrame
    last14d['Time Frame'] = 'Last 14 days'

    # create one dataframe 'all' containing all the data from the three above
    all = last14d.append([july, june])



    # create new df with mean of preis_qm_kalt
    # grouped = df.groupby(['postcode', 'district'])
    # df2 = grouped.mean()
    # df2 = df2.reset_index()


    # create chloropleth map showing means of preis_qm_kalt for each postcode
    fig = px.choropleth_mapbox(
        all,
        geojson=berlin,
        color="preis_qm_kalt",
        color_continuous_scale="Blues",
        range_color=(5, 25),
        opacity=0.65,
        locations="postcode",
        featureidkey="properties.spatial_name",
        animation_frame="Time Frame",
        hover_name="district",
        hover_data={
            'preis_qm_kalt': ':.2f',  # customized formatting of price (1 Nachkommastelle)
        },
        labels={
            'postcode': 'Postcode',
            'preis_qm_kalt': 'Average price/m² cold (€)'
        },
        center={"lat": 52.520008, "lon": 13.404954},
        mapbox_style="carto-positron",
        zoom=9
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig

dash_app.layout = html.Div(style={"position":"relative", "width": "100%", "height": "100%"}, children=[
    dcc.Graph(
        id='map',
        figure=make_map(),
        responsive=True,
        config={
            "scrollZoom": True,
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

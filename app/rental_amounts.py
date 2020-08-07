import pandas as pd
import plotly.graph_objs as go
from app.utils import fetch_rental_list

def min_house():
    query = """query MyQuery {
      rental {
        district
        property_type
      }
    }
    """
    rental_list = fetch_rental_list(query)
    df = pd.DataFrame(rental_list)

    # haus
    haus = df[df.property_type == "Haus"]
    haus = haus.groupby("district")["district"].count().to_frame()
    haus_min = haus[haus.district == haus.district.min()]
    haus_max = haus[haus.district == haus.district.max()]

    # wohnung
    wohnung = df[df.property_type == "Wohnung"]
    wohnung = wohnung.groupby("district")["district"].count().to_frame()
    wohnung_min = wohnung[wohnung.district == wohnung.district.min()]
    wohnung_max = wohnung[wohnung.district == wohnung.district.max()]

    # create bar chart
    # data = [go.Bar(
    #     x=haus_min.index,
    #     y=haus_min.district,
    #     marker={
    #         'color': haus_min.district,
    #         'colorscale': 'Viridis'})]
    #
    # my_layout = ({"title": "District with the Least Houses",
    #               "yaxis": {"title": "Count"},
    #               "xaxis": {"title": "Districts"},
    #               "showlegend": False})
    #
    # fig = go.FigureWidget(data=data, layout=my_layout)
    # fig.update_layout(barmode='stack', title_x=0.5)

    # return fig
    return {
        "haus_min": haus_min.astype(str).to_dict(),
        "haus_max": haus_max.astype(str).to_dict(),
        "whg_min": wohnung_min.astype(str).to_dict(),
        "whg_max":wohnung_max.astype(str).to_dict(),
    }
import pandas as pd
from app.utils import fetch_rental_list
from app.utils import convert_date
from app.utils import round_tenth

def get_price_extremes():
    # query of graphql database
    query = """
        query AllRentals {
          rental {
            postcode
            preis_qm_kalt,
            property_type
            area
            created_at
            num_rooms
            district
          }
        }
    """
    rental_list = fetch_rental_list(query)
    df = pd.DataFrame(rental_list)

    # Get min, max in both Haus and Wohnung categories
    price_extremes = {}

    grouped_by_property = df.groupby('property_type')
    maxValues = grouped_by_property['preis_qm_kalt'].idxmax()
    minValues = grouped_by_property['preis_qm_kalt'].idxmin()

    most_expensive_haus = df.iloc[maxValues['Haus']]
    most_expensive_wohnung = df.iloc[maxValues['Wohnung']]
    cheapest_haus = df.iloc[minValues['Haus']]
    cheapest_wohnung = df.iloc[minValues['Wohnung']]

    price_extremes['haus_max'] = most_expensive_haus.astype(str).to_dict()
    price_extremes['whg_max'] = most_expensive_wohnung.astype(str).to_dict()

    price_extremes['haus_min'] = cheapest_haus.astype(str).to_dict()
    price_extremes['whg_min'] = cheapest_wohnung.astype(str).to_dict()
    # format values before returning
    for key in price_extremes:
        price_extremes[key]['created_at'] = convert_date(price_extremes[key]['created_at']).strftime('%d.%m.%y')
        num_rooms = float(price_extremes[key]['num_rooms'])
        if (num_rooms.is_integer()):
            price_extremes[key]['num_rooms'] = str(int(num_rooms))

    # get most expensive and cheapes districts in average, both for Haus and Wohnung
    district_extremes = {}
    grouped_by_district = df.groupby(['property_type', 'district'], as_index=False, sort=False)[['preis_qm_kalt']].mean()

    haus_idxmax = grouped_by_district.loc[grouped_by_district['property_type'] == 'Haus']['preis_qm_kalt'].idxmax()
    haus_idxmin = grouped_by_district.loc[grouped_by_district['property_type'] == 'Haus']['preis_qm_kalt'].idxmin()
    district_extremes['haus_max'] = grouped_by_district.iloc[haus_idxmax].astype(str).to_dict()
    district_extremes['haus_min'] = grouped_by_district.iloc[haus_idxmin].astype(str).to_dict()

    whg_idxmax = grouped_by_district.loc[grouped_by_district['property_type'] == 'Wohnung']['preis_qm_kalt'].idxmax()
    whg_idxmin = grouped_by_district.loc[grouped_by_district['property_type'] == 'Wohnung']['preis_qm_kalt'].idxmin()
    district_extremes['whg_max'] = grouped_by_district.iloc[whg_idxmax].astype(str).to_dict()
    district_extremes['whg_min'] = grouped_by_district.iloc[whg_idxmin].astype(str).to_dict()

    property_prices = {
        'price_extremes': price_extremes,
        'district_extremes': district_extremes
    }

    return property_prices



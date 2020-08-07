import pandas as pd
from app.utils import fetch_rental_list
from app.utils import convert_date
from app.utils import round_tenth

def get_size_extremes():
    # query of graphql database
    query = """
        query AllRentals {
          rental {
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
    size_extremes = {}

    grouped_by_property = df.groupby('property_type')
    maxValues = grouped_by_property['area'].idxmax()
    minValues = grouped_by_property['area'].idxmin()


    largest_haus = df.iloc[maxValues['Haus']]
    largest_wohnung = df.iloc[maxValues['Wohnung']]
    smallest_haus = df.iloc[minValues['Haus']]
    smallest_wohnung = df.iloc[minValues['Wohnung']]



    size_extremes['haus_max'] = largest_haus.astype(str).to_dict()
    size_extremes['whg_max'] = largest_wohnung.astype(str).to_dict()

    size_extremes['haus_min'] = smallest_haus.astype(str).to_dict()
    size_extremes['whg_min'] = smallest_wohnung.astype(str).to_dict()


    # format values before returning
    for key in size_extremes:
        size_extremes[key]['created_at'] = convert_date(size_extremes[key]['created_at']).strftime('%d.%m.%y')
        num_rooms = float(size_extremes[key]['num_rooms'])
        if (num_rooms.is_integer()):
            size_extremes[key]['num_rooms'] = str(int(num_rooms))

    # get most expensive and cheapes districts in average, both for Haus and Wohnung
    district_extremes = {}
    grouped_by_district = df.groupby(['property_type', 'district'], as_index=False, sort=False)[['area']].mean()

    haus_idxmax = grouped_by_district.loc[grouped_by_district['property_type'] == 'Haus']['area'].idxmax()
    haus_idxmin = grouped_by_district.loc[grouped_by_district['property_type'] == 'Haus']['area'].idxmin()
    district_extremes['haus_max'] = grouped_by_district.iloc[haus_idxmax].astype(str).to_dict()
    district_extremes['haus_min'] = grouped_by_district.iloc[haus_idxmin].astype(str).to_dict()

    whg_idxmax = grouped_by_district.loc[grouped_by_district['property_type'] == 'Wohnung']['area'].idxmax()
    whg_idxmin = grouped_by_district.loc[grouped_by_district['property_type'] == 'Wohnung']['area'].idxmin()
    district_extremes['whg_max'] = grouped_by_district.iloc[whg_idxmax].astype(str).to_dict()
    district_extremes['whg_min'] = grouped_by_district.iloc[whg_idxmin].astype(str).to_dict()


    return {
        'size_extremes': size_extremes,
        'district_extremes': district_extremes
    }

# print(get_size_extremes())



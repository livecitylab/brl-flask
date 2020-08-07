import pandas as pd
from app.utils import fetch_rental_list

def get_amenities():
    query = """
        query rentals {
            rental {
                cellar
                balcony
                garden
                kitchen_availability
                district
            }
        }
    """
    rental_list = fetch_rental_list(query)
    df = pd.DataFrame(rental_list)

    # cellar data
    cellar = df.groupby("cellar")["cellar"].count().to_frame()
    cellar = cellar.div(cellar["cellar"].sum()) * 100
    cellar["new_index"] = ["n", "y"]
    cellar.index = cellar.new_index
    cellar = cellar.drop(columns=["new_index"])

    # balcony data
    balcony = df.groupby("balcony")["balcony"].count().to_frame()
    balcony = balcony.div(balcony["balcony"].sum()) * 100
    balcony["new_index"] = ["n", "y"]
    balcony.index = balcony.new_index
    balcony = balcony.drop(columns=["new_index"])


    # kitchen data
    kitchen = df.groupby("kitchen_availability")["kitchen_availability"].count().to_frame()
    kitchen = kitchen.div(kitchen["kitchen_availability"].sum()) * 100
    kitchen["new_index"] = ["n", "y"]
    kitchen.index = kitchen.new_index
    kitchen = kitchen.drop(columns=["new_index"])

    # garden data
    garden = df.groupby("garden")["garden"].count().to_frame()
    garden = garden.div(garden["garden"].sum()) * 100
    garden["new_index"] = ["n", "y"]
    garden.index = garden.new_index
    garden = garden.drop(columns=["new_index"])

    return {
        "cellar":cellar.astype(str).to_dict()["cellar"],
        "balcony":balcony.astype(str).to_dict()["balcony"],
        "kitchen":kitchen.astype(str).to_dict()["kitchen_availability"],
        "garden":garden.astype(str).to_dict()["garden"]
    }

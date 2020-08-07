import json  # used to parse GraphQL data
import os
import requests  # used to connect to GraphQL
from datetime import datetime

def convert_date(d):
    if ":" == d[-3:-2]:
        d = d[:-3] + d[-2:]
    try:
        newDate = datetime.strptime(d, "%Y-%m-%dT%H:%M:%S.%f%z")
    except ValueError:
        newDate = datetime.strptime(d, "%Y-%m-%dT%H:%M:%S%z")
    return newDate

def fetch_rental_list(query):
    """
    Querys the database and gets the latest rental information to feed the map
    """
    url = os.environ.get('GRAPHQL_URL')
    r = requests.post(url, json={'query': query})
    print(r.status_code)
    json_data = json.loads(r.text)
    rental_list = json_data["data"]["rental"]
    return rental_list

def fetch_district(postcode):
    """
    Querys the database and gets the distric related to the postcode
    However, in case there are more districts to each postcode,
    it will only get one of the values (the first found)
    """
    # query of graphql database
    query = """
        query district($_eq: Int) {
          districts_berlin(where: {postcode: {_eq: $_eq}}, limit: 1) {
            district
          }
        }
    """
    url = os.environ.get('GRAPHQL_URL')
    r = requests.post(url, json={'query': query, "variables": {"_eq": int(postcode)}})
    print(r.status_code)
    json_data = json.loads(r.text)
    district = json_data["data"]["districts_berlin"][0]['district']
    return district

def round_tenth(n):
    return round(n * 100) / 100

from flask import Flask
from flask_cors import CORS


app = Flask(__name__)

CORS(app, support_credentials=True)

from app import routes
from app import dash_map
from app import dash_price_variation_day
from app import dash_rental_per_day
from app import dash_num_rentals_per_district
from app import dash_num_rentals_per_district_all
from app import dash_num_rentals_per_district_least
from app import dash_price_per_floor_level

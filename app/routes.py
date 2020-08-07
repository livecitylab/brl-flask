from flask import jsonify, request
import os
import pickle
from datetime import datetime
from flask_cors import cross_origin, CORS

from app import app
from app.prices import get_price_extremes
from app.sizes import get_size_extremes
from app.ML import full_train, get_preds
from app.amenities import get_amenities
from app.rental_amounts import min_house

CORS(app, support_credentials=True)
@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"


@app.route('/price-stats')
def price_stats():
    prices = get_price_extremes()
    return jsonify({"data": prices})

@app.route('/size-stats')
def size_stats():
    sizes = get_size_extremes()
    return jsonify({"data": sizes})\

@app.route('/amenities-stats')
def amenities_stats():
    amenities = get_amenities()
    return jsonify({"data": amenities})

@app.route('/amounts-stats')
def amounts_stats():
    data = min_house()
    return jsonify({"data": data})

@app.route('/get-estimate', methods=["POST"])
@cross_origin()
def get_estimate():
    content = request.get_json()
    for key in content:
        print(key)
    data_row = {
        'area': content['area'],
        'balcony': content['balcony'],
        'cellar': content['cellar'],
        'elevator': content['elevator'],
        'kitchen_availability': content['kitchen'],
        'num_rooms': content['num_rooms'],
        'ground_floor': content['ground_floor'],
        'district': content['district']
    }
    preds = get_preds(data_row)
    return jsonify(preds)


@app.route('/do-full-train')
def do_full_train():
    time_start = datetime.now()
    ensemble_reg = full_train()
    PATH = os.environ.get('HOME') + "/model.pickle"  # CHANGE PATH TO SERVER DIR
    pickle.dump(ensemble_reg, open(PATH, "wb"))
    time_end = datetime.now()
    return jsonify({"file": PATH,
                    "start": str(time_start),
                    "end": str(time_end),
                    "status":'ok'})


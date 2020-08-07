# -*- coding: utf-8 -*-
"""
This file contains all steps to get a prediction
querying the data
cleaning/adjusting the data
training the model
getting the predictions

"""
import os
import pandas as pd
import numpy as np
import pickle
# sk-learn imports
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor
from sklearn.model_selection import cross_val_score
from app.utils import fetch_rental_list

np.random.seed(13)  # doesn't work yet




# function to dummy encode using pandas
def encode_and_bind(original_dataframe, feature_to_encode):
    """
    Function to dummy encode a given column and drop it afterwards.

    Parameters
    ----------
    original_dataframe : DataFrame to be transformed
    feature_to_encode : Column to be dummy encoded (columnname as string)

    Returns
    -------
    New DataFrame with dummy encoded columns and without original column.

    """
    dummies = pd.get_dummies(original_dataframe[feature_to_encode])
    res = pd.concat([original_dataframe, dummies], axis=1)
    res = res.drop([feature_to_encode], axis=1)
    return (res)


def df_prep_split():
    """
    Function to clean and prepare the data for the training of the ML-model.

    Returns
    -------
    X : Pandas DataFrame containing the training-data without the target value "kaltmiete"
    y : Pandas Series containing the labels/the target value "kaltmiete"

    """
    # the query should contain all wanted features
    query = """query AllRentals {
          rental {
            property_type
            area
            district
            balcony
            cellar
            elevator
            floor_level
            kaltmiete
            kitchen_availability
            num_rooms
          }
        }
    """
    rental_list = fetch_rental_list(query)
    df = pd.DataFrame(rental_list)
    # dropping rows with houses
    df.drop(df[df["property_type"] == "Haus"].index, inplace=True)
    # dropping the column as it carries no real information anymore
    df.drop("property_type", axis=1, inplace=True)
    # fill NAs in floor_level with median
    df['floor_level'].fillna((df['floor_level'].median()), inplace=True)
    # create ground_floor col
    df["ground_floor"] = df["floor_level"].apply(lambda x: 1 if x == 0 else 0)
    df.drop("floor_level", axis=1, inplace=True)
    # drop NAs in district
    df.drop(df[df["district"].isnull()].index, inplace=True)
    # remove outliers
    df.drop(df[(df["kaltmiete"] > 8000) | (df["kaltmiete"] < 150)].index, inplace=True)
    df.reset_index(drop=True, inplace=True)  # reset index
    # encode district
    df = encode_and_bind(df, "district")
    X, y = df.drop("kaltmiete", axis=1), df["kaltmiete"].copy()
    return X, y


#### RUN TO TRAIN MODEL AND SAVE IT
def full_train():
    """
    Function to train the model on all of the available data. The trained model
    is saved as a pickle file.

    Returns
    -------
    Nothing is directly returned. The function saves the model in a pickle file
    for later usage in predictions.

    """
    X, y = df_prep_split()[0], df_prep_split()[1]
    ridge_reg = Ridge()
    forest_reg = RandomForestRegressor(max_features=8, n_estimators=100,
                                       n_jobs=-1)  # downscaled n_estimators from 500 due to memory issues on server
    boost_reg = GradientBoostingRegressor()
    ensemble_reg = VotingRegressor(estimators=[("ridge", ridge_reg),
                                               ("RF", forest_reg), ("GB", boost_reg)], n_jobs=-1)
    ensemble_reg.fit(X, y)
    PATH = os.environ.get('HOME') + "/app/model.pickle"  # CHANGE PATH TO SERVER DIR
    return pickle.dump(ensemble_reg, open(PATH, "wb"))


#### RUN FOR MONITORING
def get_mean_error():
    """
    Function, that uses the model to run 10-fold cross validation in order to determine the mean
    error of the current model.

    Returns
    -------
    Mean root mean squared error of 10-fold cross validation run on the whole
    dataset.

    """
    PATH = os.environ.get('HOME') + "/app/model.pickle"
    model = pickle.load(open(PATH, 'rb'))
    X, y = df_prep_split()[0], df_prep_split()[1]
    scores = cross_val_score(model, X, y, scoring="neg_mean_squared_error", cv=10)
    ensemble_rmses = np.sqrt(-scores)
    return ensemble_rmses.mean()


def set_input_params(column):
    """
    Function to set the input range and default values for the user input.

    Parameters
    ----------
    column : string name of the column

    Returns
    -------
    min_val : minimum value for chosen column
    default : mean value for float type columns, median for int type columns
    max_val : maximum value for chosen column

    """
    df = df_prep_split()[0]
    min_val = round(df[column].min())
    max_val = round(df[column].max())
    if df[column].dtype == "float64":
        default = round(df[column].mean())
    elif df[column].dtype == "int64":
        default = round(df[column].median())
    return min_val, default, max_val


#### RUN FOR PREDS
def get_preds(dictionary):
    """
    Function to retrieve the predicted rental price based on the user input on
    the webapp.
    Version 1.0: The range is set manually based on the calculated error and
    knowledge about the rental prices in Berlin.(This will probably change in
    later versions)

    Parameters
    ----------
    dictionary : dictionary of values from the user input on the webapp
    format:
    {'area':98, 'balcony': 0, 'cellar': 1, 'elevator': 1,
          'kitchen_availability':1,'num_rooms': 3, 'ground_floor':0,
          'district': "Prenzlauer Berg"}

    Returns
    -------
    dictionary with the predicted point estimate and range of the rental price

    """
    df = pd.DataFrame(dictionary, index=[0])
    df = encode_and_bind(df, "district")
    X = df_prep_split()[0]
    X.drop(list(df.columns), axis=1, inplace=True)
    df = pd.merge(df, X, how="left", left_index=True, right_index=True)
    PATH = os.environ.get('HOME') + "/app/model.pickle"
    model = pickle.load(open(PATH, 'rb'))
    # I am currently setting the range manually, this will be changed when memory usage is not an issue
    # the range is based on the error and knowledge about the berlin rental market, with prices typically being higher than expected not lower
    return {"point_est": round(model.predict(df)[0]),
            "lower_bound": round(model.predict(df)[0]) - 100,
            "upper_bound": round(model.predict(df)[0]) + 250}


### Code for testing
# print(set_input_params("num_rooms"))
# full_train() #needs to be called once only
### Test Data Dict
"""
data_row = {'area':98, 'balcony': 0, 'cellar': 1, 'elevator': 1,
          'kitchen_availability':1,'num_rooms': 3, 'ground_floor':0,
          'district': "Prenzlauer Berg"}
"""

# print(get_mean_error())
# print(get_preds(data_row))

###finding out how much memory is used by full_train()
# import tracemalloc

# tracemalloc.start()
# full_train()
# get_mean_error()
# current, peak = tracemalloc.get_traced_memory()
# print(f"Current memory usage is {current / 10**6}MB; Peak was {peak / 10**6}MB")
# tracemalloc.stop()


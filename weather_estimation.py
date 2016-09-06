from __future__ import division

import datetime
import os

import pandas
from sklearn import linear_model
from sklearn.naive_bayes import GaussianNB

import download_training_data.download_location_info

os.environ['TZ'] = 'UTC'

def get_temperature_model(df):

    temp_linr_model = linear_model.LinearRegression()
    input_x = df[['lat', 'lng', 'elev', 'time']].values
    temp_y = df[['temp']].values

    temp_linr_model.fit(input_x, temp_y)

    return temp_linr_model

def get_humidity_model(df):

    hum_linr_model = linear_model.LinearRegression()
    input_x = df[['lat', 'lng', 'elev', 'time']].values
    hum_y = df[['hum']].values

    hum_linr_model.fit(input_x, hum_y)

    return hum_linr_model

def get_pressure_model(df):

    pres_linr_model = linear_model.LinearRegression()
    input_x = df[['lat', 'lng', 'elev', 'time']].values
    pres_y = df[['pres']].values

    pres_linr_model.fit(input_x, pres_y)

    return pres_linr_model

def get_condition_model(df):

    cond_gnb_model = GaussianNB()
    input_x = df[['lat', 'lng', 'elev', 'time']].values
    cond_y = df[['cond']].values

    cond_gnb_model.fit(input_x, cond_y)

    return cond_gnb_model

def generate_weather_data(location_info_list, temp_model, pres_model, hum_model, cond_model, start_date):

    predicted_weather_data = {}

    for location_info in location_info_list:

        loc = location_info['location']
        lat = location_info['lat']
        lng = location_info['lng']
        elev = location_info['elev']

        for date_offset in range(0, 365, 30):
            new_date = start_date + datetime.timedelta(date_offset)
            time = int((new_date).strftime('%s'))

            predicted_weather_data['Location'] = predicted_weather_data.get('Location', []) + [loc]
            predicted_weather_data['Position'] = predicted_weather_data.get('Position', []) + [str(lat) + ',' + str(lng) + ',' + str(elev)]
            predicted_weather_data['Local Time'] = predicted_weather_data.get('Local Time', []) + [new_date.isoformat()]

            cond = cond_model.predict([lat, lng, elev, time])[0].lower()
            if 'clear' not in cond:
                predicted_weather_data['Conditions'] = predicted_weather_data.get('Conditions', []) + ['Rain']
            elif 'snow' in cond:
                predicted_weather_data['Conditions'] = predicted_weather_data.get('Conditions', []) + ['Snow']
            else:
                predicted_weather_data['Conditions'] = predicted_weather_data.get('Conditions', []) + ['Sunny']

            temp = temp_model.predict([lat, lng, elev, time])[0][0]
            temp_celsius = (temp - 32) * (5.0 / 9.0)
            predicted_weather_data['Temperature'] = predicted_weather_data.get('Temperature', []) + [temp_celsius]

            pres = pres_model.predict([lat, lng, elev, time])[0][0]
            predicted_weather_data['Pressure'] = predicted_weather_data.get('Pressure', []) + [pres]

            hum = hum_model.predict([lat, lng, elev, time])[0][0]
            predicted_weather_data['Humidity'] = predicted_weather_data.get('Humidity', []) + [int(hum * 100)]

    return predicted_weather_data

if __name__ == '__main__':

    # Please specify training data file path here
    df = pandas.read_csv('data/training_weather_data.csv')

    # Generating models for weather predictions
    # using linear regression for floating point labels
    # and Gaussian naive bayes model for string labels
    temp_model = get_temperature_model(df)
    pres_model = get_pressure_model(df)
    hum_model = get_humidity_model(df)
    cond_model = get_condition_model(df)

    # Date from which we will start generating data every 30 days 
    start_date = datetime.datetime(2016, 1, 1)

    # list of locations for which we are generating data
    # we can add as many locations as we want
    location_list = None
    with open('data/target_locations.txt') as f:
        location_list = [line.strip() for line in f]

    # obtaining lat, lng and elevation for the listed locations
    location_info_list = download_training_data.download_location_info(location_list)

    # Generating weather data in the form of dictionary
    generated_weather_data = generate_weather_data(location_info_list, temp_model, pres_model, hum_model, cond_model, start_date)

    # Generating dataframe so that we can write it in the file
    df = pandas.DataFrame(generated_weather_data)
    df[["Location", "Position", "Local Time", "Conditions", "Temperature", "Pressure", "Humidity"]].to_csv(
        "data/generated_weather_data.psv",
        header=0,
        index=0,
        sep='|'
    )
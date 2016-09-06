from __future__ import division

import datetime
import requests
import json
import os

from pandas import DataFrame
import forecastio

os.environ['TZ'] = 'UTC'

def download_location_info(location_list):
    
    geocode_url = 'http://maps.googleapis.com/maps/api/geocode/json?sensor=false&address='
    elevation_url = 'https://maps.googleapis.com/maps/api/elevation/json?locations='

    location_info_list = []

    for location in location_list:
        location_info = {'location': location}

        rgc = requests.get(geocode_url+location).json()
        if rgc.get('results'):
            for rgc_results in rgc.get('results'):
                latlong = rgc_results.get('geometry','').get('location','')
                location_info['lat'] = latlong.get('lat','')
                location_info['lng'] = latlong.get('lng','')

                relev = requests.get(elevation_url + str(location_info['lat']) + ',' + str(location_info['lng'])).json()
                if relev.get('results'):
                    for relev_results in relev.get('results'):
                        location_info['elev'] = relev_results.get('elevation', '')
                        break
                break

        location_info_list.append(location_info)

    return location_info_list

def download_weather_data(location_info_list, start_date, api_key):
    weather_data = {}
    for location_info in location_info_list:
        for date_offset in range(0, 365, 7):
            try:
                forecast = forecastio.load_forecast(
                    api_key,
                    location_info['lat'],
                    location_info['lng'],
                    time=start_date+datetime.timedelta(date_offset),
                    units="us"
                )
                
                for hour in forecast.hourly().data:
                    weather_data['loc'] = weather_data.get('loc', []) + [location_info['location']]
                    weather_data['lat'] = weather_data.get('lat', []) + [location_info['lat']]
                    weather_data['lng'] = weather_data.get('lng', []) + [location_info['lng']]
                    weather_data['elev'] = weather_data.get('elev', []) + [location_info['elev']]
                    weather_data['cond'] = weather_data.get('cond', []) + [hour.d.get('summary', '')]
                    weather_data['temp'] = weather_data.get('temp', []) + [hour.d.get('temperature', 50)]
                    weather_data['hum'] = weather_data.get('hum', []) + [hour.d.get('humidity', 0.5)]
                    weather_data['pres'] = weather_data.get('pres', []) + [hour.d.get('pressure', 1000)]
                    weather_data['time'] = weather_data.get('time', []) + [hour.d['time']]
            except:
                return weather_data

    return weather_data

if __name__ == '__main__':

    location_list = None
    with open('data/training_locations.txt') as f:
        location_list = [line.strip() for line in f]

    location_info_list = download_location_info(location_list)

    weather_data = download_weather_data(location_info_list, datetime.datetime(2015, 1, 1), '790a053f46cda18de23944de6b44fc91')

    df = pandas.DataFrame(weather_data)
    df.to_csv('data/training_weather_data.csv')
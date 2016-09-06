# Toy Weather Simulator
This a toy weather simulator, which actually works by creating a model from training data and then generating weather data from this model. The file download_training_data.py is used to download the training data and save it in data folder. The weather_estimation.py file is used to generate the output data. Currently I have generated data for 15 places defined in target_locations.txt file. The generated data file name is generated_weather_data.psv.

## Requirements
This application requires Python 2.7 and following python packages.

* pandas ( for DataFrames to load and save the data )

* sklearn ( for machine learning model creation like linear regression model, guassian naive bayes model )

* forcastio ( to download training weather data from forcast.io )

## Requirement Installation

```bash
sudo pip install pandas
sudo pip install sklearn
sudo pip install python-forcastio
```
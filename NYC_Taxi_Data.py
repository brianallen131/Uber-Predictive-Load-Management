# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
from datetime import datetime
import pygeohash as g
import numpy as np

def convertDateTime(date):
    return datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

def extractDay(date):
    return date.day

def extractHour(date):
    return date.hour

def extractMinute(date):
    return date.minute

def geoHash(lat,lon,precision):
    return g.encode(lat,lon,precision)

geo_hash = pd.read_table("geo_hash.txt", header = None, sep = ",")[0].tolist()
taxi_data = pd.read_csv("yellow_tripdata_2014-05.csv")
taxi_data[" pickup_datetime"] = taxi_data[" pickup_datetime"].apply(convertDateTime)
taxi_data["date"] = taxi_data[" pickup_datetime"].apply(extractDay)
taxi_data["hour"] = taxi_data[" pickup_datetime"].apply(extractHour)
taxi_data["minute"] = taxi_data[" pickup_datetime"].apply(extractMinute)

data = taxi_data[taxi_data.date.isin([6, 13, 20, 27])]
data["geohash"] = data.apply(lambda x: geoHash(x[' pickup_latitude'], x[' pickup_longitude'],7), axis=1)
data["price"] = data[" total_amount"] - data[" tip_amount"] 

data_10_to_11 = data[(data.hour >= 22) & (data.hour < 23)]
data_10_to_11 = data_10_to_11[data_10_to_11.geohash.isin(geo_hash)]

# Get average price for 10-11PM in MSG area
avg_price = np.mean(data["price"].tolist())
std_price = np.std(data["price"].tolist())
data_10_to_11_mod = data_10_to_11[(data_10_to_11.price < avg_price + 1.5*std_price) & (data_10_to_11.price > avg_price - 1.5*std_price)]
avg_price_1 = np.mean(data_10_to_11_mod["price"].tolist())
print("Average Price: $" + str(round(avg_price_1,2)))

data_10_to_11.groupby(data_10_to_11.date).count()

# Get pick-up delta relative to control group
effect_data = data_10_to_11[data_10_to_11.date == 13]
control_data = data_10_to_11[(data_10_to_11.date == 6) | (data_10_to_11.date == 20) | (data_10_to_11.date == 27)]
control_count = np.mean(control_data[["date", "hour"]].groupby(["date"]).count()["hour"].tolist())

a = control_data[["date", "hour"]].groupby(["date"]).count()

per_hour_increase = len(effect_data) / control_count - 1
print("% Change in Pick-ups vs. Control: " + str(round(per_hour_increase*100,2)) + "%")

# Get pick-up delta relative to earlier tod
data_9_to_10 = data[(data.hour >= 21) & (data.hour < 22)]
data_9_to_10 = data_9_to_10[data_9_to_10.geohash.isin(geo_hash)]
effect_data_1 = data_9_to_10[data_9_to_10.date == 13]
per_hour_increase_1 = len(effect_data) / len(effect_data_1) - 1
print("% Change in Pick-ups vs. Earlier: " + str(round(per_hour_increase_1*100,2)) + "%")



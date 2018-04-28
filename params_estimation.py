#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 28 11:02:51 2018

@author: michelkauffmann
"""

import pandas as pd
from datetime import datetime
import pygeohash as g
import numpy as np
import os
import math as m

os.chdir("/Users/michelkauffmann/Downloads/uber-tlc-foil-response-master/uber-trip-data")
uber = pd.read_csv("uber-raw-data-may14.csv")

os.chdir("/Users/michelkauffmann/Downloads/Uber-Predictive-Load-Management-master")
taus = pd.read_csv("taus.csv")

os.chdir("/Users/michelkauffmann/Downloads/Uber-Predictive-Load-Management-master/Lookups")
geohash_6 = pd.read_csv("MSG Geohash6 Lookup.csv")
geohash_7 = pd.read_csv("MSG Geohash7 Lookup.csv")

def uber_utility(W_uber, P_uber):
        
    return 12 - 1.0*W_uber - 0.2*P_uber 

def subway_utility(W_sub, P_sub):
    
    return 5 - 0.5*W_sub

def probability(W_uber, P_uber, W_sub, P_sub, theta):
    denom = m.exp(uber_utility(W_uber, P_uber)/theta) + m.exp(subway_utility(W_sub, P_sub)/theta)
    probability = m.exp(uber_utility(W_uber, P_uber)/theta)/denom
        
    return probability

def convertDateTime(date):
    
    return datetime.strptime(date, '%m/%d/%Y %H:%M:%S')

def extractDay(date):
    
    return date.day

def extractHour(date):
    
    return date.hour

def extractMinute(date):
    
    return date.minute

def geoHash(lat,lon,precision):
    
    return g.encode(lat,lon,precision)

def clean_geohash(code):
    
    return code[0:6]

taus["pickup_loc_6"] = taus["pickup_loc"].apply(clean_geohash)
taus["dropoff_loc_6"] = taus["dropoff_loc"].apply(clean_geohash)
taus = taus[taus["avg(duration)"] <= 15*60]

taus_1_2 = taus[taus.dropoff_loc_6.isin(geohash_6["Geohash6"]) & ~taus.dropoff_loc.isin(geohash_7["Geohash7"])]
d_1_2 = np.mean(taus_1_2["avg(duration)"]) / 60

taus_1_3 = taus[~taus.dropoff_loc_6.isin(geohash_6["Geohash6"])]
d_1_3 = np.mean(taus_1_3["avg(duration)"]) / 60

P_uber = (12.03 - 3) * 1.5
P_sub = 3
theta = 2
W_sub = 7

# Get x_ij
x_ij = pd.DataFrame(0.0, index = [1,2,3], columns = [1,2,3])
x_ij[1][1] = probability(0, P_uber, W_sub, P_sub, theta)
x_ij[2][2] = probability(0, P_uber, W_sub, P_sub, theta)
x_ij[3][3] = probability(0, P_uber, W_sub, P_sub, theta)

x_ij[1][2] = probability(d_1_2, P_uber, W_sub, P_sub, theta)
x_ij[2][1] = probability(d_1_2, P_uber, W_sub, P_sub, theta)

x_ij[1][3] = probability(d_1_3, P_uber, W_sub, P_sub, theta)
x_ij[3][1] = probability(d_1_3, P_uber, W_sub, P_sub, theta)

x_ij[2][3] = probability(1.5*d_1_2, P_uber, W_sub, P_sub, theta)
x_ij[3][2] = probability(1.5*d_1_2, P_uber, W_sub, P_sub, theta)

# Get N_0j
N_0j = pd.DataFrame(0.0, index = [1,2,3], columns = ["N_0j"])

uber["Date/Time"] = uber["Date/Time"].apply(convertDateTime) 
uber["day"] = uber["Date/Time"].apply(extractDay) 
uber["hour"] = uber["Date/Time"].apply(extractHour) 
uber["geohash_7"] = uber.apply(lambda x: geoHash(x['Lat'], x['Lon'], 7), axis = 1)
uber["geohash_6"] = uber.apply(lambda x: geoHash(x['Lat'], x['Lon'], 6), axis = 1)
uber = uber[uber.day.isin([6,20,27]) & (uber.hour >= 22) & (uber.hour < 23)]

N_0j["N_0j"][1] = np.mean(uber[uber.geohash_7.isin(geohash_7["Geohash7"])].groupby(uber.day).count())[1]
N_0j["N_0j"][2] = np.mean(uber[uber.geohash_6.isin(geohash_6["Geohash6"]) & ~uber.geohash_7.isin(geohash_7["Geohash7"])].groupby(uber.day).count())[1]
N_0j["N_0j"][3] = np.mean(uber[~uber.geohash_6.isin(geohash_6["Geohash6"])].groupby(uber.day).count())[1]

# Get c_ij
cost_per_min = 1554 / 30 / 60
p_idle = 0.7

c_ij = pd.DataFrame(0.0, index = [1,2,3], columns = [1,2,3])
c_ij[1][1] = 0
c_ij[2][2] = 0
c_ij[3][3] = 0

c_ij[1][2] = d_1_2 * cost_per_min * p_idle
c_ij[2][1] = d_1_2 * cost_per_min * p_idle

c_ij[1][3] = d_1_3 * cost_per_min * p_idle
c_ij[3][1] = d_1_3 * cost_per_min * p_idle

c_ij[2][3] = d_1_2 * 1.5 * cost_per_min * p_idle
c_ij[3][2] = d_1_2 * 1.5 * cost_per_min * p_idle


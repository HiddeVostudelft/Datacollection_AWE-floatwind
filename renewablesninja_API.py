#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 16:49:42 2023

@author: hidde
"""
import requests
import pandas as pd
import json
import csv
import numpy as np
import time

inputpath= 'YOUR DIRECTORY TO THIS FOLDER'
outputpath= inputpath + '\\capacityfactors\\'

#SELECT COORDINATES
coordinates=pd.read_csv('offshore_fixed_renninja_coordinates.csv')  #Fixed-Bottom offshore wind turbines
# coordinates=pd.read_csv('offshore_float_renninja_coordinates.csv') #Floating wind turbines

#SELECT CSV NAME CORRESPONDING TO COORDINATES
csvname='Offshorewind.csv'
csvname='Floatingwind.csv'

#POWER CURVE 15MW IEA TURBINE
power_curve=pd.read_csv(inputpath + '\\power_curves\\IEA_15MW_offshore.csv')

daterange=pd.read_csv('daterange_renewablesninja.csv')
startdate=daterange['date_from']
enddate=daterange['date_to']
token = 'f9efc2d46a0660186790088ec5e0557215094691'
api_base = 'https://www.renewables.ninja/api/'

s = requests.session()
# Send token header with each request
s.headers = {'Authorization': 'Token ' + token}
height = 150
turbine = 'Vestas V80 2000' #could be any turbine, the wind speed matters
format = 'json'
raw = 'true'

longitudes=coordinates['longitude']
latitudes=coordinates['latitude']
location=coordinates['location']
country=coordinates['Country']
df_list = []

for lat, lon, loc, cou in zip(latitudes, longitudes, location, country):
    for sta, fin in zip(startdate, enddate):
        args = {
            'lat': lat,
            'lon': lon,
            'date_from': sta,
            'date_to': fin,
            'capacity': 1.0,
            'height': height,
            'turbine': turbine,
            'format': format,
            'raw': raw
        }
        r = s.get(api_base + 'data/wind', params=args)
        parsed_response = json.loads(r.text)
        data = pd.read_json(json.dumps(parsed_response['data']), orient='index')
        data['location']=loc
        data['country']=cou
        data=data.drop(['electricity'], axis=1)
        data=data.rename({'wind_speed':'windspeed'},axis=1)
        df_list.append(data)
        df = pd.concat(df_list, ignore_index=False)
        time.sleep(10)

df['time']=df.index
df=np.round(df,decimals=1)
capfactable=df.merge(power_curve, how='left', on='windspeed')
capfactable=capfactable.drop(['windspeed','power'], axis=1)
capfactable=capfactable.groupby(["country","time"])["capfac"].mean()
capfactable=pd.DataFrame(capfactable)
capfactable=capfactable.unstack(level=0)
capfactable.columns=capfactable.columns.droplevel()
capfactable=capfactable.rename(columns={"Denmark":"DNK","France":"FRA","Ireland":"IRL","Norway":"NOR","Sweden":"SWE","UK":"GBR"}) #floating only
capfactable=capfactable.rename(columns={"Netherlands":"NLD","Germany":"DEU","Belgium":"BEL"}) #fixed offshore

capfactable.to_csv(outputpath + csvname) 


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 13:53:32 2023

@author: hidde
"""

import netCDF4 as nc
import pandas as pd
import csv
import datetime
import numpy as np

inputpath= 'YOUR DIRECTORY TO THIS FOLDER'
outputpath= inputpath + '\\capacityfactors\\'

##SELECT POWER CURVE
power_curve=pd.read_csv(inputpath + '\\power_curves\\AWE_fixedwing1.csv')
# power_curve=pd.read_csv(inputpath + '\\power_curves\\AWE_fixedwing2_offshore.csv')

#SELECT CORRECT SET OF COORDINATES
coordinates=pd.read_csv('AWEcoordinates_shallow.csv') #shallow water AWE
# coordinates=pd.read_csv('AWEcoordinates_deep.csv') # deep water AWE

#SELECT CORRECT OUTPUT CSV NAME ACCORDING TO SELECTED POWER CURVE AND COORDINATES
csvname=AWE_shallow_fw1.csv
#csvname=AWE_shallow_fw2.cv
#csvname=AWE_deep_fw1.csv
#csvname=AWE_deep_fw2.csv

westlongitudes=coordinates['west_lon']
eastlongitudes=coordinates['east_lon']
northlatitudes=coordinates['north_lat']
southlatitudes=coordinates['south_lat']
filename=coordinates['location']+'.nc'
filename=filename.tolist()
location=coordinates['location']
location=location.tolist()
country=coordinates['Country']

#%% API REQUEST
output_directory= inputpath + '\\netcdfs\\pressurelevel\\'

import cdsapi
c = cdsapi.Client()
for wlon, elon, nlat, slat, fil in zip(westlongitudes, eastlongitudes, northlatitudes, southlatitudes, filename):
    c.retrieve('reanalysis-era5-pressure-levels',{
        'product_type': 'reanalysis',
        'variable': ['u_component_of_wind', 'v_component_of_wind',],
        'pressure_level': '975',
        'year': [
            '2013', '2014', '2015',
            '2016', '2017', '2018',
        ],
        'month': [
            '01', '02', '03',
            '04', '05', '06',
            '07', '08', '09',
            '10', '11', '12',
        ],
        'day': [
            '01', '02', '03',
            '04', '05', '06',
            '07', '08', '09',
            '10', '11', '12',
            '13', '14', '15',
            '16', '17', '18',
            '19', '20', '21',
            '22', '23', '24',
            '25', '26', '27',
            '28', '29', '30',
            '31',
        ],
        'time': [
            '00:00', '01:00', '02:00',
            '03:00', '04:00', '05:00',
            '06:00', '07:00', '08:00',
            '09:00', '10:00', '11:00',
            '12:00', '13:00', '14:00',
            '15:00', '16:00', '17:00',
            '18:00', '19:00', '20:00',
            '21:00', '22:00', '23:00',
        ],
        'area': [nlat,wlon,slat,elon,],
        'format': 'netcdf', 
        }, output_directory + fil )
    
#%% DATA PROCESSING
datetimeindex=pd.date_range("2013-01-01", periods= 52584, freq="H")

df_list = []
windspeed_avg_location={}

for wlon, elon, nlat, slat, loc, cou, fil in zip(westlongitudes, eastlongitudes, northlatitudes, southlatitudes, location, country, filename):
    data= nc.Dataset(output_directory + fil)
    u = data.variables['u'][:, :, :]
    v = data.variables['v'][:, :, :]
    u=u**2
    v=v**2
    windspeed=np.sqrt(u+v)
    windspeed=windspeed.reshape(52584,4)
    windspeed=pd.DataFrame(windspeed)
    windspeed['windspeed']=windspeed.mean(axis=1)
    windspeed=windspeed['windspeed']
    windspeed=pd.DataFrame(windspeed)
    windspeed=np.round(windspeed,decimals=1)
    windspeedavg=windspeed.mean(axis=0)
    windspeed_avg_location[loc] = windspeedavg['windspeed']
    windspeed['location']=loc
    windspeed['country']=cou
    windspeed['time']=datetimeindex
    df_list.append(windspeed)
    df = pd.concat(df_list, ignore_index=False)
    
capfactable=df.merge(power_curve, how='left', on='windspeed')
capfactable=capfactable.drop(['windspeed','power'], axis=1)
capfactable=capfactable.groupby(["country","time"])["capfac"].mean()
capfactable=pd.DataFrame(capfactable)
capfactable=capfactable.unstack(level=0)
capfactable.columns=capfactable.columns.droplevel()

#rename column to match North Sea Calliope 
capfactable=capfactable.rename(columns={"Denmark":"DNK","France":"FRA","Ireland":"IRL","Norway":"NOR","Sweden":"SWE","UK":"GBR"}) #floating only
capfactable=capfactable.rename(columns={"Netherlands":"NLD","Germany":"DEU","Belgium":"BEL","Luxembourg":"LUX"}) #fixed offshore

#average per country (for your own analysis)
capfacavg=capfactable.mean(axis=0)

##export to CSV, make sure to adjust the name when running a new set of coordinates or a new technology
capfactable.to_csv(outputpath + '\\ERA5_pressurelevel\\'+ csvname)

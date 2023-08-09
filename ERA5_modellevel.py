#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 14 10:59:37 2023

@author: hidde
"""

import netCDF4 as nc
import pandas as pd
import csv
import datetime
import numpy as np

inputpath=r'C:\Users\hidde\Documents\Anaconda\Spyder\WIND DATA COLLECTION'
output_directory= inputpath + '\\netcdfs\\modellevel\\'

##SELECT POWER CURVE
power_curve=pd.read_csv(inputpath + '\\power_curves\\AWE_500kw_softwing.csv')
# power_curve=pd.read_csv(inputpath + '\\power_curves\\AWE_fixedwing1.csv')
# power_curve=pd.read_csv(inputpath + '\\power_curves\\AWE_fixedwing2_offshore.csv')
# power_curve=pd.read_csv(inputpath + '\\power_curves\\AWE_fixedwing2_onshore.csv')
# power_curve=pd.read_csv(inputpath + '\\power_curves\\IEA_15MW_offshore.csv')

coordinates=pd.read_csv('AWEcoordinates_onshore.csv')
westlongitudes=coordinates['west_lon']
eastlongitudes=coordinates['east_lon']
northlatitudes=coordinates['north_lat']
southlatitudes=coordinates['south_lat']
filename=coordinates['location']+'.nc'
filename=filename.tolist()
location=coordinates['location']
location=location.tolist()
country=coordinates['Country']

#%%
# DATA COLLECTION API
import cdsapi
c = cdsapi.Client()
for wlon, elon, nlat, slat, fil in zip(westlongitudes, eastlongitudes, northlatitudes, southlatitudes, filename):
    c.retrieve('reanalysis-era5-complete', {
        'class': 'ea',
        'date': '2013-01-01/to/2018-12-31',
        'expver': '1',
        'levelist': '127',
        'levtype': 'ml',
        'param': '131/132',
        'stream': 'oper',
        'time': '00:00:00/01:00:00/02:00:00/03:00:00/04:00:00/05:00:00/06:00:00/07:00:00/08:00:00/09:00:00/10:00:00/11:00:00/12:00:00/13:00:00/14:00:00/15:00:00/16:00:00/17:00:00/18:00:00/19:00:00/20:00:00/21:00:00/22:00:00/23:00:00',
        'type': 'an',
        'area': [nlat,wlon,slat,elon,],
        'grid': '0.25/0.25',
        'format': 'netcdf',
    }, output_directory + fil )

#%% DATA PROCESSING, run after data collection is completed
datetimeindex=pd.date_range("2013-01-01", periods= 52584, freq="H")

df_list = []
windspeed_avg_location={}

#DATA PROCESSING
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
#capfactable.to_csv(outputpath + '\\capacityfactors\\renewablesninja\\offshorewind_fixed.csv')
outputpath=r'C:\Users\hidde\Documents\Anaconda\Spyder\WIND DATA COLLECTION\capacityfactors'
capfactable.to_csv(outputpath + '\\ERA5_modellevel\\AWE_onshore_ml.csv')





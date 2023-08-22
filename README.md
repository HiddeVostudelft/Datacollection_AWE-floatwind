# WIND-DATA-COLLECTION-CORRECT

This README file provides instructions on how to use the files in this repository to extract wind data from both renewables ninja and ERA5 databases. 
The files in this repository were used for modelling the potential of airborne wind energy (AWE) and floating wind turbines in the north sea region (https://github.com/HiddeVostudelft/North-Sea-Calliope-AWE-floatwind)

ERA5 DOCUMENTATION
More information on ERA5 downloads and how to use CDS API requests: https://confluence.ecmwf.int/display/CKB/ERA5%3A+data+documentation

**Data extraction**
the following scripts can be used to extract wind data.:
-ERA5_modellevel.py, for onshore AWE
-ERA5_pressurelevel.py, for offshore AWE 
-renewablesninja_API.py, for conventional and floating offshore wind

Scripts can be altered to use for other technologies.

Coordinates for individual technologies are provided in the following CSVs:
-AWEcoordinates_deep.csv
-AWEcoordinates_onshore.csv
-AWEcoordinates_shallow.csv
-offshore_fixed_renninja_coordinates.csv
-offshore_float_renninja_coordinates.csv

The coordinates in AWEcoordinates_deep.csv and AWEcoordinates_shallow.csv are the basically same as the coordinates in offshore_fixed_renninja_coordinates.csv and offshore_float_renninja_coordinates.csv, except the AWE coordinates are a grid of 0.25x 0.25 degrees and the offshore coordinates are only one specific coordinate. This is because of the difference in how renewables ninja and ERA5 requests work.

coordinatesAWE.csv includes all coordinates used for AWE.

**ERA5 modellevel.py**
ERA5 DOCUMENTATION: More information on ERA5 downloads and how to use CDS API requests: https://confluence.ecmwf.int/display/CKB/ERA5%3A+data+documentation

#PATHS AND SETTINGS FOR ONSHORE AWE (line 16-20)
Here the input and output paths are defined, as well as the name of the output file and the power curve that was used.

In line 22, the coordinates are imported. In this case for onshore AWE.

Line 23-31: standard settings corresponding to the format of the coordinates csv.

#DATA COLLECTION API (line 34-52) 
Run this section separately before running the rest of the code!

Define the date in line 41
Define the model level in line 43 (The model levels correspond to a certain altitude and can be found in the ERA5 Documentation.)

The output netcdf files go to the netcdfs>modellevel folder, as defined in line 35
#DATA PROCESSING (line 54 - 98)
Run after data collection is completed!

Here the data gets processed. Important to check whether the range defined in the API request (line 41) corresponds to the date range defined in line 55.


**ERA5 pressurelevel.py** 
ERA5 DOCUMENTATION:More information on ERA5 downloads and how to use CDS API requests: https://confluence.ecmwf.int/display/CKB/ERA5%3A+data+documentation

The structure is the same as the ERA5_modellevel.py script, but the API works slightly different
Now, you have to choose the powercurve,coordinates and output csv name in line 20-32
Make sure the power curve and coordinates correspond to the csv name. 

#API request (line 44)
The output netcdf files for the API request go to the netcdfs>modellevel folder, as defined in line 45
Run this section separately before running the rest of the code!

**renewablesninja_API.py**
RENEWABLES NINJA DOCUMENTATION: https://www.renewables.ninja/documentation

Make sure to select the desired coordinates again
The date range is defined in daterange_renewablesninja.csv (line 31)
The hub height is 150m (line 40)
The type of turbine is defined at random, because the only thing of interest isthe raw wind data (line 41-43)

PLEASE BE AWARE: you have to request an increase in usage limit (requests per hour). https://www.renewables.ninja/documentation explains how to do this
line 73 puts a delay in the for loop for the API request, you can adjust this to stay within user limits. 





#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Brent
#
# Created:     25/07/2016
# Copyright:   (c) Brent 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import math
from geographiclib.geodesic import Geodesic

#Setup WGS84 Ellipsoid
geod = Geodesic.WGS84

station_1 = ['33 48.1154N', '118 23.8991W'] #Palos Verdes, CA
station_2 = ['34 2.5073N', '118 42.376W'] #Malibu, CA (Pepperdine University)

def ConvertDecDecToDecDegreeLat(gps_lat):
    #Split decimal-decimal lattitude string
    gps_lat_split = gps_lat.split(" ")
    #Append lattitude direction to list
    gps_lat_split.append(gps_lat_split[1][len(gps_lat_split[1])-1])
    #remove lattitude direction from non direction list index
    gps_lat_split[1] = gps_lat_split[1][0:len(gps_lat_split[1])-1]
    #Assign direction polarity
    if(gps_lat_split[2]== "N"):
        lat_polarity = 1
    elif(gps_lat_split[2] == "S"):
        lat_polarity = -1
    else:
        return False #Error

    #remove lattitude polarity


    lattitude = lat_polarity*(float(gps_lat_split[0])+float(gps_lat_split[1])/60)
    return lattitude

def ConvertDecDecToDecDegreeLon(gps_long):
    #Split decimal-decimal lattitude string
    gps_long_split = gps_long.split(" ")
    #Append lattitude direction to list
    gps_long_split.append(gps_long_split[1][len(gps_long_split[1])-1])
    #remove lattitude direction from non direction list index
    gps_long_split[1] = gps_long_split[1][0:len(gps_long_split[1])-1]
    #Assign direction polarity
    if(gps_long_split[2]== "E"):
        long_polarity = 1
    elif(gps_long_split[2] == "W"):
        long_polarity = -1
    else:
        return False #Error

    #remove lattitude polarity


    longitude = long_polarity*(float(gps_long_split[0])+float(gps_long_split[1])/60)
    return longitude

def ConvertNmeaToDecDegreeLatLon(lattitude, longitude):
    lattitude_convert = convert_raw_gps_nmea_to_lat(lattitude)
    longitude_convert = convert_raw_gps_nmea_to_long(longitude)
    return [lattitude_convert, longitude_convert]

##def calc_distant_stations_miles(lat_1, long_1, lat_2, long_2):
##    '''Calculate the distance between two cordinates. This finds the distance from cordinate 1 to cordinate 2.
##    Note: This assumes earth is a perfect sphere!'''
##    earth_r = 3961 #Miles
##    dlon = long_2 - long_1
##    dlat = lat_2 - lat_1
##    a = (math.sin(dlat/2))**2 + math.cos(lat_1)*math.cos(lat_2)*(math.sin(dlon/2))**2
##    c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
##    d = earth_r*c
##
##    #Return final distance in miles
##    return d

def CalcDistanceBetweenTwoLatLonMeters(lat_1, long_1, lat_2, long_2):
    '''Calculate the distance between two cordinates from point 1 to point 2'''
    geod_inverse = geod.Inverse(lat_1, long_1, lat_2, long_2)
    return geod_inverse['s12']

def CalcBearingBetweenTwoLatLon(lat_1, long_1, lat_2, long_2):
    '''Calculate the compass bearing between two cordinates from point 1 to point 2 (true north)'''
    geod_inverse = geod.Inverse(lat_1, long_1, lat_2, long_2)
    raw_azimuth = geod_inverse['azi1'] #Choose AZI1 instead of AZI2 (the two solutions on the spherefrom two points)
    #Convert to 360 degree bearing
    if(raw_azimuth>=0):
        bearing_degrees = raw_azimuth
    else:
        bearing_degrees = 360 + raw_azimuth
    #Return bearing in degrees
    return bearing_degrees


def GetDistanceBearingBetweenTwoPointsMeters(lat_1, long_1, lat_2, long_2):
    distance = CalcDistanceBetweenTwoLatLonMeters(lat_1, long_1, lat_2, long_2)
    bearing = CalcBearingBetweenTwoLatLon(lat_1, long_1, lat_2, long_2)
    return [round(distance,1), int(round(bearing,0))]

def GetDistanceBearingBetweenTwoPointsKm(lat_1, long_1, lat_2, long_2):
    result = GetDistanceBearingBetweenTwoPointsMeters(lat_1, long_1, lat_2, long_2)
    #Convert to KM
    result[0] = round(result[0]/1000,1)
    return result

def GetDistanceBearingBetweenTwoPointsMiles(lat_1, long_1, lat_2, long_2):
    result = GetDistanceBearingBetweenTwoPointsMeters(lat_1, long_1, lat_2, long_2)
    #Convert to Miles
    result[0] = round(result[0]*0.000621371,1)
    return result

import requests
import base64
import json
import time
import ConfigParser
import os
import logging.config


# Start logging after importing modules
logging.config.fileConfig('loggingConfig.ini')
logger = logging.getLogger('SimpleUI')

# Open configuration INI
config = ConfigParser.RawConfigParser()
filename = os.path.abspath("simpleui.ini")
config.read(filename)

telemhost = config.get('FLASKTELEM', 'HOST')
telemport = int(config.get('FLASKTELEM', 'PORT'))

localcallsign = config.get('UNITS', 'UNIT0CALL')
localnodeid = int(config.get('UNITS', 'UNIT0ID'))



def getStations():
    """
    Queries telemetry server for active stations

    :return: JSON results from request
    """

    # Construct station URL and query for active stations
    url = "http://" + str(telemhost) + ":" + str(telemport) + "/stations"
    logger.debug(url)

    r = requests.get(url)
    results = r.json()

    # Return extracted JSON data
    return results

def getStationData(stations, age):
    """
    Queries telemetry server for detailed telemetry from active stations

    :param stations: List of callsign + nodeids to get telemetry data from
    :return: list containing latest station telemetry
    """

    # Initialize lists
    stationData = []

    #age = aprsConfig.getint('APRSIS', 'STATIONSAGE')

    # Construct base URL to get station data from telemetry server
    url = "http://" + str(telemhost) + ":" + str(telemport) + "/"

    # Iterate through each station and request latest telemetry data entry
    for station in stations:
        # Extract station identification data from active stations
        callsign = station["SOURCECALLSIGN"]
        nodeid = station["SOURCEID"]

        # Construct request dictionary payload
        payload = {"callsign": callsign, "nodeid": nodeid, "timespan": age, "limit": 1}

        # Request data, append to stationData list
        try:
            r = requests.get(url, params=payload)
            data = r.json()

        except requests.exceptions.RequestException as e:
            logger.error(e)

        else:
            stationData.append(data)

    # Return all detailed stationData
    return stationData

units = getStations()
print getStationData(units, 60)
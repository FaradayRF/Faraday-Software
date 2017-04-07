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

print getStations()
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

    # Return on single dictionary
    stationData = stationData[0][0]
    # Return all detailed stationData
    return stationData

def displayData(telempacket):

    #print len(telempacket)
    #print telempacket
    print "Callsign ----- ", telempacket['SOURCECALLSIGN'] + '-' + str(telempacket['SOURCEID'])
    print "GPS Altitude ----- ", telempacket['GPSALTITUDE']
    # print "Source Callsign Length", dictionaryData['SOURCECALLSIGNLEN']
    # print "Source Callsign ID", dictionaryData['SOURCEID']
    # print "Destination Callsign", dictionaryData['DESTINATIONCALLSIGN']
    # print "Destination Callsign Length", dictionaryData['DESTINATIONCALLSIGNLEN']
    # print "Destination Callsign ID", dictionaryData['DESTINATIONID']
    # print "RTC Second", dictionaryData['RTCSEC']
    # print "RTC Minute", dictionaryData['RTCMIN']
    # print "RTC Hour", dictionaryData['RTCHOUR']
    # print "RTC Day", dictionaryData['RTCDAY']
    # print "RTC Day Of Week", dictionaryData['RTCDOW']
    # print "RTC Month", dictionaryData['RTCMONTH']
    # print "Year", dictionaryData['RTCYEAR']
    # print "GPS Lattitude", dictionaryData['GPSLATITUDE']
    # print "GPS Lattitude Direction", dictionaryData['GPSLATITUDEDIR']
    # print "GPS Longitude", dictionaryData['GPSLONGITUDE']
    # print "GPS Longitude Direction", dictionaryData['GPSLONGITUDEDIR']
    # print "GPS Altitude", dictionaryData['GPSALTITUDE']
    # print "GPS Altitude Units", dictionaryData['GPSALTITUDEUNITS']
    # print "GPS Speed", dictionaryData['GPSSPEED']
    # print "GPS Fix", dictionaryData['GPSFIX']
    # print "GPS HDOP", dictionaryData['GPSHDOP']
    # print "GPIO State Telemetry", dictionaryData['GPIOSTATE']
    # print "IO State Telemetry", dictionaryData['IOSTATE']
    # print "RF State Telemetry", dictionaryData['RFSTATE']
    # print "ADC 0", dictionaryData['ADC0']
    # print "ADC 1", dictionaryData['ADC1']
    # print "ADC 2", dictionaryData['ADC2']
    # print "ADC 3", dictionaryData['ADC3']
    # print "ADC 4", dictionaryData['ADC4']
    # print "ADC 5", dictionaryData['ADC5']
    # print "VCC", dictionaryData['VCC']
    # print "CC430 Temperature", dictionaryData['BOARDTEMP']
    # print "ADC 8", dictionaryData['ADC8']
    # # print "N/A Byte", dictionaryData['']
    # print "HAB Automatic Cutdown Timer State Machine State", dictionaryData['HABTIMERSTATE']
    # print "HAB Cutdown Event State Machine State", dictionaryData['HABCUTDOWNSTATE']
    # print "HAB Automatic Cutdown Timer Trigger Time", dictionaryData['HABTRIGGERTIME']
    # print "HAB Automatic Cutdown Timer Current Time", dictionaryData['HABTIMER']
    # print "EPOCH", dictionaryData['EPOCH']


def main():
    """
    Main function which starts telemery worker thread + Flask server.

    :return: None
    """

    logger.info('Starting Faraday SimpleUI application')

    while True:
        telempacket = getStationData(getStations(), 60)
        displayData(telempacket)
        time.sleep(1)




if __name__ == '__main__':
    main()
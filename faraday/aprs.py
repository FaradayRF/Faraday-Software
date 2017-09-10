#-------------------------------------------------------------------------------
# Name:        /faraday/aprs.py
# Purpose:      Query telemetry server for station data to send to an APRS-IS
#               socket connection. Currently provide only one way data flow
#
# Author:      Bryce Salmi
#
# Created:     12/4/2016
# Licence:     GPLv3
#-------------------------------------------------------------------------------

import threading
import ConfigParser
import socket
import requests
import os
from time import sleep
import sys
import argparse
from aprslib import base91

from classes import helper

configTruthFile = "aprs.sample.ini"
configFile = "aprs.ini"

# Start logging after importing modules
faradayHelper = helper.Helper("APRS")
logger = faradayHelper.getLogger()


aprsConfig = ConfigParser.RawConfigParser()
aprsConfig.read(faradayHelper.path)

# Command line input
parser = argparse.ArgumentParser(description='APRS application queries Faraday telemetry server and uploads data to APRS-IS')
parser.add_argument('--init-config', dest='init', action='store_true', help='Initialize APRS configuration file')
parser.add_argument('--callsign', help='Set APRS-IS callsign for passcode generation')
parser.add_argument('--server', help='Set APRS-IS server address')
parser.add_argument('--port', help='Set APRS-IS server port')
parser.add_argument('--rate', help='Set APRS-IS update rate in seconds')
parser.add_argument('--stationsage', help='Set age station date can be to send to APRS-IS in seconds')
parser.add_argument('--comment', help='Set APRS comment for nodes, use quotes (43 characters maximum)')
parser.add_argument('--altcomment', help='Set APRS alternate comment for access points, use quotes (43 characters maximum)')
parser.add_argument('--start', action='store_true', help='Start APRS server')

# Parse the arguments
args = parser.parse_args()


def initializeAPRSConfig():
    '''
    Initialize APRS configuration file from aprs.sample.ini

    :return: None, exits program
    '''

    faradayHelper.initializeConfig(configTruthFile, configFile)
    sys.exit(0)


def configureAPRS(args):
    '''
    Configure aprs configuration file from command line

    :param args: argparse arguments
    :return: None
    '''

    config = ConfigParser.RawConfigParser()
    config.read(os.path.join(faradayHelper.path, configFile))

    if args.callsign is not None:
        config.set('APRSIS', 'CALLSIGN', args.callsign)
    if args.server is not None:
        config.set('APRSIS', 'SERVER', args.server)
    if args.port is not None:
        config.set('APRSIS', 'PORT', args.port)
    if args.rate is not None:
        config.set('APRSIS', 'RATE', args.rate)
    if args.stationsage is not None:
        config.set('APRSIS', 'STATIONSAGE', args.stationsage)
    if args.comment is not None:
        config.set('APRS', 'COMMENT', args.comment[:43])
    if args.altcomment is not None:
        config.set('APRS', 'ALTCOMMENT', args.altcomment[:43])

    filename = os.path.join(faradayHelper.path, configFile)
    with open(filename, 'wb') as configfile:
        config.write(configfile)


def aprs_worker(config, sock):
    """
    Obtains telemetry with infinite loop, forwards to APRS-IS server

    :param config: Configuration file descriptor from aprs.INI
    :param sock: Internet socket
    :return: None
    """
    logger.debug('Starting aprs_worker thread')
    rate = config.getint("APRSIS", "RATE")

    # Local variable initialization
    telemSequence = 0
    conn = False

    # Start infinite loop to send station data to APRS-IS
    while True:
        # Query telemetry database for station data
        stations = getStations()
        stationData = getStationData(stations)

        # Indicate number of stations tracking
        str = "Tracking {0} Faraday stations..."
        logger.info(str.format(len(stations)))

        # Iterate through all stations sending telemetry and position data
        if not conn:
            sock = connectAPRSIS()
        try:
            conn = sendPositions(telemSequence, stationData, sock)

            # Just send labels, Parameters, and Equations every 10th loop
            if telemSequence % 10 == 0:
                sendTelemLabels(stationData, sock)
                sendParameters(stationData, sock)
                sendEquations(stationData, sock)
            telemSequence += 1

        except StandardError as e:
            logger.error(e)

        # Sleep for intended update rate (seconds)
        sleep(rate)


# Now act upon the command line arguments
# Initialize and configure aprs
if args.init:
    initializeAPRSConfig()
configureAPRS(args)

# Read in APRS configuration parameters
aprsFile = aprsConfig.read(os.path.join(faradayHelper.path, configFile))

# Check for --start option and exit if not present
if not args.start:
    logger.warning("--start option not present, exiting APRS server!")
    sys.exit(0)


def getStations():
    """
    Queries telemetry server for active stations

    :return: JSON results from request
    """

    # Read configuration to query telemetry server
    host = aprsConfig.get("TELEMETRY", "HOST")
    port = aprsConfig.get("TELEMETRY", "PORT")

    # Construct station URL and query for active stations
    url = "http://" + host + ":" + port + "/stations"
    logger.debug(url)

    r = requests.get(url)
    results = r.json()

    # Return extracted JSON data
    return results


def getStationData(stations):
    """
    Queries telemetry server for detailed telemetry from active stations

    :param stations: List of callsign + nodeids to get telemetry data from
    :return: list containing latest station telemetry
    """

    # Initialize lists
    stationData = []

    # Read configuration to query telemetry server
    host = aprsConfig.get("TELEMETRY", "HOST")
    port = aprsConfig.get("TELEMETRY", "PORT")
    age = aprsConfig.getint('APRSIS', 'STATIONSAGE')

    # Construct base URL to get station data from telemetry server
    url = "http://" + host + ":" + port + "/"

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


def nmeaToDegDecMin(latitude, longitude):
    """
    Converts NMEA string latitude and longitude data into degree decimal minutes data compatible with
    APRS-IS server requirements per APRS Protocol Version 1.0

    :param latitude: NMEA latitude string
    :param longitude: NMEA longitude string
    :return: list of latitude and longitude strings per APRS protocol version 1
    """

    # Convert NMEA to Decimal Degrees
    latDeg = latitude[:2]  # latitude degrees
    lonDeg = longitude[:3]  # Longitude degrees
    latDec = round(float(latitude[2:]), 2)  # Latitude decimal minutes
    lonDec = round(float(longitude[3:]), 2)  # Longitude decimal minutes

    # round decimal minutes to 2 dec places & make 5 characters, zero fill
    latDec = str("%.2f" % latDec).zfill(5)
    lonDec = str("%.2f" % lonDec).zfill(5)

    # Combine into APRS-IS compliant lat/lon position
    latString = latDeg + str(latDec)
    lonString = lonDeg + str(lonDec)

    return [latString, lonString]


def sendAPRSPacket(socket, packet):
    """
    Sends an APRS packet (just a string) to the socket specified. If an
    error occurs a False is returned while a True is returned if successful.
    On an error, the socket is closed as it is no longer useful.

    :param socket: APRS-IS server internet socket
    :param packet: String to be sent to APRS-IS
    :return: Boolean
    """

    try:
        socket.sendall(packet)
        return True

    except IOError as e:
        logger.error(e)
        socket.close()
        return False


def sendPositions(telemSequence, stations, socket):
    """
    Constructs an APRS position string for station and sends to a socket.
    Includes BASE91 comment telemetry functionality as well.

    :param telemSequence: Telemetry sequence number
    :param stations: List of dictionary organized station data
    :param socket: APRS-IS server internet socket
    :return: None
    """

    # Iterate through each station and generate an APRS position string
    # then send the string to the socket for each station in list
    for item in stations:
        station = item[0]

        # Get Station data from GPS data
        sourceCallsign = station["SOURCECALLSIGN"]
        sourceID = station["SOURCEID"]
        destinationCallsign = station["DESTINATIONCALLSIGN"]
        destinationID = station["DESTINATIONID"]
        latitude = station["GPSLATITUDE"]
        longitude = station["GPSLONGITUDE"]
        latitudeDirection = station["GPSLATITUDEDIR"]
        longitudeDir = station["GPSLONGITUDEDIR"]
        altitude = station["GPSALTITUDE"]
        speed = station["GPSSPEED"]
        gpsFix = station["GPSFIX"]

        # Get APRS configuration
        qConstruct = aprsConfig.get('APRS', 'QCONSTRUCT')
        dataTypeIdent = aprsConfig.get('APRS', 'DATATYPEIDENT')
        destAddress = aprsConfig.get('APRS', 'DESTADDRESS')
        symbolTable = aprsConfig.get('APRS', 'SYMBOLTABLE')
        symbol = aprsConfig.get('APRS', 'SYMBOL')
        altSymbolTable = aprsConfig.get('APRS', 'ALTSYMBOLTABLE')
        altSymbol = aprsConfig.get('APRS', 'ALTSYMBOL')
        comment = aprsConfig.get('APRS', 'COMMENT')
        altComment = aprsConfig.get('APRS', 'ALTCOMMENT')
        ioSource = aprsConfig.get('APRS', 'IOSOURCE').upper()

        # Create nodes from GPS data
        node = sourceCallsign + "-" + str(sourceID)
        destNode = destinationCallsign + "-" + str(destinationID)

        #Obtain GPIO data
        gpioValues = station["GPIOSTATE"]
        rfValues = station["RFSTATE"]

        # Extract IO data
        if ioSource == 'GPIO':
            ioList = gpioValues
        elif ioSource == 'RF':
            ioList = rfValues

        # Generate BASE91 telemetry with aprslib using a width of 2
        b91seq = base91.from_decimal(telemSequence, 2)
        b91a = base91.from_decimal(station["ADC0"], 2)
        b91b = base91.from_decimal(station["ADC1"], 2)
        b91c = base91.from_decimal(station["ADC3"], 2)
        b91d = base91.from_decimal(station["ADC6"], 2)
        b91e = base91.from_decimal(station["BOARDTEMP"], 2)
        b91f = base91.from_decimal(ioList, 2)

        b91Tlm = "|{0}{1}{2}{3}{4}{5}{6}|".format(b91seq, b91a, b91b, b91c, b91d, b91e, b91f)

        # add telemetry to comments
        comment = comment + b91Tlm
        altComment = altComment + b91Tlm

        # Convert position to APRS-IS compliant string
        latString, lonString = nmeaToDegDecMin(latitude, longitude)

        # Convert altitude and speed to APRS compliant values
        try:
            rawaltitude = str(round(altitude, 0)).split('.')
            rawspeed = str(round(speed, 0)).split('.')

        except TypeError as e:
            logger.error(e)
            logger.error(altitude)
            logger.error(speed)

        else:
            altitude = rawaltitude[0].zfill(6)
            speed = rawspeed[0].zfill(3)

            # If GPSFix is not valid warn user
            if gpsFix <= 0:
                logger.debug(node + " No GPS Fix")

            if node != destNode:
                # APRS string is for remote RF node
                aprsPosition = ''.join([
                    dataTypeIdent,
                    latString,
                    latitudeDirection,
                    symbolTable,
                    lonString,
                    longitudeDir,
                    symbol])

                positionString = '{}>{},{},{}:{}.../{}/A={}{}\r'.format(
                    node,
                    destAddress,
                    qConstruct,
                    destNode,
                    aprsPosition,
                    speed,
                    altitude,
                    comment)

                logger.debug(positionString)

                status = sendAPRSPacket(socket, positionString)
                return status

            elif node == destNode:
                # APRS string is for local node
                aprsPosition = ''.join([
                    dataTypeIdent,
                    latString,
                    latitudeDirection,
                    altSymbolTable,
                    lonString,
                    longitudeDir,
                    altSymbol])
                positionString = '{}>{}:{}.../{}/A={}{}\r'.format(
                    node,
                    destAddress,
                    aprsPosition,
                    speed,
                    altitude,
                    altComment)
                logger.debug(positionString)

                status = sendAPRSPacket(socket, positionString)
                return status


def sendtelemetry(stations, telemSequence, socket):
    """
    Constructs an APRS telemetry string for each station and sends it to the socket

    :param stations: List of dictionary organized station data
    :param telemSequence: Telemetry sequence number from 0 to 999, incrementing
    :param socket: APRS-IS server internet socket
    :return: None
    """

    for item in stations:
        station = item[0]

        # Get Station data from GPS data
        sourceCallsign = station["SOURCECALLSIGN"]
        sourceID = station["SOURCEID"]
        destinationCallsign = station["DESTINATIONCALLSIGN"]
        destinationID = station["DESTINATIONID"]
        gpioValues = station["GPIOSTATE"]
        rfValues = station["RFSTATE"]

        # Get APRS Telemetry configuration
        qConstruct = aprsConfig.get('APRS', 'QCONSTRUCT')
        destAddress = aprsConfig.get('APRS', 'DESTADDRESS')
        ioSource = aprsConfig.get('APRS', 'IOSOURCE').upper()

        # Extract IO data
        if ioSource == 'GPIO':
            ioList = bin(gpioValues)[2:].zfill(8)
        elif ioSource == 'RF':
            ioList = bin(rfValues)[2:].zfill(8)

        # Create nodes from GPS data
        node = sourceCallsign + "-" + str(sourceID)
        destNode = destinationCallsign + "-" + str(destinationID)

        if node != destNode:
            # APRS string is for remote RF node
            telemetry = '{}>{},{},{}:T#{},{},{},{},{},{},{}\r'.format(
                node,
                destAddress,
                qConstruct,
                destNode,
                str(telemSequence).zfill(3),
                str(station["ADC0"] / 16).zfill(3),
                str(station["ADC1"] / 16).zfill(3),
                str(station["ADC3"] / 16).zfill(3),
                str(station["ADC6"] / 16).zfill(3),
                str(station["BOARDTEMP"] / 16).zfill(3),
                ioList)

            logger.debug(telemetry)

            status = sendAPRSPacket(socket, telemetry)
            return status

        elif node == destNode:
            # APRS string is for local node
            telemetry = '{}>{}:T#{},{},{},{},{},{},{}\r'.format(
                node,
                destAddress,
                str(telemSequence).zfill(3),
                str(station["ADC0"] / 16).zfill(3),
                str(station["ADC1"] / 16).zfill(3),
                str(station["ADC3"] / 16).zfill(3),
                str(station["ADC6"] / 16).zfill(3),
                str(station["BOARDTEMP"] / 16).zfill(3),
                ioList)

            logger.debug(telemetry)

            status = sendAPRSPacket(socket, telemetry)
            return status

        # Check for telemetry sequence rollover
        if telemSequence >= 999:
            telemSequence = 0
        else:
            telemSequence += 1
        # Return telemetrySequence to save count
        return telemSequence


def sendTelemLabels(stations, socket):
    """
    Constructs an APRS unit/label string for each station and sends it to the socket

    :param stations: List of dictionary organized station data
    :param socket: APRS-IS server internet socket
    :return: None
    """

    for item in stations:
        station = item[0]

        # Get Station data from GPS data
        sourceCallsign = station["SOURCECALLSIGN"]
        sourceID = station["SOURCEID"]
        destinationCallsign = station["DESTINATIONCALLSIGN"]
        destinationID = station["DESTINATIONID"]

        # Get APRS Telemetry configuration
        qConstruct = aprsConfig.get('APRS', 'QCONSTRUCT')
        destAddress = aprsConfig.get('APRS', 'DESTADDRESS')

        # Get units and labels from configuration file
        unit0 = aprsConfig.get('APRS', 'UNIT0')
        unit1 = aprsConfig.get('APRS', 'UNIT1')
        unit2 = aprsConfig.get('APRS', 'UNIT2')
        unit3 = aprsConfig.get('APRS', 'UNIT3')
        unit4 = aprsConfig.get('APRS', 'UNIT4')
        bLabel0 = aprsConfig.get('APRS', 'BLABEL0')
        bLabel1 = aprsConfig.get('APRS', 'BLABEL1')
        bLabel2 = aprsConfig.get('APRS', 'BLABEL2')
        bLabel3 = aprsConfig.get('APRS', 'BLABEL3')
        bLabel4 = aprsConfig.get('APRS', 'BLABEL4')
        bLabel5 = aprsConfig.get('APRS', 'BLABEL5')
        bLabel6 = aprsConfig.get('APRS', 'BLABEL6')
        bLabel7 = aprsConfig.get('APRS', 'BLABEL7')

        unitsAndLabels = ','.join([
            unit0[:6], unit1[:6], unit2[:5], unit3[:5], unit4[:4],
            bLabel0[:5], bLabel1[:4], bLabel2[:3], bLabel3[:3],
            bLabel4[:3], bLabel5[:2], bLabel6[:2], bLabel7[:2]])

        # Create nodes from GPS data
        node = sourceCallsign + "-" + str(sourceID)
        destNode = destinationCallsign + "-" + str(destinationID)

        if node != destNode:
            # APRS string is for remote node
            labels = '{}>{},{},{}::{} :UNIT.{}\r'.format(
                node, destAddress, qConstruct, destNode, node, unitsAndLabels)
            logger.debug(labels)

            status = sendAPRSPacket(socket, labels)
            return status

        elif node == destNode:
            # APRS string is for local node
            labels = '{}>{}::{} :UNIT.{}\r'.format(
                node, destAddress, node, unitsAndLabels)

            status = sendAPRSPacket(socket, labels)
            return status


def sendParameters(stations, socket):
    """
    Constructs an APRS parameters string for each station and sends it to the socket

    :param stations: List of dictionary organized station data
    :param socket: APRS-IS server internet socket
    :return:
    """

    for item in stations:
        station = item[0]

        # Get Station data from GPS data
        sourceCallsign = station["SOURCECALLSIGN"]
        sourceID = station["SOURCEID"]
        destinationCallsign = station["DESTINATIONCALLSIGN"]
        destinationID = station["DESTINATIONID"]

        # Get APRS Telemetry configuration
        qConstruct = aprsConfig.get('APRS', 'QCONSTRUCT')
        destAddress = aprsConfig.get('APRS', 'DESTADDRESS')

        adc0 = aprsConfig.get('APRS', 'ADC0PARAM')
        adc1 = aprsConfig.get('APRS', 'ADC1PARAM')
        adc2 = aprsConfig.get('APRS', 'ADC2PARAM')
        adc3 = aprsConfig.get('APRS', 'ADC3PARAM')
        adc4 = aprsConfig.get('APRS', 'ADC4PARAM')
        io0 = aprsConfig.get('APRS', 'IO0PARAM')
        io1 = aprsConfig.get('APRS', 'IO1PARAM')
        io2 = aprsConfig.get('APRS', 'IO2PARAM')
        io3 = aprsConfig.get('APRS', 'IO3PARAM')
        io4 = aprsConfig.get('APRS', 'IO4PARAM')
        io5 = aprsConfig.get('APRS', 'IO5PARAM')
        io6 = aprsConfig.get('APRS', 'IO6PARAM')
        io7 = aprsConfig.get('APRS', 'IO7PARAM')

        adcAndIoParams = ','.join([
            adc0[:6], adc1[:6], adc2[:5], adc3[:5], adc4[:4],
            io0[:5], io1[:4], io2[:3], io3[:3],
            io4[:3], io5[:2], io6[:2], io7[:2]])

        # Create nodes from GPS data
        node = sourceCallsign + "-" + str(sourceID)
        destNode = destinationCallsign + "-" + str(destinationID)

        if node != destNode:
            # APRS string is for remote node
            parameters = '{}>{},{},{}::{} :PARM.{}\r'.format(
                node, destAddress, qConstruct, destNode, node, adcAndIoParams)

            status = sendAPRSPacket(socket, parameters)
            return status

        elif node == destNode:
            # APRS string is for local node
            parameters = '{}>{}::{} :PARM.{}\r'.format(
                node, destAddress, node, adcAndIoParams)

            status = sendAPRSPacket(socket, parameters)
            return status


def sendEquations(stations, socket):
    """
    Constructs an APRS equation string for each station and sends it to the socket

    :param stations: List of dictionary organized station data
    :param socket: APRS-IS server internet socket
    :return: None
    """

    for item in stations:
        station = item[0]

        # Get Station data from GPS data
        sourceCallsign = station["SOURCECALLSIGN"]
        sourceID = station["SOURCEID"]
        destinationCallsign = station["DESTINATIONCALLSIGN"]
        destinationID = station["DESTINATIONID"]

        # Get APRS Telemetry configuration
        qConstruct = aprsConfig.get('APRS', 'QCONSTRUCT')
        destAddress = aprsConfig.get('APRS', 'DESTADDRESS')

        # Get equations from configuration file
        equationConfig = ','.join([
            str(aprsConfig.get('APRS', 'EQ0A')),
            str(aprsConfig.get('APRS', 'EQ0B')),
            str(aprsConfig.get('APRS', 'EQ0C')),
            str(aprsConfig.get('APRS', 'EQ1A')),
            str(aprsConfig.get('APRS', 'EQ1B')),
            str(aprsConfig.get('APRS', 'EQ1C')),
            str(aprsConfig.get('APRS', 'EQ2A')),
            str(aprsConfig.get('APRS', 'EQ2B')),
            str(aprsConfig.get('APRS', 'EQ2C')),
            str(aprsConfig.get('APRS', 'EQ3A')),
            str(aprsConfig.get('APRS', 'EQ3B')),
            str(aprsConfig.get('APRS', 'EQ3C')),
            str(aprsConfig.get('APRS', 'EQ4A')),
            str(aprsConfig.get('APRS', 'EQ4B')),
            str(aprsConfig.get('APRS', 'EQ4C'))
        ])

        # Create nodes from GPS data
        node = sourceCallsign + "-" + str(sourceID)
        destNode = destinationCallsign + "-" + str(destinationID)

        if node != destNode:
            # APRS string is for remote node
            equations = '{}>{},{},{}::{} :EQNS.{}\r'.format(
                node, destAddress, qConstruct, destNode, node, equationConfig)

            status = sendAPRSPacket(socket, equations)
            return status

        elif node == destNode:
            # APRS string is for local node
            equations = '{}>{}::{} :EQNS.{}\r'.format(
                node, destAddress, node, equationConfig)

            status = sendAPRSPacket(socket, equations)
            return status


def connectAPRSIS():
    """
    Connect to APRS-IS server with login credentials

    :return: APRS-IS socket connection
    """

    # Read APRS-IS login credentials from configuration file
    callsign = aprsConfig.get('APRSIS', 'CALLSIGN').upper()

    # APRS-IS passcode generator
    passcode = generatePasscode(callsign)

    # Read APRS-IS server address from configuration file
    server = aprsConfig.get("APRSIS", "SERVER")
    port = aprsConfig.getint("APRSIS", "PORT")

    if passcode is not None:
        logger.info("Connecting to APRS-IS as: " + str(callsign))
        logger.debug("Server: " + str(server) + ":" + str(port))

        # Set socket up
        aprssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Infinite loop until connection is successful
        while True:
            try:
                # Create login string and connect to server
                logon_string = 'user' + ' ' + callsign + ' ' + 'pass' + ' ' + str(
                    passcode) + ' vers "FaradayRF APRS-IS application" \r'
                logger.debug(logon_string)
                aprssock.connect((server, port))
                aprssock.sendall(logon_string)

            except IOError as e:
                # Close socket and setup for next connection attempt
                logger.error(e)
                aprssock.close()
                aprssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            else:
                logger.info("Connection successful!")
                return aprssock
                break

            sleep(2)  # Try to reconnect every 10 seconds
        return aprssock
    else:
        while True:
            logger.error("APRS-IS LOGIN ERROR!")
            sleep(1)


def generatePasscode(callsign):
    """
    Generates an APRS-IS compliant passcode.

    Based on the open-source work of magicbug at https://github.com/magicbug/PHP-APRS-Passcode. Thanks!

    :param callsign: Uppercase callsign string
    :return: APRS-IS Passcode if successful, None if error
    """
    # Initialize variables
    callhash = None
    i = 0

    # Convert callsign to list and obtain length
    callList = list(callsign)
    if len(callList) % 2 != 0:
        callList.append('\0')
    length = len(callList)

    # Perform hash if length is valid
    if length <= 10 and length > 1 and not(callsign == "REPLACEME"):
        callhash = 0x73e2  # Set hash seed

        while (i < length):
            try:
                callhash ^= ord(callList[i]) << 8
                callhash ^= ord(callList[i + 1])
                i += 2

            except StandardError as e:
                logger.error(e)
                callhash = None
                break

        if callhash is not None:
            callhash = callhash & 0x7ffff  # Ensure passcode is always positive

    else:
        # Callsign is wrong length
        logger.error("Callsign '{0}' invalid!".format(callsign))

    # Return hash as passcode or None if the operation was erroneous
    logger.debug("'{0}' APRS-IS Passcode: {1}".format(callsign, callhash))
    return callhash


def main():
    """
    Main function which starts telemery worker thread + Flask server.

    :return: None
    """

    logger.info('Starting Faraday APRS-IS application')
    #sock = connectAPRSIS()
    sock = ''

    # Initialize local variables
    threads = []

    t = threading.Thread(target=aprs_worker, args=(aprsConfig, sock))
    threads.append(t)
    t.start()


if __name__ == '__main__':
    main()

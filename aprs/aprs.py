#-------------------------------------------------------------------------------
# Name:        /aprs/aprs.py
# Purpose:      Query telemetry server for station data to send to an APRS-IS
#               socket connection. Currently provide only one way data flow
#
# Author:      Bryce Salmi
#
# Created:     12/4/2016
# Licence:     GPLv3
#-------------------------------------------------------------------------------

import time
import logging
import logging.config
import threading
import ConfigParser
from collections import deque
import os
import sys
#import sqlite3
import json
import socket
import requests

from flask import Flask
from flask import request
from flask import jsonify

# Can we clean this up?
sys.path.append(os.path.join(os.path.dirname(__file__), "../Faraday_Proxy_Tools/")) #Append path to common tutorial FaradayIO module
from FaradayIO import faradaybasicproxyio
from FaradayIO import telemetryparser

# Start logging after importing modules
logging.config.fileConfig('loggingConfig.ini')
logger = logging.getLogger('aprs')

# Load Telemetry Configuration from telemetry.ini file
# Should have common file for apps...
aprsConfig = ConfigParser.RawConfigParser()
aprsConfig.read('aprs.ini')

# Read in APRS-IS Credentials
aprsISConfig = ConfigParser.RawConfigParser()
aprsISConfig.read('login.ini')

# Create and initialize dictionary queues
telemetryDicts = {}


def aprs_worker(config, sock):
    """
    Interface Faraday Telemetry application to forward to APRS-IS servers

    This worker thread is used to periodically query the telemetry server
    and obtain recent stations heard over RF and locally. It then forwards
    the information in appropriate APRS formatted strings to APRS-IS. It is
    currently not bidirectional
    """
    logger.info('Starting aprs_worker thread')
    while(5):
        stations = getStations()
        stationData = getStationData(stations)
        #print len(stationData)
        sendPositions(stationData, sock)
        time.sleep(2) # should slow down



def getStations():
    # Probably shouldn't hardcode
    url = "http://127.0.0.1:8001/stations"
    r = requests.get(url)
    results = r.json()
    return results

def getStationData(stations):
    url = "http://127.0.0.1:8001/"
    stationData = []
    for station in stations:
        #print station
        callsign = station["SOURCECALLSIGN"]
        nodeid = station["SOURCEID"]
        epoch = station["EPOCH"]


        #hardcoding station timespan in...
        payload = {"callsign": callsign, "nodeid": nodeid, "timespan": 60}
        try:
            r = requests.get(url, params = payload)
            #data = json.loads(r.text)
            data = r.json()
            #print len(data)
        except:
            pass
            print "none"

        stationData.append(data)

    # Return all station data from specified timespan
    return stationData[0]

def sendPositions(stations, socket):
    for station in stations:
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

        node = sourceCallsign + "-" + str(sourceID)
        destNode = destinationCallsign + "-" + str(destinationID)

        #Convert NMEA to Decimal Degrees
        #decLoc = decdec2decdeg(latitude,longitude)
        aprsLat = round(float(latitude),2)
        aprsLon = round(float(longitude),2)

        latString = str('{:.2f}'.format(aprsLat))
        lonString = str('{:.2f}'.format(aprsLon))

        aprsPosition = '=' + latString + latitudeDirection + '/' + lonString + longitudeDir

        rawaltitude = str(round(altitude, 0)).split('.')
        altitude = rawaltitude[0].zfill(6)
        rawspeed = str(round(speed, 0)).split('.')
        speed = rawspeed[0].zfill(3)

        positionString = node + '>GPSFDY,' + 'qAR,' + destNode + ':' + aprsPosition + '[' + '.../' + speed + '/A=' + altitude + 'FaradayRF Modem' + '\r'
        socket.sendall(positionString)
        #print positionString, socket

def aprsPosition(data):
    for station in data:
        station = station[0]

        if (station["gpsfix"] == 1) or (station["gpsfix"] == 2):
            # Extract stations
            node = station["callsign"] + "-" + str(station["id"])
            destNode = station["destcallsign"] + "-" + str(station["destid"])

            # Extract node GPS data suitable for APRS-IS use
            dmlat = "%.2f" % round(station["latdec"], 2)
            dmlon = "%.2f" % round(station["londec"], 2)
            latdeg = str(station["latdeg"])
            londeg = str(station["londeg"])
            latdir = station["latdir"]
            londir = station['londir']
            rawaltitude = str(round(station["altitude"], 0)).split('.')
            altitude = rawaltitude[0].zfill(6)
            rawspeed = str(round(station["speed"], 0)).split('.')
            speed = rawspeed[0].zfill(3)

            aprsposition = '=' + latdeg + dmlat + latdir + '/' + londeg + dmlon + londir

            if station["aprf"] == 1:
                positionString = node + '>GPSFDY,' + 'qAR,' + destNode + ':' + aprsposition + '[' + '.../' + speed + '/A=' + altitude + 'FaradayRF Modem' + '\r'
            else:
                positionString = node + '>GPSFDY,' + ':' + aprsposition + '[' + '.../' + speed + '/A=' + altitude + 'FaradayRF Modem' + '\r'
            print positionString
            aprs = connectAPRSIS()
            aprs.sendall(positionString)
            aprs.close()

def decdec2decdeg(latitude,longitude):
    # GPS NMEA decimal value is 7 characters long
    decLen = 7
    latLen = len(latitude)
    lonLen = len(longitude)

    # Split up decimal decmal NMEA
    lat1 = float(latitude[latLen - decLen:])
    lat0 = float(latitude[:latLen - decLen])
    lon0 = float(longitude[:lonLen - decLen])
    lon1 = float(longitude[lonLen - decLen:])

    latDec = lat0 + lat1/60
    lonDec = lon0 + lon1/60

    return {"latitude": latDec, "longitude": lonDec}

def decDeg2DMS(latitude,longitude):
    print "decDeg2DMS"
    print latitude
    print str(latitude).split(".")
    tempLat = str(latitude).split(".")
    latDegree = tempLat[0]
    temp = str(float("0." + tempLat[1]) * 60)
    tempLat = temp.split(".")
    latMinute = tempLat[0]
    latSecond = float("0." + tempLat[1]) * 60
    print latDegree, latMinute, latSecond
    #needs work...

# Initialize Flask microframework
app = Flask(__name__)

@app.route('/', methods=['GET'])
def aprs():
    """
    Provides a RESTful interface to aprs server at URL '/'

    Serves JSON responses to the "/" URL containing output of SQLite queries.
    Specific SQLite queries can return data from specified ranges and source
    stations as
    """

    try:
        # Obtain URL parameters
        callsign = request.args.get("callsign", "%")
        nodeid = request.args.get("nodeid", "%")
        direction = request.args.get("direction", 0)
        startTime = request.args.get("starttime", None)
        endTime = request.args.get("endtime", None)
        timespan = request.args.get("timespan", 5*60)

        nodeid = str(nodeid)
        direction = int(direction)
        callsign = str(callsign).upper()
        timespan = int(timespan)

    except ValueError as e:
        logger.error("ValueError: " + str(e))
        return json.dumps({"error": str(e)}), 400
    except IndexError as e:
        logger.error("IndexError: " + str(e))
        return json.dumps({"error": str(e)}), 400
    except KeyError as e:
        logger.error("KeyError: " + str(e))
        return json.dumps({"error": str(e)}), 400

    # Validate timespan
    if timespan <= 0:
        message = "Error: Timespan '{0}' is invalid".format(timespan)
        return json.dumps({"error": message}), 400

    # Create tuple of parameters for SQLite3
    parameters = {}
    parameters["CALLSIGN"] = callsign
    parameters["NODEID"] = nodeid
    parameters["DIRECTION"] = direction
    parameters["STARTTIME"] = startTime
    parameters["ENDTIME"] = endTimeF
    parameters["TIMESPAN"] = timespan

    data = []
    data = queryDb(parameters)

    # Check if data returned, if not, return HTTP 204
    if len(data) <= 0:
        logger.info("No station data in last %d seconds", timespan)
        return '', 204  # HTTP 204 response cannot have message data

    return json.dumps(data, indent=1), 200,\
            {'Content-Type': 'application/json'}

@app.route('/raw', methods=['GET'])
def rawTelemetry():
    """
    Provides a RESTful interface to the decoded raw telemetry at URL '/raw'

    The rawTelemetry() function is run when the URL "/raw" is queried. It
    provides non-SQLite database dequeu results. Each query can pop data off of
    a queu, thus ensuring there are no duplicates and acting like a proxy with
    decoded data instead of BASE64 encoded data.
    """

    try:
        # Obtain URL parameters
        callsign = request.args.get("callsign", None)
        nodeId = request.args.get("nodeid", None)
        limit = request.args.get("limit", None)

    except ValueError as e:
        logger.error("ValueError: " + str(e))
        return json.dumps({"error": str(e)}), 400
    except IndexError as e:
        logger.error("IndexError: " + str(e))
        return json.dumps({"error": str(e)}), 400
    except KeyError as e:
        logger.error("KeyError: " + str(e))
        return json.dumps({"error": str(e)}), 400

    # Check to see that required parameters are present
    # Use try statement to fail cleanly with relevant error information
    try:
        # If callsign is present then nodeid is required
        if callsign is not None:
            if nodeId is None:

                raise StandardError("Missing 'nodeid' parameter")
            else:
                # Convert nodeId to int and callsign to uppercase string
                nodeId = int(nodeId)
                callsign = str(callsign).upper()

                # Check to see if the Node ID is in the valid range
                if nodeId > 255 or nodeId < 0:
                    raise ValueError(
                        "Faraday Node ID's valid integer between 0-255")
        else:
            # Don't change anything since callsign is None
           pass

        if limit is None:
            # Optional, set limit to largest value of any radio queue size
            temp = []
            for key, value in telemetryDicts.iteritems():
                temp.append(len(value))
            limit = int(max(temp))
        else:
            # Limit provided, convert to int and check if it's valid
            limit = int(limit)
            if limit <= 0:
                message = "Error: Limit '{0}' is invalid".format(limit)
                return json.dumps({"error": message}), 400

    except ValueError as e:
        logger.error("ValueError: " + str(e))
        return json.dumps({"error": str(e)}), 400
    except IndexError as e:
        logger.error("IndexError: " + str(e))
        return json.dumps({"error": str(e)}), 400
    except KeyError as e:
        logger.error("KeyError: " + str(e))
        return json.dumps({"error": str(e)}), 400
    except StandardError as e:
        logger.error("StandardError: " + str(e))
        return json.dumps({"error": str(e)}), 400

    # Ready to get data from the queue. We have to cases: callsign and nodeid
    # are present or they are not. The resulting dictionary created needs to
    # be different in both cases. Use try statement to fail cleanly
    try:
        # Clear all data from any previous requests
        data = []

        # If callsign and nodeId are not present, return all connected radio
        # queue data.
        if callsign == None and nodeId == None:
            # Iterate through each faraday radio connected via USB
            for key, value in telemetryDicts.iteritems():
                # Make sure queue actually has data in it
                if (len(value) > 0):
                    stationData = []
                    station = {}
                    while value:
                        # While data is still in the queue pop off items
                        # Pops off right to maintain newest item in object 0
                        packet = []
                        packet = value.pop()
                        if len(stationData) >= limit:
                            # Hit the limit, break out of the while loop early
                            break
                        # Append packet to stationData list
                        stationData.append(packet)
                    # All necessary data from radio obtained, add to dictionary
                    station[key] = stationData
            # The data list is a list of dictionaries for json.dumps()
            data.append(station)
        else:
            # Local radio has been specified, only return data from it
            stationData = []
            station = {}
            if (len(telemetryDicts[str(callsign) + str(nodeId)]) > 0):
                # Make sure specific radio queue actually has data in it.
                # If so, pop off the items and build up a dictionary for it.
                while telemetryDicts[str(callsign) + str(nodeId)]:
                    # Pop off items from right so JSON has newest items first
                    packet = \
                        telemetryDicts[
                            str(callsign) + str(nodeId)].pop()
                    stationData.append(packet)
                    station[str(callsign) + str(nodeId)] = stationData
                    if len(stationData) >= limit:
                        # Hit the limit, break from loop
                        break
                # Append specified radio data to the json.dumps() list
                data.append(station)

    except ValueError as e:
        logger.error("ValueError: " + str(e))
        return json.dumps({"error": str(e)}), 400
    except IndexError as e:
        logger.error("IndexError: " + str(e))
        return json.dumps({"error": str(e)}), 400
    except KeyError as e:
        logger.error("KeyError: " + str(e))
        return json.dumps({"error": str(e)}), 400
    except StandardError as e:
        logger.error("StandardError: " + str(e))
        return json.dumps({"error": str(e)}), 400

    # Completed our query for "/raw", return json.dumos() and HTTP 200
    return json.dumps(data, indent=1), 200,\
            {'Content-Type': 'application/json'}

@app.route('/stations', methods=['GET'])
def stations():
    """
    Provides a RESTful interface to station queries at URL '/stations'

    This function, stations(), runs whenever "/stations" URL is queried. The
    intent of this function is to return a JSON dictionary of stations and
    the time they were heard. If no timespan or range is specified then it
    defaults to the last 5 minutes. If a specific station is specified, then
    the last time it was heard is returned.
    """

    try:
        # Obtain URL parameters
        timespan = request.args.get("timespan", 5*60)
        startTime = request.args.get("starttime", None)
        endTime = request.args.get("endtime", None)
        callsign = request.args.get("callsign", None)
        nodeId = request.args.get("nodeid", "%")

        # Timespan will allways be an integer
        timespan = int(timespan)

    except ValueError as e:
        logger.error("ValueError: " + str(e))
        return json.dumps({"error": str(e)}), 400
    except IndexError as e:
        logger.error("IndexError: " + str(e))
        return json.dumps({"error": str(e)}), 400
    except KeyError as e:
        logger.error("KeyError: " + str(e))
        return json.dumps({"error": str(e)}), 400
    except StandardError as e:
        logger.error("StandardError: " + str(e))
        return json.dumps({"error": str(e)}), 400

    # Clear parameters dictionary and add URL parameters to it
    parameters = {}
    parameters["TIMESPAN"] = timespan
    parameters["STARTTIME"] = startTime
    parameters["ENDTIME"] = endTime
    parameters["CALLSIGN"] = callsign
    parameters["NODEID"] = nodeId

    # Provide parameters to queryStationsDb to return the result SQLite rows
    data = queryStationsDb(parameters)

    # Check if no stations returned, if not, return HTTP 204
    if len(data) <= 0:
        logger.info("Station(s) not heard in last %d seconds", timespan)
        return '', 204  # HTTP 204 response cannot have message data

    # Completed the /stations request, return data json.dumps() and HTTP 200
    print len(data)
    return json.dumps(data, indent=1), 200,\
            {'Content-Type': 'application/json'}

@app.errorhandler(404)
def pageNotFound(error):
    """HTTP 404 response for incorrect URL"""

    # Completed handling of unknown URL, return json error message and HTTP 404
    logger.error("Error: " + str(error))
    return json.dumps({"error": "HTTP " + str(error)}), 404

# # Database Functions
# def initDB():
#     """Initialize database, if not present then create it"""
#     # Obtain configuration filenames
#     dbFilename = telemetryConfig.get("database", "filename")
#     dbSchema = telemetryConfig.get("database", "schemaname")
#
#     # Check if database exists
#     if os.path.isfile(dbFilename):
#         pass
#     else:
#         # Open database schema SQL file and execute the SQL functions inside
#         # after connecting. Close the database when complete.
#         with open(dbSchema, 'rt') as f:
#             schema = f.read()
#
#         conn = sqlite3.connect(dbFilename)
#         cur = conn.cursor()
#         cur.executescript(schema)
#
#         conn.close()

# def sqlInsert(data):
#     """Takes in a data tuple and inserts int into the telemetry SQLite table"""
#
#     # Read in name of telemetry databse
#     db = telemetryConfig.get("database", "filename")
#
#     # Create parameter substitute "?" string for SQL query then create SQL
#     data = (None,) + data  # Add a null to tuple for KEYID
#     numKeys = len(data)
#     paramSubs = "?" * (numKeys)
#     paramSubs = ",".join(paramSubs)
#     sql = "INSERT INTO TELEMETRY VALUES(" + paramSubs + ")"
#
#     # Connect to database, create SQL query, execute query, and close database
#     try:
#         conn = sqlite3.connect(db)
#         cursor = conn.cursor()
#
#         # Use connection as context manager to rollback automatically if error
#         with conn:
#             conn.execute(sql,data)
#
#     except StandardError as e:
#         logger.error("StandardError: " + str(e))
#     except ValueError as e:
#         logger.error("ValueError: " + str(e))
#     except IndexError as e:
#         logger.error("IndexError: " + str(e))
#     except KeyError as e:
#         logger.error("KeyError: " + str(e))
#
#     # Completed, close database
#     conn.close()
#
# def queryDb(parameters):
#     """
#     Takes in parameters to query the SQLite database, returns the results
#
#     Performs a SQL query to retrieve data from specific times, stations, or
#     ranges of time. Returns all results as a list of JSON dictionaries
#     """
#     # Use supplied parameters to generate a Tuple of epoch start/stop times
#     # SQLite3 parameters need to be Tuples
#     timeTuple = generateStartStopTimes(parameters)
#     callsign = parameters["CALLSIGN"].upper()
#     nodeid = parameters["NODEID"]
#     paramTuple = (callsign, nodeid) + timeTuple
#
#     # Detect the direction, this will change the query from searching for
#     # the source or destination radio. Must generate two slightly different
#     # SQL queries for each case
#     if parameters["DIRECTION"] == 0:
#         # Direction 0 = Source radio
#         sqlWhereCall = "WHERE SOURCECALLSIGN LIKE ? "
#         sqlWhereID = "AND SOURCEID LIKE ? "
#     else:
#         # Direction 1 = Destination radio
#         sqlWhereCall = "WHERE DESTINATIONCALLSIGN LIKE ? "
#         sqlWhereID = "AND DESTINATIONID LIKE ? "
#
#     sqlBeg = "SELECT * FROM TELEMETRY "
#     sqlEpoch ="AND EPOCH BETWEEN ? AND ? "
#     sqlEnd = "ORDER BY KEYID DESC"
#
#     # Create  SQL Query string
#     sql = sqlBeg + sqlWhereCall + sqlWhereID + sqlEpoch + sqlEnd
#
#     # Open configuration file
#     dbFilename = telemetryConfig.get("database", "filename")
#
#     # Connect to database, create SQL query, execute query, and close database
#     try:
#         conn = sqlite3.connect(dbFilename)
#         conn.row_factory = sqlite3.Row  # Row_factory returns column/values
#         cur = conn.cursor()
#         cur.execute(sql,paramTuple)
#         rows = cur.fetchall()
#
#     except StandardError as e:
#         logger.error("StandardError: " + str(e))
#     except ValueError as e:
#         logger.error("ValueError: " + str(e))
#     except IndexError as e:
#         logger.error("IndexError: " + str(e))
#     except KeyError as e:
#         logger.error("KeyError: " + str(e))
#
#
#     # Iterate through resulting data and create a list of dictionaries for JSON
#     try:
#         sqlData = []
#         for row in rows:
#             rowData = {}
#             for parameter in row.keys():
#                 rowData[parameter] = row[parameter]
#             sqlData.append(rowData)
#
#     except StandardError as e:
#         logger.error("StandardError: " + str(e))
#     except ValueError as e:
#         logger.error("ValueError: " + str(e))
#     except IndexError as e:
#         logger.error("IndexError: " + str(e))
#     except KeyError as e:
#         logger.error("KeyError: " + str(e))
#
#     # Completed query, close database, return sqlData list of dictionaries
#     conn.close()
#     return sqlData
#
# def queryStationsDb(parameters):
#     """
#     Takes in parameters to query the SQLite database, returns the results
#
#     Performs a SQL query to retrieve data about stations in the SQLite db.
#     Can retrieve all stations ever heard, in a specific time range, or in
#     a timespan before now. Returns all results as a list of JSON dictionaries
#     """
#
#     # Check for whether a time range or timespan is being specified
#     if parameters["STARTTIME"] != None and parameters["ENDTIME"] != None:
#         # Start end end times provided, ignore timespan
#         startTime = str(parameters["STARTTIME"])
#         endTime = str(parameters["ENDTIME"])
#         timeTuple = iso8601ToEpoch(startTime,endTime)
#     else:
#         # We should use the timespan provided to generate start and stop times
#         endEpoch = time.time()
#         startEpoch = endEpoch - int(parameters["TIMESPAN"])
#         timeTuple = (startEpoch, endEpoch)
#
#     # Specify and create SQL command string
#     sqlBeg = "SELECT SOURCECALLSIGN, SOURCEID, EPOCH FROM TELEMETRY "
#     sqlWhere = "WHERE EPOCH BETWEEN ? AND ? "
#     sqlEnd = "GROUP BY SOURCECALLSIGN, SOURCEID ORDER BY EPOCH DESC"
#
#     # detect if callsign/nodeid provided, return the last time it was heard
#     if parameters["CALLSIGN"] != None:
#         # Since a callsign was specified, simply search the entire db for it
#         # and return the last epoch time it was heard.
#         timeTuple = (0, time.time())
#
#         # Update the sqlWhere and sqlEnd strings for this query
#         sqlWhere = sqlWhere + "AND SOURCECALLSIGN LIKE ? AND SOURCEID LIKE ? "
#         sqlEnd = sqlEnd + " LIMIT 1"
#
#         # Create paramTuple for SQLite3 execute function
#         paramTuple = timeTuple + (str(parameters["CALLSIGN"]), parameters["NODEID"])
#     else:
#         # No callsign was provided, keep SQL query as defined
#         # Create paramTuple from only timeTuple
#         paramTuple = timeTuple
#
#     # Create SQL query string
#     sql = sqlBeg + sqlWhere + sqlEnd
#
#     # Get telemetry databse name from configuration file
#     dbFilename = telemetryConfig.get("database", "filename")
#
#     # Connect to database, create SQL query, execute query, and close database
#     try:
#         conn = sqlite3.connect(dbFilename)
#         conn.row_factory = sqlite3.Row  # SQLite.Row returns columns,values
#         cur = conn.cursor()
#         cur.execute(sql,paramTuple)
#         rows = cur.fetchall()
#
#     except StandardError as e:
#         logger.error("StandardError: " + str(e))
#     except ValueError as e:
#         logger.error("ValueError: " + str(e))
#     except IndexError as e:
#         logger.error("IndexError: " + str(e))
#     except KeyError as e:
#         logger.error("KeyError: " + str(e))
#
#     # Parse through rows and create key:value dictionaries for each row.
#     # Then build up a list of dictionaries for all results.
#     try:
#         sqlData = []
#         for row in rows:
#             rowData = {}
#             for parameter in row.keys():
#                 rowData[parameter] = row[parameter]
#             sqlData.append(rowData)
#
#     except StandardError as e:
#         logger.error("StandardError: " + str(e))
#     except ValueError as e:
#         logger.error("ValueError: " + str(e))
#     except IndexError as e:
#         logger.error("IndexError: " + str(e))
#     except KeyError as e:
#         logger.error("KeyError: " + str(e))
#
#     # Completed query, close database, return list of dictionary data for JSON
#     conn.close()
#     return sqlData
#
# def generateStartStopTimes(parameters):
#     """Use parameters dictionary to build up a Tuple of start/stop time values"""
#
#     # Check if start and stop times were provided in ISO 8610 format,
#     # if not then generate epoch from timespan
#     if parameters["STARTTIME"] != None and parameters["ENDTIME"] != None:
#         # Start end end times provided, ignore timespan
#         startTime = str(parameters["STARTTIME"])
#         endTime = str(parameters["ENDTIME"])
#         timeTuple = iso8601ToEpoch(startTime,endTime)
#
#     else:
#         # We should use the timespan provided to generate start and stop times
#         endEpoch = time.time()
#         startEpoch = endEpoch - float(parameters["TIMESPAN"])
#         timeTuple = (int(startEpoch), int(endEpoch))
#
#     return timeTuple
#
#
#
# def iso8601ToEpoch(startTime, endTime):
#     # Date format is ISO 8601
#     fmt = "%Y-%m-%dT%H:%M:%S"
#
#     # Generate start and stop time tuples
#     start = time.strptime(startTime,fmt)
#     end = time.strptime(endTime,fmt)
#
#     # Convert time tuples to epoch times
#     startEpoch = time.mktime(start)
#     endEpoch = time.mktime(end)
#
#     # Create a tuple of the start and stop time, return it
#     timeTuple = (startEpoch, endEpoch)
#     return timeTuple

def getCredentials():
    pass
    # Read in APRS-IS Credentials
    aprsISConfig = ConfigParser.RawConfigParser()
    aprsISConfig.read('login.ini')

    callsign = aprsISConfig.get('credentials', 'callsign')
    passcode = aprsISConfig.getint('credentials', 'passcode')

    return [callsign,passcode]

def connectAPRSIS():
    pass
    callsign = aprsISConfig.get('credentials', 'callsign')
    passcode = aprsISConfig.getint('credentials', 'passcode')
    server = aprsConfig.get("aprsis", "server")
    port = aprsConfig.getint("aprsis", "port")
    print callsign, passcode, server, port

    aprssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            aprssock.connect((server, port))
            logon_string = 'user' + ' ' + callsign + ' ' + 'pass' + ' ' + str(
                passcode) + ' vers "FaradayRF APRS-IS application" \r'
            print logon_string
            aprssock.sendall(logon_string)

        except socket.error as e:
            print e

        else:
            print "Connected to %s on port %d!" % (server, port)
            print aprssock.getsockname()
            return aprssock
            break
        time.sleep(10)  # Try to reconnect every 10 seconds
    return aprssock


def main():
    """Main function which starts telemery worker thread + Flask server."""
    logger.info('Starting APRS-IS server')
    #credentials = getCredentials()
    #print credentials
    sock = connectAPRSIS()



    # Initialize local variables
    threads = []

    # Open or create database if it doesn't exist
    #initDB()

    t = threading.Thread(target=aprs_worker, args=(aprsConfig, sock))
    threads.append(t)
    t.start()

    # Start the flask server on localhost:8001
    aprsHost = aprsConfig.get("flask", "host")
    aprsPort = aprsConfig.getint("flask", "port")

    app.run(host=aprsHost, port=aprsPort, threaded=True)

if __name__ == '__main__':
    main()
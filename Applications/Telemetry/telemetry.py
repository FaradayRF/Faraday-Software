#-------------------------------------------------------------------------------
# Name:        /telemetry/telemetry.py
# Purpose:      Query proxy for telemetry data and parse it to a local database
#               as well as provide a RESTful interface to decoded data.
#
# Author:      Bryce Salmi
#
# Created:     11/10/2016
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
import sqlite3
import json

from flask import Flask
from flask import request

# Can we clean this up?
sys.path.append(os.path.join(os.path.dirname(__file__), "../../Faraday_Proxy_Tools/")) #Append path to common tutorial FaradayIO module
from FaradayIO import faradaybasicproxyio
from FaradayIO import telemetryparser

# Start logging after importing modules
logging.config.fileConfig('loggingConfig.ini')
logger = logging.getLogger('telemetry')

# Load Telemetry Configuration from telemetry.ini file
# Should have common file for apps...
telemetryConfig = ConfigParser.RawConfigParser()
telemetryConfig.read('telemetry.ini')

# Create and initialize dictionary queues
telemetryDicts = {}


def telemetry_worker(config):
    """
    Interface Faraday Proxy to obtain telemtry

    This function interfaces the Proxy application via its RESTful interface.
    It is a one-way operation as it makes no sense to POST data to proxy for
    telemetry to a specific unit with this application.
    """
    logger.info('Starting telemetry_worker thread')

    # initialize variables
    stations = {}

    # Initialize proxy object
    proxy = faradaybasicproxyio.proxyio()

    # Initialize Faraday parser
    faradayParser = telemetryparser.TelemetryParse()  # Add logger?

    # Open configuration file
    dbFilename = config.get("DATABASE", "FILENAME")

    # Pragmatically create descriptors for each Faraday connected to Proxy
    count = config.getint("TELEMETRY", "UNITS")

    for num in range(count):
        callsign = config.get("TELEMETRY", "UNIT" + str(num) + "CALL").upper()
        nodeid = config.get("TELEMETRY", "UNIT" + str(num) + "ID")
        stations["UNIT" + str(num) + "CALL"] = callsign
        stations["UNIT" + str(num) + "ID"] = nodeid
        telemetryDicts[str(callsign) + str(nodeid)] = deque([], maxlen=1000)

    # check for data on telemetry port, if True place into deque
    while(1):
         for radio in range(count):
            callsign = stations["UNIT" + str(num) + "CALL"]
            nodeid = stations["UNIT" + str(num) + "ID"]
            data = proxy.GET(str(callsign), str(nodeid), int(proxy.TELEMETRY_PORT))

            # Iterate through each packet and unpack into dictionary
            if data != None:
                for item in data:
                    try:
                        # Decode BASE64 JSON data packet into
                        unPackedItem = proxy.DecodeRawPacket(item["data"])
                        # Unpack packet into datagram elements
                        datagram = faradayParser.UnpackDatagram(unPackedItem,False)
                        # Extract the payload length from payload since padding could be used
                        telemetryData = faradayParser.ExtractPaddedPacket(datagram["PayloadData"],faradayParser.packet_3_len)
                        # Unpack payload and return a dictionary of telemetry, return tuple and dictionary
                        parsedTelemetry = faradayParser.UnpackPacket_3(telemetryData, False)

                    except ValueError as e:
                        logger.error("ValueError: " + str(e))
                    except IndexError as e:
                        logger.error("IndexError: " + str(e))
                    except KeyError as e:
                        logger.error("KeyError: " + str(e))

                    else:
                        sqlInsert(parsedTelemetry)
                        telemetryDicts[str(callsign) + str(nodeid)].append(parsedTelemetry)

         time.sleep(1) # should slow down

# Initialize Flask microframework
app = Flask(__name__)

@app.route('/', methods=['GET'])
def dbTelemetry():
    """
    Provides a RESTful interface to telemetry in the SQLite database at URL '/'

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
        limit = request.args.get("limit")

        nodeid = str(nodeid)
        direction = int(direction)
        callsign = str(callsign).upper()
        timespan = int(timespan)
        if limit != None:
            limit = int(limit)

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
    parameters["ENDTIME"] = endTime
    parameters["TIMESPAN"] = timespan
    parameters["LIMIT"] = limit

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

    :return: JSON formatted string with data or error. HTTP204 if no data
    """
    #  Initialize local variables
    stationData = []

    try:
        # Obtain URL parameters
        callsign = request.args.get("callsign", None)
        nodeId = request.args.get("nodeid", None)
        limit = request.args.get("limit", None)

    except IOError as e:
        logger.error("IOError: " + str(e))
        return json.dumps({"error": str(e)}), 400

    # Check to see that required parameters are present
    # Use try statement to fail cleanly with relevant error information
    try:
        # If callsign is present then nodeid is required
        if callsign is not None:
            if nodeId is None:
                raise ValueError("Missing 'nodeid' parameter")

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
            #  Optional, set limit to largest value of any radio queue size
            temp = []
            #  telemetryDicts is telemetryWorker queue
            for key, value in telemetryDicts.iteritems():
                temp.append(len(value))
            limit = int(max(temp))

        else:
            # Limit provided, convert to int and check if it's valid
            limit = int(limit)
            if limit <= 0:
                message = "Error: Limit '{0}' is invalid".format(limit)
                raise ValueError(message)

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

    # Ready to get data from the queue. We have two cases: callsign and nodeid
    # are present or they are not. The resulting dictionary created needs to
    # be different in both cases. Use try statement to fail cleanly
    try:
        # Clear all data from any previous requests
        data = []

        # If callsign and nodeId are not present, return all connected radio
        # queue data.
        if callsign == None and nodeId == None:
            # Iterate through each faraday radio connected via USB
            #  telemetryDicts is telemetryWorker queue
            for key, value in telemetryDicts.iteritems():
                # Make sure queue actually has data in it
                if (len(value) > 0):
                    station = {}
                    while value:
                        # While data is still in the queue pop off items
                        # Pops off right to maintain newest item in object 0
                        packet = []
                        packet = value.pop()
                        if len(stationData) >= limit:
                            # Hit the limit, break out of the while loop early
                            break
                            #  Unsure if break will cause multiple locally connected
                            #  units to not have data

                        # Append packet to stationData list
                        stationData.append(packet)

                    # All necessary data from radio obtained, add to dictionary
                    station[key] = stationData
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

    if len(stationData) == 0:
        #  No new data is in queue
        logger.info("No station data is in queue")
        return '', 204  # HTTP 204 response cannot have message data

    # Completed our query for "/raw", return json.dumps() and HTTP 200
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

    :return: JSON formatted string with data or error. HTTP204 if no data
    """

    try:
        # Obtain URL parameters
        timespan = request.args.get("timespan", 5*60)
        startTime = request.args.get("starttime", None)
        endTime = request.args.get("endtime", None)
        callsign = request.args.get("callsign", "%").upper()
        nodeId = request.args.get("nodeid", "%")

        # Timespan will always be an integer
        timespan = int(timespan)

    except IOError as e:
        logger.error("IOError: " + str(e))
        return json.dumps({"error": str(e)}), 400
    except ValueError as e:
        logger.error("ValueError: " + str(e))
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
        logger.info("No Station have been heard in last %d seconds", timespan)
        return '', 204  # HTTP 204 response cannot have message data

    # Completed the /stations request, return data json.dumps() and HTTP 200
    return json.dumps(data, indent=1), 200,\
            {'Content-Type': 'application/json'}

@app.errorhandler(404)
def pageNotFound(error):
    """
    HTTP 404 response for incorrect URL

    :param error: HTTP Error
    :return: JSON formatted string with error description
    """

    # Completed handling of unknown URL, return json error message and HTTP 404
    logger.error("Error: " + str(error))
    return json.dumps({"error": "HTTP " + str(error)}), 404

# Database Functions
def initDB():
    """Initialize database, if not present then create it"""
    # Obtain configuration filenames
    dbFilename = telemetryConfig.get("DATABASE", "FILENAME")
    dbSchema = telemetryConfig.get("DATABASE", "SCHEMANAME")

    # Check if database exists
    if os.path.isfile(dbFilename):
        pass
    else:
        # Open database schema SQL file and execute the SQL functions inside
        # after connecting. Close the database when complete.
        with open(dbSchema, 'rt') as f:
            conn = sqlite3.connect(dbFilename)
            cur = conn.cursor()
            schema = f.read()
            cur.executescript(schema)
        conn.close()

def createTelemetryList(data):
    """Converts data dictionary into a defined list for insertion into SQLite db"""

    # Create list of dictionary data in appropriate order
    # First statement in None for KeyID
    temp = [None,
            data["SOURCECALLSIGN"],
            data["SOURCEID"],
            data["DESTINATIONCALLSIGN"],
            data["DESTINATIONID"],
            data["RTCSEC"],
            data["RTCMIN"],
            data["RTCHOUR"],
            data["RTCDAY"],
            data["RTCDOW"],
            data["RTCMONTH"],
            data["RTCYEAR"],
            data["GPSLATITUDE"],
            data["GPSLATITUDEDIR"],
            data["GPSLONGITUDE"],
            data["GPSLONGITUDEDIR"],
            data["GPSALTITUDE"],
            data["GPSALTITUDEUNITS"],
            data["GPSSPEED"],
            data["GPSFIX"],
            data["GPSHDOP"],
            data["GPIOSTATE"],
            data["RFSTATE"],
            data["ADC0"],
            data["ADC1"],
            data["ADC2"],
            data["ADC3"],
            data["ADC4"],
            data["ADC5"],
            data["VCC"],
            data["BOARDTEMP"],
            data["ADC8"],
            data["HABTIMERSTATE"],
            data["HABCUTDOWNSTATE"],
            data["HABTRIGGERTIME"],
            data["HABTIMER"],
            data["EPOCH"]
            ]

    return temp


def sqlInsert(data):
    """Takes in a data tuple and inserts int into the telemetry SQLite table"""

    # Read in name of telemetry databse
    db = telemetryConfig.get("DATABASE", "FILENAME")

    telem = createTelemetryList(data)

    # Create parameter substitute "?" string for SQL query then create SQL
    numKeys = len(telem)
    paramSubs = "?" * (numKeys)
    paramSubs = ",".join(paramSubs)
    sql = "INSERT INTO TELEMETRY VALUES(" + paramSubs + ")"

    # Connect to database, create SQL query, execute query, and close database
    try:
        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        # Use connection as context manager to rollback automatically if error
        with conn:
            conn.execute(sql,telem)

    except conn.ProgrammingError as e:
        logger.error(e)
        logger.error(telem)
        conn.rollback()
    except ValueError as e:
        logger.error("ValueError: " + str(e))
    except IndexError as e:
        logger.error("IndexError: " + str(e))
    except KeyError as e:
        logger.error("KeyError: " + str(e))
    except sqlite3.OperationalError as e:
        # TODO: cleanup
        logger.error(e)
        initDB()

    # Completed, close database
    conn.close()

def queryDb(parameters):
    """
    Takes in parameters to query the SQLite database, returns the results

    Performs a SQL query to retrieve data from specific times, stations, or
    ranges of time. Returns all results as a list of JSON dictionaries.
    Parameters:
    "CALLSIGN":Uppercase callsign
    "NODEID": Node ID
    "LIMIT": Number of SQL rows to return
    "DIRECTION": Specify if callsign-nodeid to search is local (0) or remote (1)
    "STARTTIME": ISO8601 time to start search
    "ENDTIME": ISO8601 time to end search
    "TIMESPAN": Number of seconds to search over, ending at current time

    :param parameters: Search parameter dictionary
    :return: List of SQL output where each item is a dictionary
    """

    #Declare local variables
    sqlData = []

    # Use supplied parameters to generate a Tuple of epoch start/stop times
    # SQLite3 parameters need to be Tuples
    timeTuple = generateStartStopTimes(parameters)
    callsign = parameters["CALLSIGN"]
    nodeid = parameters["NODEID"]
    limit = parameters["LIMIT"]

    # Detect the direction, this will change the query from searching for
    # the source or destination radio. Must generate two slightly different
    # SQL queries for each case
    if parameters["DIRECTION"] == 0:
        # Direction 0 = Source radio
        sqlWhereCall = "WHERE SOURCECALLSIGN LIKE ? "
        sqlWhereID = "AND SOURCEID LIKE ? "
    else:
        # Direction 1 = Destination radio
        sqlWhereCall = "WHERE DESTINATIONCALLSIGN LIKE ? "
        sqlWhereID = "AND DESTINATIONID LIKE ? "

    sqlBeg = "SELECT * FROM TELEMETRY "
    sqlEpoch ="AND EPOCH BETWEEN ? AND ? "
    sqlEnd = "ORDER BY KEYID DESC"
    if limit != None:
        sqlEnd = sqlEnd + " LIMIT ?"
        paramTuple = (callsign, nodeid) + timeTuple + (limit,)
    else:
        paramTuple = (callsign, nodeid) + timeTuple

    # Create  SQL Query string
    sql = sqlBeg + sqlWhereCall + sqlWhereID + sqlEpoch + sqlEnd
    logger.debug(sql)

    # Open configuration file
    try:
        dbFilename = telemetryConfig.get("DATABASE", "FILENAME")

    except ConfigParser.Error as e:
        logger.error(e)
        return sqlData

    # Connect to database, create SQL query, execute query, and close database
    try:
        conn = sqlite3.connect(dbFilename)

    except sqlite3.Error as e:
        logger.error("Sqlite3.Error: " + str(e))
        logger.error(paramTuple)
        return sqlData

    conn.row_factory = sqlite3.Row  # Row_factory returns column/values
    cur = conn.cursor()

    try:
        cur.execute(sql,paramTuple)

    except sqlite3.Error as e:
        logger.error("Sqlite3.Error: " + str(e))
        logger.error(paramTuple)
        conn.close()
        return sqlData

    # Iterate through resulting data and create a list of dictionaries for JSON
    try:
        rows = cur.fetchall()
        for row in rows:
            rowData = {}
            for parameter in row.keys():
                rowData[parameter] = row[parameter]
            sqlData.append(rowData)

    except StandardError as e:
        logger.error("StandardError: " + str(e))
        conn.close()
        return sqlData

    # Completed query, close database, return sqlData list of dictionaries
    conn.close()
    return sqlData

def queryStationsDb(parameters):
    """
    Takes in parameters to query the SQLite database, returns the results

    Performs a SQL query to retrieve data about stations in the SQLite db.
    Can retrieve all stations ever heard, a base callsign, in a specific
    time range, or in a timespan. Returns all results as a list of JSON
    dictionaries

    Parameters:
    "CALLSIGN":Uppercase callsign
    "NODEID": Node ID
    "DIRECTION": Specify if callsign-nodeid to search is local (0) or remote (1)
    "STARTTIME": ISO8601 time to start search
    "ENDTIME": ISO8601 time to end search
    "TIMESPAN": Number of seconds to search over, ending at current time

    :param parameters: Search parameter dictionary
    :return: List of SQL output where each item is a dictionary
    """

    #  Initialize local variables
    sqlData = []

    # Check for whether a time range or timespan is being specified
    if parameters["STARTTIME"] != None and parameters["ENDTIME"] != None:
        # Start end end times provided, ignore timespan
        startTime = str(parameters["STARTTIME"])
        endTime = str(parameters["ENDTIME"])
        timeTuple = iso8601ToEpoch(startTime,endTime)
    else:
        # We should use the timespan provided to generate start and stop times
        endEpoch = time.time()
        startEpoch = endEpoch - int(parameters["TIMESPAN"])
        timeTuple = (startEpoch, endEpoch)

    # Specify and create SQL command string
    sqlBeg = "SELECT SOURCECALLSIGN, SOURCEID, EPOCH FROM TELEMETRY "
    sqlWhere = "WHERE EPOCH BETWEEN ? AND ? "
    sqlEnd = "GROUP BY SOURCECALLSIGN, SOURCEID ORDER BY EPOCH DESC"

    # detect if callsign/nodeid provided, return the last time it was heard
    if parameters["CALLSIGN"] != "%":
        # Since a callsign was specified, simply search the entire db for it
        # and return the last epoch time it was heard.
        timeTuple = (0, time.time())

        # Update the sqlWhere strings for this query
        sqlWhere = sqlWhere + "AND SOURCECALLSIGN LIKE ?"

        # Create paramTuple for SQLite3 execute function
        paramTuple = timeTuple + (parameters["CALLSIGN"],)
    else:
        # Create paramTuple for SQLite3 execute function do not include callsign
        paramTuple = timeTuple

    # Create SQL query string
    sql = sqlBeg + sqlWhere + sqlEnd

    # Get telemetry database name from configuration file
    try:
        dbFilename = telemetryConfig.get("DATABASE", "FILENAME")

    except ConfigParser.Error as e:
        logger.error(e)
        return sqlData

    # Connect to database, create SQL query, execute query, and close database
    try:
        conn = sqlite3.connect(dbFilename)

    except sqlite3.Error as e:
        logger.error("Sqlite3.error: " + str(e))
        logger.error(paramTuple)
        return sqlData

    conn.row_factory = sqlite3.Row  # SQLite.Row returns columns,values
    cur = conn.cursor()

    try:
        cur.execute(sql,paramTuple)

    except sqlite3.Error as e:
        logger.error("Sqlite3.error: " + str(e))
        logger.error(paramTuple)
        conn.close()
        return sqlData

    # Parse through rows and create key:value dictionaries for each row.
    # Then build up a list of dictionaries for all results.
    try:
        rows = cur.fetchall()
        for row in rows:
            rowData = {}
            for parameter in row.keys():
                rowData[parameter] = row[parameter]
            sqlData.append(rowData)

    except StandardError as e:
        logger.error("StandardError: " + str(e))
        conn.close()
        return sqlData

    # Completed query, close database, return list of dictionary data for JSON
    conn.close()
    return sqlData

def generateStartStopTimes(parameters):
    """Use parameters dictionary to build up a Tuple of start/stop time values"""

    # Check if start and stop times were provided in ISO 8610 format,
    # if not then generate epoch from timespan
    if parameters["STARTTIME"] != None and parameters["ENDTIME"] != None:
        # Start end end times provided, ignore timespan
        startTime = str(parameters["STARTTIME"])
        endTime = str(parameters["ENDTIME"])
        timeTuple = iso8601ToEpoch(startTime,endTime)

    else:
        # We should use the timespan provided to generate start and stop times
        endEpoch = time.time()
        startEpoch = endEpoch - float(parameters["TIMESPAN"])
        timeTuple = (int(startEpoch), int(endEpoch))

    return timeTuple



def iso8601ToEpoch(startTime, endTime):
    # Date format is ISO 8601
    fmt = "%Y-%m-%dT%H:%M:%S"

    # Generate start and stop time tuples
    start = time.strptime(startTime,fmt)
    end = time.strptime(endTime,fmt)

    # Convert time tuples to epoch times
    startEpoch = time.mktime(start)
    endEpoch = time.mktime(end)

    # Create a tuple of the start and stop time, return it
    timeTuple = (startEpoch, endEpoch)
    return timeTuple


def main():
    """Main function which starts telemery worker thread + Flask server."""
    logger.info('Starting telemetry server')

    # Initialize local variables
    threads = []

    # Open or create database if it doesn't exist
    initDB()

    t = threading.Thread(target=telemetry_worker, args=(telemetryConfig,))
    threads.append(t)
    t.start()

    # Start the flask server on localhost:8001
    telemetryHost = telemetryConfig.get("FLASK", "HOST")
    telemetryPort = telemetryConfig.getint("FLASK", "PORT")

    app.run(host=telemetryHost, port=telemetryPort, threaded=True)

if __name__ == '__main__':
    main()

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
sys.path.append(os.path.join(os.path.dirname(__file__), "../Faraday_Proxy_Tools/")) #Append path to common tutorial FaradayIO module
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
    dbFilename = config.get("database", "filename")

    # Pragmatically create descriptors for each Faraday connected to Proxy
    count = config.getint("telemetry", "units")

    for num in range(count):
        callsign = config.get("telemetry", "unit" + str(num) + "call").upper()
        nodeid = config.get("telemetry", "unit" + str(num) + "id")
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
                        # Grab the payload of the datagram
                        paddedPacket = datagram[3]
                        # Extract the payload length from payload since padding could be used
                        telemetryData = faradayParser.ExtractPaddedPacket(paddedPacket,faradayParser.packet_3_len)
                        # Unpack payload and return a dictionary of telemetry, return tuple and dictionary
                        parsedTelemetry = faradayParser.UnpackPacket_3(telemetryData, False)

                    except StandardError as e:
                        logger.error("StandardError: " + str(e))
                    except ValueError as e:
                        logger.error("ValueError: " + str(e))
                    except IndexError as e:
                        logger.error("IndexError: " + str(e))
                    except KeyError as e:
                        logger.error("KeyError: " + str(e))

                    else:

                        sqlInsert(dbFilename,parsedTelemetry[0])
                        telemetryDicts[str(callsign) + str(nodeid)].append(parsedTelemetry[1])

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
        #limit = request.args.get("limit", 100)
        startTime = request.args.get("starttime", None)
        endTime = request.args.get("endtime", None)
        timespan = request.args.get("timespan", 5*60)

        #limit = str(limit)
        nodeid = str(nodeid)
        direction = int(direction)
        callsign = str(callsign).upper()


    except ValueError as e:
        logger.error("ValueError: " + str(e))
        return json.dumps({"error": str(e)}), 400
    except IndexError as e:
        logger.error("IndexError: " + str(e))
        return json.dumps({"error": str(e)}), 400
    except KeyError as e:
        logger.error("KeyError: " + str(e))
        return json.dumps({"error": str(e)}), 400

    # Create tuple of parameters for SQLite3
    parameters = {}
    parameters["CALLSIGN"] = callsign
    parameters["NODEID"] = nodeid
    parameters["DIRECTION"] = direction
    parameters["STARTTIME"] = startTime
    parameters["ENDTIME"] = endTime
    parameters["TIMESPAN"] = timespan

    queryResults = queryDb(parameters)

    return json.dumps(queryResults, indent=1), 200,\
            {'Content-Type': 'application/json'}

@app.route('/raw', methods=['GET'])
def rawTelemetry():
    """
    Provides a RESTful interface to the decoded raw telemetry at URL '/raw'

    Starts a flask server on port 8001 (default) which serves data from the
    requested Faraday via it's proxy interface on localhost URL "/". Callsign
    and nodeid of the Faraday radio connected via USB is required.
    """

    try:
        # Obtain URL parameters
        callsign = request.args.get("callsign")
        nodeid = request.args.get("nodeid")
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
    try:
        if callsign is None:
            # Required
            raise StandardError("Missing 'callsign' parameter")
        else:
            # Ensure callsign value is a string and all uppercase
            callsign = str(callsign).upper()
        if nodeid is None:
            # Required
            raise StandardError("Missing 'nodeid' parameter")
        else:
            nodeid = int(nodeid)
            # Check to see if the Node ID is in the valid range
            if nodeid > 255 or nodeid < 0:
                raise ValueError(
                    "Faraday Node ID's valid integer between 0-255")
        if limit is None:
            # Optional
            limit = len(telemetryDicts[str(callsign) + str(nodeid)])
        else:
            limit = int(limit)
            # Check for less than or equal to zero case
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

    # Pop data off of the queue
    try:
        if (len(telemetryDicts[str(callsign) + str(nodeid)]) > 0):
            data = []
            while telemetryDicts[str(callsign) + str(nodeid)]:
                packet = \
                    telemetryDicts[
                        str(callsign) + str(nodeid)].popleft()
                data.append(packet)
                if len(data) >= limit:
                    break

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

    return json.dumps(data, indent=1), 200,\
            {'Content-Type': 'application/json'}

@app.route('/stations', methods=['GET'])
def stations():
    """
    Provides a RESTful interface to station queries at URL '/stations'

    Starts a flask server on port 8001 (default) which serves data from the
    requested Faraday via it's proxy interface on localhost URL "/stations".
    """

    try:
        # Obtain URL parameters
        timespan = request.args.get("timespan", 15*60)
        startTime = request.args.get("starttime", None)
        endTime = request.args.get("endtime", None)

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

    parameters = {}
    parameters["TIMESPAN"] = timespan
    parameters["STARTTIME"] = startTime
    parameters["ENDTIME"] = endTime

    data = queryStationsDb(parameters)

    return json.dumps(data, indent=1), 200,\
            {'Content-Type': 'application/json'}

@app.errorhandler(404)
def pageNotFound(error):
    """HTTP 404 response for incorrect URL"""
    logger.error("Error: " + str(error))
    return json.dumps({"error": "HTTP " + str(error)}), 404

# Database Functions
def initDB():
    # Obtain configuration filenames
    dbFilename = telemetryConfig.get("database", "filename")
    dbSchema = telemetryConfig.get("database", "schemaname")

    # Check if database exists
    if os.path.isfile(dbFilename):
        pass
    else:
        # Open database schema SQL file and execute the SQL
        with open(dbSchema, 'rt') as f:
            schema = f.read()
        conn = sqlite3.connect(dbFilename)
        cur = conn.cursor()
        cur.executescript(schema)
        conn.close()

def sqlInsert(db, data):
    """Takes in database filename and data tuple and inserts data into table"""
    data = (None,) + data  # Add a null to tuple for KEYID

    # Create parameter substitute "?" string for SQL query
    numKeys = len(data)
    paramSubs = "?" * (numKeys)
    paramSubs = ",".join(paramSubs)

    # Connect to database, create SQL query, execute query, and close database
    try:
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        sql = "INSERT INTO TELEMETRY VALUES(" + paramSubs + ")"
        # Use connection as context manager to rollback automatically if error
        with conn:
            conn.execute(sql,data)

    except StandardError as e:
        logger.error("StandardError: " + str(e))
    except ValueError as e:
        logger.error("ValueError: " + str(e))
    except IndexError as e:
        logger.error("IndexError: " + str(e))
    except KeyError as e:
        logger.error("KeyError: " + str(e))

    # Completed INSERT, close database
    conn.close()

def queryDb(parameters):
    """Takes in parameters to query the SQLite database, returns the results"""
    print "PARAMS: ", parameters
    timeTuple = generateStartStopTimes(parameters)

    if parameters["DIRECTION"] == 0:
        print "source"
        sqlWhereCall = "WHERE SOURCECALLSIGN LIKE ? "
        sqlWhereID = "AND SOURCEID LIKE ? "
        sqlEpoch ="AND EPOCH BETWEEN ? AND ? "

    else:
        print "dest"
        sqlWhereCall = "WHERE DESTINATIONCALLSIGN LIKE ? "
        sqlWhereID = "AND DESTINATIONID LIKE ? "
        sqlEpoch ="AND EPOCH BETWEEN ? AND ? "


    # Initialize variables
    results = []

    # Open configuration file
    dbFilename = telemetryConfig.get("database", "filename")

    # Connect to database, create SQL query, execute query, and close database
    try:
        conn = sqlite3.connect(dbFilename)
        conn.row_factory = sqlite3.Row

    except StandardError as e:
        logger.error("StandardError: " + str(e))
    except ValueError as e:
        logger.error("ValueError: " + str(e))
    except IndexError as e:
        logger.error("IndexError: " + str(e))
    except KeyError as e:
        logger.error("KeyError: " + str(e))

    cur = conn.cursor()
    sqlBeg = "SELECT * FROM TELEMETRY "
    sqlEnd = "ORDER BY KEYID DESC"
    sql = sqlBeg + sqlWhereCall + sqlWhereID + sqlEpoch + sqlEnd
    print sql
    #parameters["LIMIT"] = 5
    #print parameters["LIMIT"]
    try:
        cur.execute(sql,(parameters["CALLSIGN"].upper(),parameters["NODEID"], str(timeTuple[0]), str(timeTuple[1])))
        rows = cur.fetchall()

        sqlData = []
        for row in rows:
            rowData = {}
            for parameter in row.keys():
                rowData[parameter] = row[parameter]
            sqlData.append(rowData)

    except StandardError as e:
        logger.error("StandardError: " + str(e))
    except ValueError as e:
        logger.error("ValueError: " + str(e))
    except IndexError as e:
        logger.error("IndexError: " + str(e))
    except KeyError as e:
        logger.error("KeyError: " + str(e))

    # Completed query, close database
    conn.close()

    return sqlData

def queryStationsDb(parameters):
    """Takes in parameters to query the SQLite database, returns the results"""
    print parameters

    if parameters["STARTTIME"] != None and parameters["ENDTIME"] != None:
        # Start end end times provided, ignore timespan
        startTime = str(parameters["STARTTIME"])
        endTime = str(parameters["ENDTIME"])
        timeTuple = iso8601ToEpoch(startTime,endTime)
    else:
        # We should use the timespan provided to generate start and stop times
        endEpoch = time.time()
        startEpoch = endEpoch - float(parameters["TIMESPAN"])
        timeTuple = (startEpoch, endEpoch)

    # Initialize variables
    results = []
    currentTime = time.time()
    try:
        startTime = float(currentTime) - float(parameters["TIMESPAN"])
    except:
        print "fail"

    # Open configuration file
    dbFilename = telemetryConfig.get("database", "filename")

    # Connect to database, create SQL query, execute query, and close database
    try:
        conn = sqlite3.connect(dbFilename)
        conn.row_factory = sqlite3.Row

    except StandardError as e:
        logger.error("StandardError: " + str(e))
    except ValueError as e:
        logger.error("ValueError: " + str(e))
    except IndexError as e:
        logger.error("IndexError: " + str(e))
    except KeyError as e:
        logger.error("KeyError: " + str(e))

    cur = conn.cursor()
    sqlBeg = "SELECT SOURCECALLSIGN, SOURCEID, EPOCH FROM TELEMETRY "
    sqlWhere = "WHERE EPOCH BETWEEN ? AND ? "
    sqlEnd = "GROUP BY SOURCECALLSIGN, SOURCEID ORDER BY EPOCH DESC"
    sql = sqlBeg + sqlWhere + sqlEnd
    try:
        cur.execute(sql,timeTuple)
        rows = cur.fetchall()

        sqlData = []
        for row in rows:
            rowData = {}
            for parameter in row.keys():
                rowData[parameter] = row[parameter]
            sqlData.append(rowData)

    except StandardError as e:
        logger.error("StandardError: " + str(e))
    except ValueError as e:
        logger.error("ValueError: " + str(e))
    except IndexError as e:
        logger.error("IndexError: " + str(e))
    except KeyError as e:
        logger.error("KeyError: " + str(e))

    # Completed query, close database
    conn.close()

    return sqlData

def generateStartStopTimes(parameters):
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
        print timeTuple

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
    telemetryHost = telemetryConfig.get("flask", "host")
    telemetryPort = telemetryConfig.getint("flask", "port")

    app.run(host=telemetryHost, port=telemetryPort, threaded=True)

if __name__ == '__main__':
    main()
#-------------------------------------------------------------------------------
# Name:        /faraday/telemetry.py
# Purpose:      Query proxy for telemetry data and parse it to a local database
#               as well as provide a RESTful interface to decoded data.
#
# Author:      Bryce Salmi
#
# Created:     11/10/2016
# Licence:     GPLv3
#-------------------------------------------------------------------------------

import time
import threading
import ConfigParser
from collections import deque
import os
import sqlite3
import json
import sys
import argparse
import shutil

from flask import Flask
from flask import request
from flask_cors import CORS

from faraday.proxyio import faradaybasicproxyio
from faraday.proxyio import telemetryparser
from classes import helper

configTruthFile = "telemetry.sample.ini"
configFile = "telemetry.ini"

# Start logging after importing modules
faradayHelper = helper.Helper("Telemetry")
logger = faradayHelper.getLogger()

# Load Telemetry Configuration from telemetry.ini file
telemetryConfig = ConfigParser.RawConfigParser()

# Create and initialize dictionary queues
telemetryDicts = {}

# Command line input
parser = argparse.ArgumentParser(description='Telemetry application saves and queries Faraday telemetry')
parser.add_argument('--init-config', dest='init', action='store_true', help='Initialize Telemetry configuration file')
parser.add_argument('--callsign', help='Set Faraday callsign in Proxy to connect to')
parser.add_argument('--nodeid', type=int, help='Set Faraday node ID in Proxy to connect to')
parser.add_argument('--unit', type=int, default=0, help='Specify Faraday unit to configure')
parser.add_argument('--start', action='store_true', help='Start Telemetry server')
parser.add_argument('--proxyhost', help='Set hostname/IP of Proxy to connect to')

# Telemetry database options
parser.add_argument('--database', help='Set Telemetry database name')
parser.add_argument('--schema', help='Set Telemetry database schema')
parser.add_argument('--init-log', dest='initlog', action='store_true', help='Initialize Telemetry log database')
parser.add_argument('--save-log', dest='savelog', help='Save Telemetry log database into new SAVELOG file')
parser.add_argument('--show-logs', dest='showlogs', action='store_true', help='Show Telemetry log database files')

# Telemetry Flask options
parser.add_argument('--flask-host', dest='flaskhost', help='Set Faraday Telemetry Flask server host address')
parser.add_argument('--flask-port', type=int, dest='flaskport', help='Set Faraday Telemetry Flask server port')

# Parse the arguments
args = parser.parse_args()

def openDB():
    # Read in name of database
    try:
        dbFilename = telemetryConfig.get("DATABASE", "FILENAME")
        dbPath = os.path.join(faradayHelper.userPath, 'lib', dbFilename)
        logger.debug("Telemetry Database: " + dbPath)
        dbFilename = os.path.join(dbPath)

    except ConfigParser.Error as e:
        logger.error("ConfigParse.Error: " + str(e))
        return False

    # Connect to database, create SQL query, execute query, and close database
    try:
        conn = sqlite3.connect(dbFilename)

    except sqlite3.Error as e:
        logger.error("Sqlite3.error: " + str(e))
        conn.close()

    return conn


def initializeTelemetryConfig():
    '''
    Initialize telemetry configuration file from telemetry.sample.ini

    :return: None, exits program
    '''

    faradayHelper.initializeConfig(configTruthFile, configFile)
    sys.exit(0)


def initializeTelemetryLog(config):
    '''
    Initialize the log database by deleting file

    :param config: Telemetry ConfigParser object from telemetry.ini
    :return: None
    '''

    logger.info("Initializing Telemetry Log File")
    log = config.get("DATABASE", "filename")
    logpath = os.path.join(faradayHelper.userPath, 'lib', log)

    try:
        os.remove(logpath)
        logger.info("Log initialization complete")

    except OSError as e:
        logger.error(e)


def saveTelemetryLog(name, config):
    '''
    Save telemetry log database into a new file

    :param name: Name of file to save data into (should be .db)
    :param config: Telemetry ConfigParser object from telmetry.ini
    :return: None
    '''

    log = config.get("DATABASE", "filename")
    oldpath = os.path.join(faradayHelper.userPath, 'lib', log)
    newpath = os.path.join(faradayHelper.userPath, 'lib', name)
    try:
        shutil.move(oldpath, newpath)
        sys.exit(0)

    except shutil.Error as e:
        logger.error(e)
    except IOError as e:
        logger.error(e)


def showTelemetryLogs():
    '''
    Show telemetry log database filenames in user path ~/.faraday/lib folder

    :return: None, exits program
    '''

    logger.info("The following logs exist for Telemetry...")
    path = os.path.join(faradayHelper.userPath, 'lib')
    for file in os.listdir(path):
        if file.endswith(".db"):
            logger.info(file)
    sys.exit(0)


def configureTelemetry(args):
    '''
    Configure telemetry configuration file from command line

    :param args: argparse arguments
    :return: None
    '''

    config = ConfigParser.RawConfigParser()
    config.read(os.path.join(faradayHelper.path, configFile))

    # Configure UNITx sections
    unit = 'UNIT' + str(args.unit)
    if args.unit is not 0:
        try:
            config.set('TELEMETRY', unit + "CALL", "REPLACEME")
            config.set('TELEMETRY', unit + "ID", "REPLACEME")

        except ConfigParser.DuplicateSectionError:
            pass

    if args.callsign is not None:
        config.set('TELEMETRY', unit + 'CALL', args.callsign)
    if args.nodeid is not None:
        config.set('TELEMETRY', unit + 'ID', args.nodeid)
    if args.proxyhost is not None:
        config.set('TELEMETRY', 'proxyhost', args.proxyhost)

    #Configure Telemetry databases
    if args.database is not None:
        config.set('DATABASE', 'filename', args.database)
    if args.schema is not None:
        config.set('DATABASE', 'schemaname', args.schema)

    # Configure Telemetry flask server
    if args.flaskhost is not None:
        config.set('FLASK', 'host', args.flaskhost)
    if args.flaskport is not None:
        config.set('FLASK', 'port', args.flaskport)

    filename = os.path.join(faradayHelper.path, configFile)
    with open(filename, 'wb') as configfile:
        config.write(configfile)


# Now act upon the command line arguments
# Initialize and configure telemetry
if args.init:
    initializeTelemetryConfig()
configureTelemetry(args)

# Read in telemetry configuration parameters
telemetryFile = telemetryConfig.read(os.path.join(faradayHelper.path, configFile))

# Initialize Telemetry log database
if args.initlog:
    initializeTelemetryLog(telemetryConfig)

# Save Telemetry log database
if args.savelog is not None:
    saveTelemetryLog(args.savelog, telemetryConfig)

# List Telemetry log database files
if args.showlogs:
    showTelemetryLogs()

# Check for --start option and exit if not present
if not args.start:
    logger.warning("--start option not present, exiting Telemetry server!")
    sys.exit(0)


if len(telemetryFile) == 0:
    #  File missing, indicate error and infinite loop
    while True:
            logger.error("telemetry.ini missing")
            time.sleep(1)


def telemetry_worker(config):
    """
    Interface Faraday Proxy to obtain telemetry

    This function interfaces the Proxy application via its RESTful interface.
    It is a one-way operation as it makes no sense to POST data to proxy for
    telemetry to a specific unit with this application. This function runs
    in an infinite loop continually querying for data.

    :param config: telemetry.ini ConfigParser object
    :return: Nothing
    """
    logger.info('Starting telemetry_worker thread')

    # initialize variables
    stations = {}
    count = 0

    # Initialize proxy object
    proxy = faradaybasicproxyio.proxyio()

    # Initialize Faraday parser
    faradayParser = telemetryparser.TelemetryParse()  # Add logger?

    try:
        # Pragmatically create descriptors for each Faraday connected to Proxy
        count = config.getint("TELEMETRY", "UNITS")

    except ConfigParser.Error as e:
            #  Error reading in configs so get stuck in infinite loop indicating problem
            while True:
                logger.error("ConfigParse.Error: " + str(e))
                time.sleep(1)

    for num in range(count):
        try:
            callsign = config.get("TELEMETRY", "UNIT" + str(num) + "CALL").upper()
            nodeid = config.get("TELEMETRY", "UNIT" + str(num) + "ID")
            proxyHost = str(config.get("TELEMETRY", "proxyhost"))

        except ConfigParser.Error as e:
            #  Error reading in configs so get stuck in infinite loop indicating problem
            while True:
                logger.error("ConfigParse.Error: " + str(e))
                time.sleep(1)

        stations["UNIT" + str(num) + "CALL"] = callsign
        stations["UNIT" + str(num) + "ID"] = nodeid
        telemetryDicts[str(callsign) + str(nodeid)] = deque([], maxlen=1000)

    #  Check for data on telemetry port with infinite loop.
    while True:
        for radio in range(count):
            callsign = stations["UNIT" + str(num) + "CALL"]
            nodeid = stations["UNIT" + str(num) + "ID"]
            data = proxy.GET(proxyHost, str(callsign), str(nodeid), int(proxy.TELEMETRY_PORT))

            if type(data) is dict:
                #  A dict means something is wrong with GET, print error JSON
                logger.info(data["error"])

            elif data is None:
                #  No data is available from Proxy
                logger.debug("telemetryworker data GET response = None")

            else:
                # Iterate through each packet and unpack into dictionary
                logger.debug("Proxy data: " + repr(data))
                for item in data:
                    try:
                        # Decode BASE64 JSON data packet into
                        unPackedItem = proxy.DecodeRawPacket(item["data"])
                        # Unpack packet into datagram elements
                        datagram = faradayParser.UnpackDatagram(unPackedItem, False)
                        # Extract the payload length from payload since padding could be used
                        telemetryData = faradayParser.ExtractPaddedPacket(datagram["PayloadData"], faradayParser.packet_3_len)
                        # Unpack payload and return a dictionary of telemetry, return tuple and dictionary
                        parsedTelemetry = faradayParser.UnpackPacket_3(telemetryData, False)

                    except ValueError as e:
                        logger.error("ValueError: " + str(e))
                    except IndexError as e:
                        logger.error("IndexError: " + str(e))
                    except KeyError as e:
                        logger.error("KeyError: " + str(e))

                    else:
                        workerDB = openDB()
                        sqlInsert(workerDB, parsedTelemetry)
                        telemetryDicts[str(callsign) + str(nodeid)].append(parsedTelemetry)
        time.sleep(1)  # Slow down main while loop


# Initialize Flask microframework
app = Flask(__name__)
# Enable CORS support
CORS(app)


@app.route('/', methods=['GET'])
def dbTelemetry():
    """
    Provides a RESTful interface to telemetry in the SQLite database at URL '/'

    Serves JSON responses to the "/" URL containing output of SQLite queries.
    Specific SQLite queries can return data from specified ranges and source
    stations as

    :return: JSON formatted string with data or error message and HTTP response
    """

    #  Initialize local variables
    parameters = {}
    data = []

    try:
        # Obtain URL parameters
        callsign = request.args.get("callsign", "%")
        nodeid = request.args.get("nodeid", "%")
        direction = request.args.get("direction", 0)
        startTime = request.args.get("starttime", None)
        endTime = request.args.get("endtime", None)
        timespan = request.args.get("timespan", 5 * 60)
        limit = request.args.get("limit")

    except IOError as e:
        logger.error("IOError: " + str(e))
        return json.dumps({"error": str(e)}), 400

    nodeid = str(nodeid)
    direction = int(direction)
    callsign = str(callsign).upper()
    timespan = int(timespan)
    if limit is not None:
        limit = int(limit)

    # Validate timespan
    if timespan <= 0:
        message = "Error: Timespan '{0}' is invalid".format(timespan)
        return json.dumps({"error": message}), 400

    # Create tuple of parameters for SQLite3
    parameters["CALLSIGN"] = callsign
    parameters["NODEID"] = nodeid
    parameters["DIRECTION"] = direction
    parameters["STARTTIME"] = startTime
    parameters["ENDTIME"] = endTime
    parameters["TIMESPAN"] = timespan
    parameters["LIMIT"] = limit

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
        if callsign is None and nodeId is None:
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
        timespan = request.args.get("timespan", 5 * 60)
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
        logger.info("No stations have been heard in last %d seconds", timespan)
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
    """
    Initialize database, creates it if not present

    :return: True or False if successful
    """

    # make directory tree, necessary?
    try:
        os.makedirs(os.path.join(faradayHelper.userPath, 'lib'))
    except:
        pass

    # Obtain configuration file names, always place at sys.prefix
    try:
        dbFilename = telemetryConfig.get("DATABASE", "FILENAME")
        dbPath = os.path.join(faradayHelper.userPath, 'lib', dbFilename)
        logger.debug("Telemetry Database: " + dbPath)
        dbFilename = dbPath

        dbSchema = telemetryConfig.get("DATABASE", "SCHEMANAME")
        dbSchema = os.path.join(faradayHelper.path, dbSchema)

    except ConfigParser.Error as e:
        logger.error("ConfigParse.Error: " + str(e))
        return False

    # Check if database exists
    if os.path.isfile(dbFilename):
        pass
    else:
        # Open database schema SQL file and execute the SQL functions inside
        # after connecting. Close the database when complete.
        try:
            with open(dbSchema, 'rt') as f:
                #conn = sqlite3.connect(dbFilename)
                initConn = openDB()
                cur = initConn.cursor()
                schema = f.read()
                cur.executescript(schema)
            initConn.close()

        except sqlite3.Error as e:
            logger.error("Sqlite3.Error: " + str(e))
            return False

    return True


def createTelemetryList(data):
    """
    Converts data dictionary into a defined list for insertion into SQLite db

    SQLite3 insertions require that the data be ordered correctly. Python dictionaries
    do not guarantee order so a list is greated from the dictionary.

    :param data: Telemetry dictionary
    :return: list that contains telemetry data
    """

    # Create list of dictionary data in appropriate order
    # First statement in None for KeyID
    try:
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
                data["IOSTATE"],
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

    except KeyError as e:
        logger.error("KeyError: " + str(e))
        temp = []

    return temp


def sqlInsert(dbConn, data):
    """
    Takes in a data tuple and inserts int into the telemetry SQLite table

    :param data: Telemetry dictionary
    :return: Status True or False on SQL insertion success
    """

    # Read in name of database
    # try:
    #     dbFilename = telemetryConfig.get("DATABASE", "FILENAME")
    #     dbPath = os.path.join(faradayHelper.userPath, 'lib', dbFilename)
    #     logger.debug("Telemetry Database: " + dbPath)
    #     db = os.path.join(dbPath)
    #
    # except ConfigParser.Error as e:
    #     logger.error("ConfigParse.Error: " + str(e))
    #     return False

    # Change dictionary into list with proper order
    telem = createTelemetryList(data)

    # Check if length of telem is correct
    if len(telem) > 0:
        # Create parameter substitute "?" string for SQL query then create SQL
        numKeys = len(telem)
        paramSubs = "?" * (numKeys)
        paramSubs = ",".join(paramSubs)
        sql = "INSERT INTO TELEMETRY VALUES(" + paramSubs + ")"

        # Connect to database, create SQL query, execute query, and close database
        # try:
        #     conn = sqlite3.connect(db)
        #
        # except sqlite3.Error as e:
        #     logger.error("Sqlite3.Error: " + str(e))
        #     return False

        # Connect to database, create SQL query, execute query, and close database
        try:
            #conn = sqlite3.connect(db)
            # Use connection as context manager to rollback automatically if error
            with dbConn:
                dbConn.execute(sql, telem)

        except sqlite3.Error as e:
            logger.error("Sqlite3.Error: " + str(e))
            dbConn.rollback()
            dbConn.close()
            return False

        # Completed, close database and return True
        dbConn.close()
        return True

    else:
        return False


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
    :return: List of SQL output where each item is a dictionary, empty list when error
    """

    #Declare sqlData
    sqlData = []

    # Use supplied parameters to generate a Tuple of epoch start/stop times
    # SQLite3 parameters need to be Tuples
    timeTuple = generateStartStopTimes(parameters)
    callsign = parameters["CALLSIGN"]
    nodeid = parameters["NODEID"]
    limit = parameters["LIMIT"]

    #Check for timeTuple = None
    try:
        if timeTuple is None:
            raise StandardError("Start and Stop times caused and error")

    except StandardError as e:
        logger.error("StandardError: " + str(e))
        return sqlData

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
    sqlEpoch = "AND EPOCH BETWEEN ? AND ? "
    sqlEnd = "ORDER BY KEYID DESC"
    if limit is not None:
        sqlEnd = sqlEnd + " LIMIT ?"
        paramTuple = (callsign, nodeid) + timeTuple + (limit,)
    else:
        paramTuple = (callsign, nodeid) + timeTuple

    # Create  SQL Query string
    sql = sqlBeg + sqlWhereCall + sqlWhereID + sqlEpoch + sqlEnd
    logger.debug(sql)

    # Read in name of database
    # try:
    #     dbFilename = telemetryConfig.get("DATABASE", "FILENAME")
    #     dbPath = os.path.join(faradayHelper.userPath, 'lib', dbFilename)
    #     logger.debug("Telemetry Database: " + dbPath)
    #     dbFilename = os.path.join(dbPath)
    #
    # except ConfigParser.Error as e:
    #     logger.error("ConfigParse.Error: " + str(e))
    #     return False

    # Connect to database, create SQL query, execute query, and close database
    try:
        #conn = sqlite3.connect(dbFilename)
        queryConn = openDB()

    except sqlite3.Error as e:
        logger.error("Sqlite3.Error: " + str(e))
        logger.error(paramTuple)
        return sqlData

    queryConn.row_factory = sqlite3.Row  # Row_factory returns column/values
    cur = queryConn.cursor()

    try:
        cur.execute(sql, paramTuple)

    except sqlite3.Error as e:
        logger.error("Sqlite3.Error: " + str(e))
        logger.error(paramTuple)
        queryConn.close()
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
        queryConn.close()
        return sqlData

    # Completed query, close database, return sqlData list of dictionaries
    queryConn.close()
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

    timeTuple = generateStartStopTimes(parameters)

    # Specify and create SQL command string
    sqlBeg = "SELECT SOURCECALLSIGN, SOURCEID, EPOCH FROM TELEMETRY "
    sqlWhere = "WHERE EPOCH BETWEEN ? AND ? "
    sqlEnd = "GROUP BY SOURCECALLSIGN, SOURCEID ORDER BY EPOCH DESC"

    #  Check if callsign/nodeid provided, return the last time it was heard
    if parameters["CALLSIGN"] != "%":

        # Update the sqlWhere strings for this query
        sqlWhere = sqlWhere + "AND SOURCECALLSIGN LIKE ?"

        # Create paramTuple for SQLite3 execute function
        paramTuple = timeTuple + (parameters["CALLSIGN"],)

        #  Check if nodeid was given, add into SQL query if it was
        if parameters["NODEID"] != "%":

            # Update the sqlWhere strings for this query
            sqlWhere = sqlWhere + " AND SOURCEID LIKE ?"

            # Create paramTuple for SQLite3 execute function
            paramTuple += (parameters["NODEID"],)

    else:
        # Create paramTuple for SQLite3 execute function do not include callsign
        paramTuple = timeTuple

    # Create SQL query string
    sql = sqlBeg + sqlWhere + sqlEnd

    # Read in name of database
    try:
        dbFilename = telemetryConfig.get("DATABASE", "FILENAME")
        dbPath = os.path.join(faradayHelper.userPath, 'lib', dbFilename)
        logger.debug("Telemetry Database: " + dbPath)
        dbFilename = os.path.join(dbPath)

    except ConfigParser.Error as e:
        logger.error("ConfigParse.Error: " + str(e))
        return False

    # Connect to database, create SQL query, execute query, and close database
    try:
        #conn = sqlite3.connect(dbFilename)
        queryStationsDB = openDB()

    except sqlite3.Error as e:
        logger.error("Sqlite3.error: " + str(e))
        logger.error(paramTuple)
        return sqlData

    queryStationsDB.row_factory = sqlite3.Row  # SQLite.Row returns columns,values
    cur = queryStationsDB.cursor()

    try:
        cur.execute(sql, paramTuple)

    except sqlite3.Error as e:
        logger.error("Sqlite3.error: " + str(e))
        logger.error(paramTuple)
        queryStationsDB.close()
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
        queryStationsDB.close()
        return sqlData

    # Completed query, close database, return list of dictionary data for JSON
    queryStationsDB.close()
    return sqlData


def generateStartStopTimes(parameters):
    """
    Use parameters dictionary to build up a Tuple of start/stop time values

    :param parameters: dictionary with 'STARTTIME', 'ENDTIME' ISO 8601 keys:val
    :return: Tuple containing epoch times from input ISO 8601 times
    """

    # Check if start and stop times were provided in ISO 8610 format,
    # if not then generate epoch from timespan
    if parameters["STARTTIME"] is not None and parameters["ENDTIME"] is not None:
        # Start end end times provided, ignore timespan
        startTime = str(parameters["STARTTIME"])
        endTime = str(parameters["ENDTIME"])
        timeTuple = iso8601ToEpoch(startTime, endTime)

    elif parameters["STARTTIME"] is not None:
        # Start time provided, use current time as end, ignore timespan
        startTime = str(parameters["STARTTIME"])
        endTime = time.strftime("%Y-%m-%dT%H:%M:%S")
        timeTuple = iso8601ToEpoch(startTime, endTime)

    else:
        # We should use the timespan provided to generate start and stop times
        endEpoch = time.time()
        startEpoch = endEpoch - float(parameters["TIMESPAN"])
        timeTuple = (int(startEpoch), int(endEpoch))

    return timeTuple


def iso8601ToEpoch(startTime, endTime):
    """
    Converts ISO 8601 start and stop times into epoch time values

    :param startTime: ISO 8601 time
    :param endTime: ISO 8601 time
    :return: tuple with EPOCH times (START,STOP). None if error.
    """

    # Date format is ISO 8601
    fmt = "%Y-%m-%dT%H:%M:%S"

    try:
        # Generate start and stop time tuples
        start = time.strptime(startTime, fmt)
        end = time.strptime(endTime, fmt)

        # Convert time tuples to epoch times
        startEpoch = time.mktime(start)
        endEpoch = time.mktime(end)

    except StandardError as e:
        logger.error("StandardError: " + str(e))
        return None

    # Create a tuple of the start and stop time, return it
    timeTuple = (startEpoch, endEpoch)
    return timeTuple


def main():
    """
    Main function which starts telemery worker thread + Flask server.

    :return: Nothing
    """
    logger.info('Starting telemetry server')

    # Initialize local variables
    threads = []

    # Open or create database if it doesn't exist
    initDB()

    t = threading.Thread(target=telemetry_worker, args=(telemetryConfig,))
    threads.append(t)
    t.start()

    # Start the flask server on host:port
    try:
        telemetryHost = telemetryConfig.get("FLASK", "HOST")
        telemetryPort = telemetryConfig.getint("FLASK", "PORT")

    except ConfigParser.Error as e:
        while True:
            logger.error("ConfigParse.Error: " + str(e))
            time.sleep(1)

    app.run(host=telemetryHost, port=telemetryPort, threaded=True)


if __name__ == '__main__':
    main()

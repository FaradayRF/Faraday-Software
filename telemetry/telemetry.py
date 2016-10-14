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
def telemetry():
    """
    Provides a RESTful interface to the decoded telemetry '/'

    Starts a flask server on port 8001 (default) which serves data from the
    requested Faraday via it's proxy interface on localhost URL "/".
    """
    if request.method == "GET":  # Needed?
        pass

        dbFilename = telemetryConfig.get("database", "filename")
        conn = sqlite3.connect(dbFilename)
        #print conn

        return str(conn), 200

@app.route('/raw', methods=['GET'])
def rawTelemetry():
    """
    Provides a RESTful interface to the decoded raw telemetry '/raw'

    Starts a flask server on port 8001 (default) which serves data from the
    requested Faraday via it's proxy interface on localhost URL "/".
    """
    if request.method == "GET":  # Needed?

        # Initialize variables


        callsign = request.args.get("callsign")
        nodeid = request.args.get("nodeid")
        limit = request.args.get("limit")

        # Convert to corrent datatypes to work with expected types
        # Might want to consider checking values for correct ranges
        callsign = str(callsign).upper()
        nodeid = int(nodeid)
        limit = int(limit)

        data = []
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
        sql = "INSERT INTO TELEMETRY VALUES(" + paramSubs + ")"
        conn.execute(sql,data)
        conn.commit()
        conn.close()

    except StandardError as e:
        logger.error("StandardError: " + str(e))
    except ValueError as e:
        logger.error("ValueError: " + str(e))
    except IndexError as e:
        logger.error("IndexError: " + str(e))
    except KeyError as e:
        logger.error("KeyError: " + str(e))

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
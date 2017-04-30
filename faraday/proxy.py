# /Proxy/proxy.py
# License: GPLv3 with Network Interface Clause

"""
Proxy is meant to communicate with a Faraday Radio over USB UART via a serial
port. It has a thread which continuously checks for data over USB and places it
into a thread safe dequeue. The Flask server returns requested data from this
queue with a GET request or adds to it with a POST request via an IP address
and port specified in the configuration file proxy.ini.
"""

import base64
from collections import deque
import ConfigParser
import json
import logging.config
import os
import sqlite3
import sys
import threading
import time

from flask import Flask
from flask import request

from faraday.uart import layer_4_service

# Start logging after importing modules
filename = os.path.abspath("loggingConfig.ini")
logging.config.fileConfig(filename)
logger = logging.getLogger('Proxy')

# Load Proxy Configuration from proxy.ini file
proxyConfig = ConfigParser.RawConfigParser()
filename = os.path.abspath("proxy.ini")
proxyConfig.read(filename)

# Create and initialize dictionary queues
postDict = {}
postDicts = {}
getDicts = {}
unitDict = {}


def uart_worker(modem, getDicts, units, log):
    """
    Interface Faraday ports over USB UART

    This function interfaces the USB UART serial data with an infinite loop
    that checks all Faraday "ports" for data and appends/pops data from
    queues for send and receive directions.
    """
    logger.info('Starting uart_worker thread')

    # Iterate through dictionary of each unit in the dictionary creating a
    # deque for each item
    postDicts[modem['unit']] = {}
    getDicts[modem['unit']] = {}

    # Loop through each unit checking for data, if True place into deque
    while(1):
        # Place data into the FIFO coming from UART
        try:
            for port in modem['com'].RxPortListOpen():
                if(modem['com'].RxPortHasItem(port)):
                    for i in range(0, modem['com'].RxPortItemCount(port)):
                        # Data is available
                        # convert to BASE64 and place in queue
                        item = {}
                        item["data"] = base64.b64encode(modem['com'].GET(port))

                        try:
                            getDicts[modem['unit']][port].append(item)

                        except:
                            getDicts[modem['unit']][port] = deque([], maxlen=100)
                            getDicts[modem['unit']][port].append(item)

                        # Check for Proxy logging and save to SQL if true
                        if log:
                            item["port"] = port
                            sqlInsert(item)

        except StandardError as e:
            logger.error("StandardError: " + str(e))
        except ValueError as e:
            logger.error("ValueError: " + str(e))
        except IndexError as e:
            logger.error("IndexError: " + str(e))
        except KeyError as e:
            logger.error("KeyError: " + str(e))

        # Check for data in the POST FIFO queue. This needs to check for
        # COM ports and create the necessary buffers on the fly
        for port in postDicts[modem['unit']].keys():
            try:
                count = len(postDicts[modem['unit']][port])
            except:
                # Port simply doesn't exist so don't bother
                pass
            else:
                for num in range(count):
                    # Data is available, pop off [unit][port] queue
                    # and convert to BASE64 before sending to UART
                    message = postDicts[modem['unit']][port].popleft()
                    message = base64.b64decode(message)
                    modem['com'].POST(port, len(message), message)

        # Slow down while loop to something reasonable
        time.sleep(0.01)


def testdb_read_worker():
    """
    Read from DB and insert traffic in deque

    This function periodically appends traffic obtained from a
    pre-generated SQLite database to the deque as if there were
    hardware attached.  This is to enable testing when hardware
    is not present.  The callsign and nodeid are derived from
    the config file.
    """
    logger.info('Starting testdb_read_worker thread')

    # Obtain the test callsign and nodeid and create a
    # deque

    # Obtain configuration properties
    try:
        testCallsign = proxyConfig.get("PROXY", "TESTCALLSIGN")
        testNodeId = proxyConfig.getint("PROXY", "TESTNODEID")
        testRate = proxyConfig.getint("PROXY", "TESTRATE")

    except ConfigParser.Error as e:
        logger.error("ConfigParse.Error: " + str(e))
        return None

    if int(testRate) <= 0:
        logger.warn('Test packet rate invalid, TESTRATE = [ {} ]'
                    ' setting rate to [ 1 ] per second.'
                    .format(int(testRate)))
        testRate = 1

    sleepTime = 1.0 / testRate
    unit = testCallsign + "-" + str(testNodeId)
    getDicts[unit] = {}

    conn = openTestDB()
    if conn is None:
        return

    cursor = sqlBeginRead(conn)
    if cursor is None:
        return

    row = cursor.fetchone()

    # Loop through each row placing each row into deque
    while(row is not None):

        port = row[1]
        item = {}
        item["data"] = row[2]
        try:
            getDicts[unit][port].append(item)

        except:
            getDicts[unit][port] = deque([], maxlen=100)
            getDicts[unit][port].append(item)

        logger.debug('Appended packet: id [ {} ] port [ {} ]'
                     ' data [ {} ] ts [ {} ] '
                     .format(row[0], port, item, row[3]))

        time.sleep(sleepTime)
        row = cursor.fetchone()


# Initialize Flask microframework
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def proxy():
    """
    Provides a RESTful interface to the USB UART on localhost '/'

    Starts a flask server on port 8000 (default) which serves data from the
    requested Faraday port on localhost URL "/". This simple server is the
    intermediary between the USB UART of a Faraday radio and software
    applications. All data is transferred to the localhost as BASE64 packets in
    JSON dictionaries while all data tranferred over USB UART is converted to
    raw bytes.
    """
    if request.method == "POST":
        try:
            data = request.get_json(force=False)  # Requires HTTP JSON header
            port = request.args.get("port")
            callsign = request.args.get("callsign").upper()
            nodeid = request.args.get("nodeid")

            # Check for parameters and ensure all required are present and of
            # acceptable values

            if port is None:
                # Required
                raise StandardError("Missing 'port' parameter")
            else:
                # Ensure port value is an Integer
                port = int(port)
                # Check to see if the port is in the valid range
                if port > 255 or port < 0:
                    raise ValueError(
                        "Faraday Ports valid integer between 0-255")

            if callsign is None:
                # Required
                raise StandardError("Missing 'callsign' parameter")
            else:
                # Ensure callsign value is a string
                callsign = str(callsign)

            if nodeid is None:
                # Required
                raise StandardError("Missing 'nodeid' parameter")
            else:
                nodeid = int(nodeid)
                # Check to see if the Node ID is in the valid range
                if nodeid > 255 or nodeid < 0:
                    raise ValueError(
                        "Faraday Node ID's valid integer between 0-255")

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

        # Create station name and check for presents of postDicts queue.
        # Error if not present since this means unit not in proxy.ini configs
        station = callsign + "-" + str(nodeid)
        try:
            postDicts[station]
        except KeyError as e:
            logger.error("KeyError: " + str(e))
            return json.dumps({"error": str(e)}), 400

        # Iterate through items in the data["data"] array. If port isn't
        # present, create port queue for it and append data to that queue
        try:
            data["data"]
        except:
            logger.error("Error: No 'data' key in dictionary")
            return json.dumps(
                {"error": "Error: No 'data' key in dictionary"}), 400
        else:
            total = len(data["data"])
            print "length:", total
            sent = 0
            for item in data['data']:
                try:
                    postDicts[station][port].append(item)
                except:
                    postDicts[station][port] = deque([], maxlen=100)
                    postDicts[station][port].append(item)
                sent += 1
            return json.dumps(
                {"status": "Posted {0} of {1} Packet(s)"
                    .format(sent, total)}), 200

    else:
        # This is the GET routine to return data to the user
        try:
            port = request.args.get("port")
            limit = request.args.get("limit", 100)
            callsign = request.args.get("callsign").upper()
            nodeid = request.args.get("nodeid")

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
            if port is None:
                # Required
                raise StandardError("Missing 'port' parameter")
            else:
                # Ensure port value is an Integer
                port = int(port)
                # Check to see if the port is in the valid range
                if port > 255 or port < 0:
                    raise ValueError(
                        "Faraday Ports valid integer between 0-255")
            if callsign is None:
                # Required
                raise StandardError("Missing 'callsign' parameter")
            else:
                # Ensure callsign value is a string
                callsign = str(callsign)
            if nodeid is None:
                # Required
                raise StandardError("Missing 'nodeid' parameter")
            else:
                nodeid = int(nodeid)
                # Check to see if the Node ID is in the valid range
                if nodeid > 255 or nodeid < 0:
                    raise ValueError(
                        "Faraday Node ID's valid integer between 0-255")

            # Make sure port exists before checking it's contents and length
            station = callsign + "-" + str(nodeid)
            try:
                getDicts[station][port]
            except KeyError as e:
                message = "KeyError: " +\
                    "Callsign '{0}' or Port '{1}' does not exist"\
                    .format(station, port)
                logger.error(message)
                return json.dumps({"error": message}), 400

            if limit is None:
                # Optional
                limit = len(getDicts[station][port])
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
        # Return data from queue to RESTapi
        # If data is in port queu, turn it into JSON and return
        try:
            if (len(getDicts[callsign + "-" + str(nodeid)][port]) > 0):
                data = []
                while getDicts[callsign + "-" + str(nodeid)][port]:
                    packet = \
                        getDicts[
                            callsign + "-" + str(nodeid)][port].popleft()
                    data.append(packet)
                    if len(data) >= limit:
                        break

                return json.dumps(data, indent=1), 200,\
                    {'Content-Type': 'application/json'}
            else:
                # No data in service port, but port is being used
                logger.info("Empty buffer for port %d", port)
                return '', 204  # HTTP 204 response cannot have message data

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


@app.errorhandler(404)
def pageNotFound(error):
    """HTTP 404 response for incorrect URL"""
    logger.error("Error: " + str(error))
    return json.dumps({"error": "HTTP " + str(error)}), 404


def callsign2COM():
    """ Associate configuration callsigns with serial COM ports"""
    local = {}
    num = int(proxyConfig.get('PROXY', 'units'))
    units = range(0, num)

    for unit in units:
        # TODO We don't really check for valid input here yet
        item = "UNIT" + str(unit)
        callsign = proxyConfig.get(item, "callsign").upper()
        nodeid = proxyConfig.get(item, "nodeid")
        com = proxyConfig.get(item, "com")
        baudrate = proxyConfig.getint(item, "baudrate")
        timeout = proxyConfig.getint(item, "timeout")
        local[str(item)] = {
            "callsign": callsign,
            "nodeid": nodeid,
            "com": com,
            "baudrate": baudrate,
            "timeout": timeout
        }

    local = json.dumps(local)
    return json.loads(local)


def initDB():
    """
    Initialize database, creates it if not present

    :return: True or False if successful
    """

    # Obtain configuration file names
    try:
        dbFilename = proxyConfig.get("DATABASE", "FILENAME")
        dbSchema = proxyConfig.get("DATABASE", "SCHEMANAME")

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
                conn = sqlite3.connect(dbFilename)
                cur = conn.cursor()
                schema = f.read()
                cur.executescript(schema)
            conn.close()

        except sqlite3.Error as e:
            logger.error("Sqlite3.Error: " + str(e))
            return False

    return True


def openTestDB():
    """
    Opens a test database, returns a connection object or None

    :return: connection object or None if unsuccessful
    """

    # Obtain configuration file names
    try:
        testDbFilename = proxyConfig.get("TESTDATABASE", "FILENAME")

    except ConfigParser.Error as e:
        logger.error("ConfigParse.Error: " + str(e))
        return None

    if not os.path.isfile(testDbFilename):
        logger.error('Test database: {} not found. '.format(testDbFilename))
        return None

    conn = None
    try:
        conn = sqlite3.connect(testDbFilename)

    except sqlite3.Error as e:
        logger.error("Sqlite3.Error: " + str(e))
        return None

    return conn


def sqlBeginRead(conn):
    """
    Starts a read by executing SQL and returning a cursor

    :param conn: Database connection
    :return: cursor or None if we encountered a problem
    """

    sql = "SELECT KEYID, PORT, BASE64, EPOCH FROM PROXY"
    cursor = None

    try:
        # Use connection as context manager to rollback automatically if error
        with conn:
            cursor = conn.cursor()
            cursor.execute(sql)

    except sqlite3.Error as e:
        logger.error("Sqlite3.Error: " + str(e))
        conn.close()
        return None

    return cursor


def sqlInsert(data):
    """
    Takes in a data tuple and inserts it into the Proxy SQLite table

    :param data: Proxy dictionary
    :return: Status True or False on SQL insertion success
    """

    # Read in name of database
    try:
        db = proxyConfig.get("DATABASE", "FILENAME")

    except ConfigParser.Error as e:
        logger.error("ConfigParse.Error: " + str(e))
        return False

    # # Change dictionary into list with proper order
    sqlparameters = [None, data["port"], data["data"], time.time()]

    if len(sqlparameters) > 0:
        # Create parameter substitute "?" string for SQL query then create SQL
        numKeys = len(sqlparameters)
        paramSubs = "?" * (numKeys)
        paramSubs = ",".join(paramSubs)
        sql = "INSERT INTO PROXY VALUES(" + paramSubs + ")"

        # Connect to database, create SQL query, execute query, and close database
        try:
            conn = sqlite3.connect(db)

        except sqlite3.Error as e:
            logger.error("Sqlite3.Error: " + str(e))
            return False

        try:
            # Use connection as context manager to rollback automatically if error
            with conn:
                conn.execute(sql, sqlparameters)

        except sqlite3.Error as e:
            logger.error("Sqlite3.Error: " + str(e))
            conn.close()
            return False

        # Completed, close database and return True
        conn.close()
        return True

    else:
        return False


def main():
    try:
        log = proxyConfig.getboolean('PROXY', 'LOG')
        testmode = proxyConfig.getboolean('PROXY', 'TESTMODE')
    except ConfigParser.Error as e:
        logger.error("ConfigParse.Error: " + str(e))
        sys.exit(0)

    """Main function which starts UART Worker thread + Flask server."""
    logger.info('Starting proxy server')

    initDB()  # Initialize database for logging

    # Associate serial ports with callsigns
    # global units
    units = callsign2COM()

    if testmode == 0:
        for key, values in units.iteritems():
            unitDict[str(values["callsign"] + "-" + values["nodeid"])] = layer_4_service.faraday_uart_object(str(values["com"]), int(values["baudrate"]), int(values["timeout"]))

        for key in unitDict:
            logger.info('Starting Thread For Unit: ' + str(key))
            tempdict = {"unit": key, 'com': unitDict[key]}
            t = threading.Thread(target=uart_worker, args=(tempdict, getDicts, units, log))
            t.start()
    else:
        t = threading.Thread(target=testdb_read_worker)
        t.start()

    try:
        # Start the flask server on localhost:8000
        proxyHost = proxyConfig.get("FLASK", "host")
        proxyPort = proxyConfig.getint("FLASK", "port")
    except ConfigParser.Error as e:
        logger.error("ConfigParse.Error: " + str(e))
        sys.exit(0)

    app.run(host=proxyHost, port=proxyPort, threaded=True)


if __name__ == '__main__':
    main()

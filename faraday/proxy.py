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
import argparse
import shutil
import socket
import struct
import array

from flask import Flask
from flask import request

from faraday.uart import layer_4_service

# Start logging after importing modules

relpath1 = os.path.join('etc', 'faraday')
relpath2 = os.path.join('..', 'etc', 'faraday')
setuppath = os.path.join(sys.prefix, 'etc', 'faraday')
userpath = os.path.join(os.path.expanduser('~'), '.faraday')
path = ''

for location in os.curdir, relpath1, relpath2, setuppath, userpath:
    try:
        logging.config.fileConfig(os.path.join(location, "loggingConfig.ini"))
        path = location
        break
    except ConfigParser.NoSectionError:
        pass

logger = logging.getLogger('Proxy')

# Set werkzeug logging level

werkzeuglog = logging.getLogger('werkzeug')
werkzeuglog.setLevel(logging.ERROR)

#Create Proxy configuration file path
proxyConfigPath = os.path.join(path, "proxy.ini")
logger.debug('Proxy.ini PATH: ' + proxyConfigPath)

# Command line input
parser = argparse.ArgumentParser(description='Proxy application interfaces a Faraday radio over USB UART')
parser.add_argument('--init-config', dest='init', action='store_true', help='Initialize Proxy configuration file')
parser.add_argument('--start', action='store_true', help='Start Proxy server')
parser.add_argument('--callsign', help='Set Faraday callsign')
parser.add_argument('--nodeid', type=int, help='Set Faraday node ID')
parser.add_argument('--port', help='Set Faraday UART port')
parser.add_argument('--baudrate', default='115200', help='Set Faraday UART baudrate')
parser.add_argument('--timeout', type=int, default=5, help='Set Faraday UART timeout')
parser.add_argument('--unit', type=int, default=0, help='Specify Faraday unit to configure')

#Proxy options
parser.add_argument('--number', type=int, default=0, help='Set number of Faraday radios to use')
parser.add_argument('--log', action='store_true', help='Set Proxy into logging mode')
parser.add_argument('--test-mode', dest='testmode', action='store_true', help='Set Proxy into test mode')
parser.add_argument('--test-callsign', dest='testcallsign', help='Set Faraday test mode callsign')
parser.add_argument('--test-nodeid', dest='testnodeid', type=int, help='Set Faraday test mode nodeid')
parser.add_argument('--test-rate', dest='testrate', default=1, type=int, help='Set Faraday test mode rate')

# Proxy database options
parser.add_argument('--database', help='Set Faraday Proxy database')
parser.add_argument('--schema', help='Set Faraday database schema')
parser.add_argument('--test-database', dest='testdatabase', help='Set Faraday test mode database')
parser.add_argument('--init-log', dest='initlog', action='store_true', help='Initialize Proxy log database')
parser.add_argument('--save-log', dest='savelog', help='Save Proxy log database into new SAVELOG file')
parser.add_argument('--show-logs', dest='showlogs', action='store_true', help='Show Proxy log database files')

# Proxy Flask options
parser.add_argument('--flask-host', dest='flaskhost', help='Set Faraday Flask server host address')
parser.add_argument('--flask-port', type=int, dest='flaskport', help='Set Faraday Flask server port')

# Parse the arguments
args = parser.parse_args()


def initializeProxyConfig():
    '''
    Initialize proxy configuration file from proxy.sample.ini

    :return: None, exits program
    '''

    logger.debug("Initializing Proxy")
    shutil.copy(os.path.join(path, "proxy.sample.ini"), os.path.join(path, "proxy.ini"))
    logger.debug("Initialization complete")
    sys.exit(0)


def initializeProxyLog(config):
    '''
    Initialize the log database by deleting file

    :param config: Proxy ConfigParser object from proxy.ini
    :return: None
    '''

    logger.info("Initializing Proxy Log File")
    log = config.get("DATABASE", "filename")
    logpath = os.path.join(os.path.expanduser('~'), '.faraday', 'lib', log)
    os.remove(logpath)
    logger.info("Log initialization complete")


def saveProxyLog(name, config):
    '''
    Save proxy log database into a new file

    :param name: Name of file to save data into (should be .db)
    :param config: Proxy ConfigParser object from proxy.ini
    :return: None
    '''

    log = config.get("DATABASE", "filename")
    oldpath = os.path.join(os.path.expanduser('~'), '.faraday', 'lib', log)
    newpath = os.path.join(os.path.expanduser('~'), '.faraday', 'lib', name)
    shutil.move(oldpath, newpath)
    sys.exit(0)


def showProxyLogs():
    '''
    Show proxy log database filenames in user path ~/.faraday/lib folder

    :return: None, exits program
    '''

    logger.info("The following logs exist for Proxy...")
    path = os.path.join(os.path.expanduser('~'), '.faraday', 'lib')
    for file in os.listdir(path):
        if file.endswith(".db"):
            logger.info(file)
    sys.exit(0)


def configureProxy(args, proxyConfigPath):
    '''
    Configure proxy configuration file from command line

    :param args: argparse arguments
    :param proxyConfigPath: Path to proxy.ini file
    :return: None
    '''

    config = ConfigParser.RawConfigParser()
    config.read(os.path.join(path, "proxy.ini"))

    # Configure UNITx sections
    unit = 'UNIT' + str(args.unit)
    if args.unit is not 0:
        try:
            config.add_section(unit)

        except ConfigParser.DuplicateSectionError:
            pass

    if args.callsign is not None:
        config.set(unit, 'CALLSIGN', args.callsign)
    if args.nodeid is not None:
        config.set(unit, 'NODEID', args.nodeid)
    if args.port is not None:
        config.set(unit, 'COM', args.port)
    if args.baudrate:
        config.set(unit, 'BAUDRATE', args.baudrate)
    if args.timeout:
        config.set(unit, 'TIMEOUT', args.timeout)

    # Configure Proxy section items
    if args.number is not 0:
        config.set('PROXY', 'units', args.number)
    if args.log:
        config.set('PROXY', 'log', 1)
    else:
        config.set('PROXY', 'log', 0)
    if args.testmode:
        config.set('PROXY', 'testmode', 1)
    else:
        config.set('PROXY', 'testmode', 0)
    if args.testcallsign is not None:
        config.set('PROXY', 'testcallsign', args.testcallsign)
    if args.testnodeid is not None:
        config.set('PROXY', 'testnodeid', args.testnodeid)
    if args.testrate:
        config.set('PROXY', 'testrate', args.testrate)

    #Configure Proxy databases
    if args.database is not None:
        config.set('DATABASE', 'filename', args.database)
    if args.schema is not None:
        config.set('DATABASE', 'schemaname', args.schema)
    if args.testdatabase is not None:
        config.set('TESTDATABASE', 'filename', args.testdatabase)

    # Configure Proxy flask server
    if args.flaskhost is not None:
        config.set('FLASK', 'host', args.flaskhost)
    if args.flaskport is not None:
        config.set('FLASK', 'port', args.flaskport)

    with open(proxyConfigPath, 'wb') as configfile:
        config.write(configfile)


# Initialize and configure proxy
if args.init:
    initializeProxyConfig()

# Attempt to configure proxy
try:
    configureProxy(args, proxyConfigPath)

except ConfigParser.NoSectionError as e:
    # Possible that no configuration file found
    logger.error('Proxy configuration file error!')
    logger.error('Did you remember to --init-config?')
    logger.error(e)
    sys.exit(1)

# Load Proxy Configuration from proxy.ini file
proxyConfig = ConfigParser.RawConfigParser()
proxyConfig.read(proxyConfigPath)

# Initialize Proxy log database
if args.initlog:
    initializeProxyLog(proxyConfig)

# Save Proxy log database
if args.savelog is not None:
    saveProxyLog(args.savelog, proxyConfig)

# List Proxy log database files
if args.showlogs:
    showProxyLogs()

# Check for --start option and exit if not present
if not args.start:
    logger.warning("--start option not present, exiting Proxy server!")
    sys.exit(0)

# Create and initialize dictionary queues
#postDict = {}
postDicts = {}
getDicts = {}
unitDict = {}
dataBuffer = {}

def startServer(modem, dataPort):
    # Start socket
    s = socket.socket()
    host = socket.gethostname()
    port = dataPort
    result = 0

    # Check port status
    while result == 0:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = 1
            result = sock.connect_ex((host,port))
        except socket.error as e:
            logger.warning(e)


        #logger.info(port)

    logger.info("Started server on {0}:{1}".format(host,port))


    s.bind((host,port))

    return s

def uart_worker(modem, getDicts, units, log):
    """
    Interface Faraday ports over USB UART

    This function interfaces the USB UART serial data with an infinite loop
    that checks all Faraday "ports" for data and appends/pops data from
    queues for send and receive directions.
    """
    logger.debug('Starting uart_worker thread')

    # Iterate through dictionary of each unit in the dictionary creating a
    # deque for each item
    postDicts[modem['unit']] = {}
    getDicts[modem['unit']] = {}

    # Loop through each unit checking for data, if True place into deque
    while True:
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
                    try:
                        message = postDicts[modem['unit']][port].popleft()
                        message = base64.b64decode(message)
                        modem['com'].POST(port, len(message), message)
                    except StandardError as e:
                        logger.error(e)


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
    logger.debug('Starting testdb_read_worker thread')

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

def acceptConnection(server):
    conn, addr = server.accept()
    logger.info("Got connection from  {0}".format(addr))
    return conn, addr

def closeConnection(conn, addr):
    # close the connection
    logger.info("Closing connection with {0}".format(addr))
    conn.close()

def extractBytes(data, dataBuffer, unit):
    # data is a BASE64 string with unknown length, iterate and separete
    data = data.decode('base64', 'strict')

    for byte in data:
        try:
            byte = struct.unpack("c",byte)[0]
            dataBuffer[unit].append(byte)

        except:
            dataBuffer[unit] = deque([])
            dataBuffer[unit].append(byte)

def receiveData(conn, addr, dataBuffer, unit):
    while True:
        try:
            data = conn.recv(4096)
        except socket.error as e:
            logger.error(e)
            closeConnection(conn, addr)

        if not data:
            closeConnection(conn,addr)
            break

        # Expect BASE64 so decode it
        extractBytes(data, dataBuffer, unit)

def sendData(conn, addr, getDicts, unit):
    while True:
        # not sure why I need a delay... otherwise socket closes
        time.sleep(0.05)

        if len(getDicts) <= 0:
            conn.sendall("No Data!")
            closeConnection(conn, addr)
            break


        try:
            # pop off a data entry from the left of getDicts
            temp = getDicts[unit][1].popleft()
        except collections.error as e:
            logger.error(e)

        try:
            conn.sendall(temp['data'])
        except socket.error as e:
            logger.warning(e)
            closeConnection(conn, addr)
            break


def socket_worker(modem, units, log, dataPort):
    """
    Create sockets for data connections

    """
    logger.info('Starting socket_worker thread')
    unit = modem['unit']
    dataBuffer[unit] = {}

    # Start a socket server for the modem
    server = startServer(unit, dataPort)

    # Listen to server in infinit loop
    server.listen(5)
    while True:
        conn, addr = acceptConnection(server)

        # connection is open, receive data until connection closes
        receiveData(conn, addr, dataBuffer, unit)

def socket_worker_RX(modem, getDicts, dataPort):
    """
    Create sockets for data connections

    """
    logger.info('Starting socket_worker thread')
    unit = modem['unit']
    dataBuffer[unit] = {}

    # Start a socket server for the modem
    server = startServer(unit, dataPort)

    # Listen to server in infinit loop
    server.listen(5)
    while True:
        conn, addr = acceptConnection(server)

        sendData(conn, addr, getDicts, unit)




def bufferWorker(modem, postDicts):
    logger.info("Starting bufferWorker Thread")

    while True:
        # Initialize temp list
        temp = []
        #logger.info("unit : {0}".format(len(dataBuffer[modem['unit']])))

        try:
            if len(dataBuffer[modem['unit']]) > 0:
                temp = []

                # Pop off 121 bytes and append to temporary list
                for i in range(121):
                    try:
                        a = dataBuffer[modem['unit']].popleft()
                        temp.append(a)
                    except StandardError as e:
                        pass

                # Join list together and append two control bytes, convert to BASE64
                try:

                    temp = ''.join(temp)
                    b = struct.pack("BB", 0,0)
                    temp = b + temp
                    temp = temp.encode('base64','strict')

                except struct.error as e:
                    logger.error(e)
                    break

                except StandardError as e:
                    logger.info("StandardError")
                    logger.error(e)
                    break

                # Append formatted packet to postDicts for corrent unit/port to send
                try:
                    # Hardcoded for port 1
                    postDicts[modem['unit']][1].append(temp)
                except:
                    postDicts[modem['unit']][1] = deque([], maxlen=100)
                    postDicts[modem['unit']][1].append(temp)
        except StandardError as e:
            pass
            # logger.info(e)


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

        except KeyError:
            logger.error("Error: No 'data' key in dictionary")
            return json.dumps(
                {"error": "Error: No 'data' key in dictionary"}), 400
        else:
            total = len(data["data"])
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
                logger.debug("Empty buffer for port {0}".format(port))
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
    # make directory tree, necessary?
    try:
        os.makedirs(os.path.join(os.path.expanduser('~'), '.faraday.', 'lib'))
    except:
        pass

    # Obtain configuration file names, always place at sys.prefix
    try:
        dbFilename = proxyConfig.get("DATABASE", "FILENAME")
        dbPath = os.path.join(os.path.expanduser('~'), '.faraday.', 'lib', dbFilename)
        logger.debug("Proxy Database: " + dbPath)
        dbFilename = dbPath

        dbSchema = proxyConfig.get("DATABASE", "SCHEMANAME")
        dbSchema = os.path.join(path, dbSchema)

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
        dbPath = os.path.join(os.path.expanduser('~'), '.faraday.', 'lib', testDbFilename)
        logger.debug("Proxy Test Database: " + dbPath)
        testDbFilename = dbPath

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
        dbFilename = proxyConfig.get("DATABASE", "FILENAME")
        dbPath = os.path.join(os.path.expanduser('~'), '.faraday.', 'lib', dbFilename)
        logger.debug("Proxy Database: " + dbPath)
        dbFilename = os.path.join(dbPath)

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
            conn = sqlite3.connect(dbFilename)

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
        sys.exit(1)  # Sys.exit(1) is an error

    """Main function which starts UART Worker thread + Flask server."""
    logger.info('Starting proxy server')

    initDB()  # Initialize database for logging

    # Associate serial ports with callsigns
    # global units
    try:
        units = callsign2COM()
    except ConfigParser.NoSectionError as e:
        logging.error(e)
        sys.exit(1)  # Sys.exit(1) is an error

    if testmode == 0:
        for key, values in units.iteritems():
            try:
                node = str(values["callsign"] + "-" + values["nodeid"])
                unitDict[node] = layer_4_service.faraday_uart_object(str(values["com"]), int(values["baudrate"]), int(values["timeout"]))
            except:
                logger.error('Could not connect to {0} on {1}'.format(node, values["com"]))

        dataPort = 10000
        for key in unitDict:
            logger.info(key)
            logger.info('Starting Thread For Unit: {0}'.format(str(key)))
            tempdict = {"unit": key, 'com': unitDict[key]}
            t = threading.Thread(target=uart_worker, args=(tempdict, getDicts, units, log))
            t.start()

            logger.info("starting socket_worker")
            u = threading.Thread(target=socket_worker, args=(tempdict, units, log, dataPort))
            u.start()

            logger.info("starting socket_worker")
            w = threading.Thread(target=socket_worker_RX, args=(tempdict, getDicts, dataPort+10))
            w.start()

            logger.info("starting bufferWorker")
            try:

                v = threading.Thread(target=bufferWorker, args=(tempdict, postDicts))

                v.start()
                logger.error("test")
            except:
                logger.error("crap")

            dataPort += 1
    else:
        t = threading.Thread(target=testdb_read_worker)
        t.start()

    try:
        # Start the flask server on localhost:8000
        proxyHost = proxyConfig.get("FLASK", "host")
        proxyPort = proxyConfig.getint("FLASK", "port")
    except ConfigParser.Error as e:
        logger.error("ConfigParse.Error: " + str(e))
        sys.exit(1)  # Sys.exit(1) is an error



    #app.run(host=proxyHost, port=proxyPort, threaded=True)


if __name__ == '__main__':
    main()

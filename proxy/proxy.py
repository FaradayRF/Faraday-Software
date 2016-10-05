# /proxy/proxy.py
# License: GPLv3 with Network Interface Clause

"""
Proxy is meant to communicate with a Faraday Radio over USB UART via a serial
port. It has a thread which continuously checks for data over USB and places it
into a thread safe dequeue. The Flask server returns requested data from this
queue with a GET request or adds to it with a POST request via an IP address
and port specified in the configuration file proxy.ini.
"""

import time
import base64
import json
import logging
import logging.config
import threading
import ConfigParser
from collections import deque

from flask import Flask
from flask import request

from faraday_uart_stack import layer_4_service

# Start logging after importing modules
logging.config.fileConfig('loggingConfig.ini')
logger = logging.getLogger('Proxy')

# Load Proxy Configuration from proxy.ini file
proxyConfig = ConfigParser.RawConfigParser()
proxyConfig.read('proxy.ini')

# Create and initialize dictionary queues
queDict = {}
portDict = {}
postDict = {}


def uart_worker(modem, que):
    """
    Interface Faraday ports over USB UART

    This function interfaces the USB UART serial data with an infinit loop
    that checks all Faraday "ports" for data and appends/pops data from
    queues for send and receive directions.
    """
    logger.info('Starting uart_worker thread')
    while(1):
        # Place data into the FIFO coming from UART
        try:
            for port in range(0, 255):
                if(modem.RxPortHasItem(port)):
                    # Data is available, convert to BASE64 and place in queue
                    item = {}
                    item["port"] = port
                    item["data"] = base64.b64encode(modem.GET(port))
                    try:
                        que[port].append(item)
                    except:
                        # Port qeue does not exist, create one
                        que[port] = deque([], maxlen=100)
                        que[port].append(item)

        except StandardError as e:
            logger.error("StandardError: " + str(e))

        except ValueError as e:
            logger.error("ValueError: " + str(e))

        except IndexError as e:
            logger.error("IndexError: " + str(e))

        except KeyError as e:
            logger.error("KeyError: " + str(e))

        time.sleep(0.01)
        # Check for data in the POST FIFO queue
        try:
            for port in range(0, 255):
                try:
                    postDict[port]
                except:
                    pass
                else:
                    for num in range(len(postDict[port])):
                        # Data is available, convert to BASE64, place in queue
                        message = postDict[port].popleft()
                        message = base64.b64decode(message)
                        modem.POST(port, len(message), message)
        except:
            # Need to implement some error catching functionality here
            pass
        # Slow down while loop to something reasonable
        time.sleep(0.01)

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
            callsign = str(request.args.get("callsign", "NONE"))
            nodeid = int(request.args.get("nodeid", 0))
            port = int(request.args.get("port"))
            data = request.get_json(force=False)

        except StandardError as e:
            logger.warn("StandardError: " +  str(e))
            return e, 400

        except ValueError as e:
            logger.warn("ValueError: " +  str(e))
            return e, 400

        except TypeError as e:
            logger.warn("ValueError: " +  str(e))
            return e, 400

        # Find COM Port
        for station in units:
            if units[station][0] == callsign and int(units[station][1]) == nodeid:
                com = units[station][2] #do something with this!!!

        # Does not actually use multi-node COM port!
        for item in data['data']:
            try:
                postDict[port].append(str(item))
            except:
                postDict[port] = deque([], maxlen=100)
                postDict[port].append(str(item))

        try:
            if(len(data)>0):
                return ' ', 200

            else:
                return ' ', 204

        except KeyError as e:
            # Service port has never been used and has no data in it
            logger.warn("KeyError: " +  str(e))
            return ' ', 204

        except StandardError as e:
            logger.warn("StandardError: " +  str(e))

        return "POST", 200
    else:
        port = request.args.get("port")
        limit = request.args.get("limit")
        logger.debug("GET Request: port=%s limit=%s", port, limit)

        if port is None:
            return 'Port value required for GET request', 400
        else:
            port = int(port)
        logger.debug(limit)
        if limit is None:
            try:
                limit = len(queDict[port])

            except StandardError as e:
                logger.error("GET StandardError: " + str(e))
                return ' ', 500
            except ValueError as e:
                logger.error("GET ValueError: " + str(e))
                return ' ', 500
            except IndexError as e:
                logger.error("GET IndexError: " + str(e))
                return ' ', 500
            except KeyError as e:
                logger.error("GET KeyError: " + str(e))
                return ' ', 400
        else:
            limit = int(limit)

        try:
            # Check if there is a queue for the specified service port
            if (len(queDict[port]) > 0):
                queryTime = time.asctime(time.localtime(time.time()))
                data = []
                try:
                    # NEVER CHECKS FOR LIMIT, FIX!
                    while queDict[port]:
                        data.append(queDict[port].popleft())
                        if limit == 1:
                            break
                    logger.info("GET returned %s items from queue", len(data))
                    return json.dumps(data, indent=4),\
                        200,\
                        {'Content-Type': 'application/json'}

                except StandardError as e:
                    logger.error("GET StandardError: " + str(e))
                    return ' ', 500
                except ValueError as e:
                    logger.error("GET ValueError: " + str(e))
                    return ' ', 500
                except IndexError as e:
                    logger.error("GET IndexError: " + str(e))
                    return ' ', 500
                except KeyError as e:
                    logger.error("GET KeyError: " + str(e))
                    return ' ', 400

            else:
                # No data in service port, but port is being used
                return ' ', 204

        except KeyError as e:
            # Service port has never been used and has no data in it
            print "KeyError: ", e
            return ' ', 204

        except StandardError as e:
            print e


@app.errorhandler(404)
def pageNotFound(error):
    """HTTP 404 response for incorrect URL"""
    return "HTTP 404: Not found", 404

def callsign2COM():
    """ Associate configuration callsigns with serial COM ports"""
    local = {}
    num = int(proxyConfig.get('proxy', 'units'))
    units = range(0, num)

    for unit in units:
        item = "UNIT" + str(unit)
        callsign = proxyConfig.get(item, "callsign")
        nodeid = proxyConfig.get(item, "nodeid")
        com = proxyConfig.get(item, "com")
        local[str(item)] = [callsign, nodeid, com]

    local = json.dumps(local)
    return json.loads(local)

def main():
    """Main function which starts UART Worker thread + Flask server."""
    logger.info('Starting proxy server')

    # Load serial port configuration
    proxyCOM = proxyConfig.get("serial", "com")
    proxyBaud = proxyConfig.getint("serial", "baudrate")
    proxyTimeout = proxyConfig.getint("serial", "timeout")

    # Associate serial ports with callsigns
    global units
    units = callsign2COM()
    logger.info(str(units))

    # Initialize local variables
    threads = []

    while(1):
        # Initialize a Faraday Radio device
        try:
            faradayUART1 = \
                layer_4_service.faraday_uart_object(proxyCOM,
                                                    proxyBaud,
                                                    proxyTimeout)
            logger.info("Connected to Faraday")
            break
            time.sleep(1)
        except:
            logger.error("%s not detected", proxyCOM)
            time.sleep(1)

    t = threading.Thread(target=uart_worker, args=(faradayUART1, queDict))
    threads.append(t)
    t.start()

    # Start the flask server on localhost:8000
    proxyHost = proxyConfig.get("flask", "host")
    proxyPort = proxyConfig.getint("flask", "port")

    app.run(host=proxyHost, port=proxyPort)

if __name__ == '__main__':
    main()

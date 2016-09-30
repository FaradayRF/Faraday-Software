#-------------------------------------------------------------------------------
# Name:        /proxy/proxy.py
# Purpose:     Communicate with Faraday Radio over USB UART and facilitate
#              bidirectional data transfer with a RESTful API to a network
#              interface.
#
# Author:      Bryce Salmi
#
# Created:     22/09/2016
# Licence:     GPLv3
#-------------------------------------------------------------------------------

"""
Proxy is meant to communicate with a Faraday Radio over USB UART via a serial
port. It has a thread which continuously checks for data over USB and places it
into a thread safe dequeue. The Flask server returns requested data from this
queue with a GET request or adds to it with a POST request via an IP address and
port specified in the configuration file proxy.ini.
"""

from flask import Flask
from flask import request
import logging
import logging.config
import time
import threading
from collections import deque
import base64
import json
import ConfigParser

# Faraday specific modules
from faraday_uart_stack import layer_4_service

# Start logging before even initializing flask
logging.config.fileConfig('loggingConfig.ini')
logger = logging.getLogger('Proxy')

# Load Proxy Configuration
proxyConfig = ConfigParser.RawConfigParser()
proxyConfig.read('proxy.ini')

#make one global dictionaries
queDict = {}
queDict2 = []
portDict = {}
postDict = {}

def uart_worker(modem,que):
    """ Check Faraday ports available for data, append to dictionary if found."""
    logger.info('Starting uart_worker thread')

    #start an infinit loop
    while(1):
        # Place data into the FIFO coming from UART for GET function
        try:
            for port in range(0,255):
                if(modem.RxPortHasItem(port)):
                    #data is waiting from UART, encode BASE64 and place in qeue
                    item = {}
                    item["port"] = port
                    item["data"] = \
                    base64.b64encode(modem.GET(port))
                    try:
                        que[port].append(item)
                    except:
                        # Qeue does not exist for port, create one
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
        # Check for data in the POST FIFO to send to UART
        try:
            for port in range(0,255):
                try:
                    postDict[port]
                except:
                    pass
                else:
                    for num in range(len(postDict[port])):
                        #Data is present in qeue, decode BASE64, send to UART
                        message = postDict[port].popleft()
                        message = base64.b64decode(message)
                        modem.POST(port, len(message), message)
        except:
            pass
        time.sleep(0.01)

# Initialize Flask microframework
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def proxy():
    """ Provides a RESTful interface to the USB UART on URL '/'."""
    if request.method == "POST":
        logger.debug("POST")
        return "POST", 200
    else:
        port = request.args.get("port")
        limit = request.args.get("limit")
        logger.debug("GET Request: port=%s limit=%s", port, limit)

        if port == None:
            logger.warn("Port value required for GET request")
            return '', 400
        else:
            port = int(port)
        logger.debug(limit)
        if limit == None:
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
                queryTime = time.asctime(time.localtime(time.time())) #I SHOULD ADD TIMESTAMP TO DATA SENT
                data = []
                try:
                    # NEVER CHECKS FOR LIMIT, FIX!
                    while queDict[port]:
                        data.append(queDict[port].popleft())
                        if (limit == 1):
                            break;
                    logger.info("GET returned %s items from queue", len(data))
                    return json.dumps(data, indent = 4), 200, {'Content-\
                    Type': 'application/json'}

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
    """ Returns a string indicating the page was not found and an HTTP 404 response."""
    return "HTTP 404: Page not found", 404

def main():
    """ Main function which reads configuration files and starts threads + Flask."""
    logger.info('Starting proxy server')

    # Load serial port configuration
    proxyCOM = proxyConfig.get("serial", "com")
    proxyBaud = proxyConfig.getint("serial", "baudrate")
    proxyTimeout = proxyConfig.getint("serial", "timeout")

    # Initialize local variables
    threads = []

    while(1):
        # Initialize a Faraday Radio device
        try:
            faradayUART1 = layer_4_service.faraday_uart_object(proxyCOM,proxyBaud,proxyTimeout)
            logger.info("Connected to Faraday")
            break
            time.sleep(1)
        except:
            logger.error("%s not detected",proxyCOM) #make dynamic
            time.sleep(1)

    t = threading.Thread(target=uart_worker, args=(faradayUART1,queDict))
    threads.append(t)
    t.start()

    # Start the flask server on localhost:8000
    proxyHost = proxyConfig.get("flask","host")
    proxyPort = proxyConfig.getint("flask","port")

    app.run(host=proxyHost, port=proxyPort)

if __name__ == '__main__':
    main()

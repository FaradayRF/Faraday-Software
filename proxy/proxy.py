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

from flask import Flask
from flask import request
import logging
import logging.config
import time
import threading
from collections import deque
import base64
import json

# Faraday specific modules
from faraday_uart_stack import layer_4_service

# Start logging before even initializing flask
logging.config.fileConfig('loggingConfig.ini')
logger = logging.getLogger('Proxy')

#make one global dictionaries
queDict = {}
queDict2 = []
portDict = {}
postDict = {}

#Create threaded worker definition for RX
def uart_worker(modem,que):
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
    return "HTTP 404: Page not found", 404

def main():
    logger.info('Starting proxy server')

    # Initialize local variables
    threads = []

    while(1):
        # Initialize a Faraday Radio device
        try:
            faradayUART1 = layer_4_service.faraday_uart_object('COM7',115200,5)
            logger.info("Connected to Faraday")
            break
            time.sleep(1)
        except:
            logger.warn("COM port not detected") #make dynamic

    t = threading.Thread(target=uart_worker, args=(faradayUART1,queDict))
    threads.append(t)
    t.start()

    # Start the flask server on localhost:8000
    app.run(host='127.0.0.1', port=8000)

if __name__ == '__main__':
    main()

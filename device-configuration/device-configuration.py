
import time
import logging
import logging.config
import threading
import ConfigParser
from collections import deque
import os
import sys
import json

from flask import Flask
from flask import request

# Can we clean this up?
sys.path.append(os.path.join(os.path.dirname(__file__), "../Faraday_Proxy_Tools/")) #Append path to common tutorial FaradayIO module
from FaradayIO import faradaybasicproxyio
from FaradayIO import telemetryparser

# Start logging after importing modules
logging.config.fileConfig('loggingConfig.ini')
logger = logging.getLogger('deviceconfiguration')

# Load Telemetry Configuration from telemetry.ini file
# Should have common file for apps...
deviceConfig = ConfigParser.RawConfigParser()
deviceConfig.read('deviceconfiguration.ini')

# Initialize proxy object
proxy = faradaybasicproxyio.proxyio()

# Initialize Flask microframework
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def getconfig():
    """
    Provides a RESTful interface to device-configuration at URL '/'
    """

    try:
        # Obtain URL parameters
        callsign = request.args.get("callsign", "%")
        nodeid = request.args.get("nodeid", "%")

        callsign = str(callsign).upper()
        nodeid = str(nodeid)

    except ValueError as e:
        logger.error("ValueError: " + str(e))
        return json.dumps({"error": str(e)}), 400
    except IndexError as e:
        logger.error("IndexError: " + str(e))
        return json.dumps({"error": str(e)}), 400
    except KeyError as e:
        logger.error("KeyError: " + str(e))
        return json.dumps({"error": str(e)}), 400


    #data = callsign, nodeid

    data = proxy.GET(str(callsign), str(nodeid), 5)

    print "DATA:", data


    # Check if data returned, if not, return HTTP 204
    if len(data) <= 0:
        logger.info("No station data in last %d seconds", timespan)
        return '', 204  # HTTP 204 response cannot have message data

    return json.dumps(data, indent=1), 200,\
            {'Content-Type': 'application/json'}


def main():
    """Main function which starts telemery worker thread + Flask server."""
    logger.info('Starting device configuration server')


    # Start the flask server on localhost:8001
    telemetryHost = deviceConfig.get("flask", "host")
    telemetryPort = deviceConfig.getint("flask", "port")

    app.run(host=telemetryHost, port=telemetryPort, threaded=True)

if __name__ == '__main__':
    main()
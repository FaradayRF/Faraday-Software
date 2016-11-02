
import time
import logging
import logging.config
import threading
import ConfigParser
from collections import deque
import os
import sys
import json
import ConfigParser

from flask import Flask
from flask import request

# Can we clean this up?
sys.path.append(os.path.join(os.path.dirname(__file__), "../Faraday_Proxy_Tools/")) #Append path to common tutorial FaradayIO module
from FaradayIO import faradaybasicproxyio
from FaradayIO import telemetryparser
from FaradayIO import faradaycommands

# Start logging after importing modules
logging.config.fileConfig('loggingConfig.ini')
logger = logging.getLogger('deviceconfiguration')

# Load Telemetry Configuration from telemetry.ini file
# Should have common file for apps...
deviceConfig = ConfigParser.RawConfigParser()
deviceConfig.read('deviceconfiguration.ini')

# Initialize proxy object
proxy = faradaybasicproxyio.proxyio()

#Initialize faraday command module
faradayCmd = faradaycommands.faraday_commands()

# Initialize Flask microframework
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def getconfig():
    if request.method == "POST":
        # Obtain URL parameters
        callsign = request.args.get("callsign", "%")
        nodeid = request.args.get("nodeid", "%")

        callsign = str(callsign).upper()
        nodeid = str(nodeid)

        telemetryConfig = ConfigParser.RawConfigParser()
        telemetryConfig.read('faraday_config.ini')

        callsign_ini = str(telemetryConfig.get("identification", "callsign")).upper()

        print callsign_ini

        command_send = faradayCmd.CommandLocal(9, callsign_ini)

        proxy.POST(callsign, nodeid, 2, command_send)
        print "Testing POST"
        return '', 204
    else: #If a GET command
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

        # data = callsign, nodeid

        data = proxy.GET(str(callsign), str(nodeid), proxy.CMD_UART_PORT)

        print "DATA:", data

        # Check if data returned, if not, return HTTP 204
        if len(data) <= 0:
            logger.info("No station data in last %d seconds", timespan)
            return '', 204  # HTTP 204 response cannot have message data

        return json.dumps(data, indent=1), 200, \
               {'Content-Type': 'application/json'}


@app.route('/printconfig', methods=['GET'])
def printconfig():
    if request.method == "POST":
        # Read configuration file
        device_config_dict = dict(telemetryConfig.items("Config"))
        device_identification_dict = dict(telemetryConfig.items("Identification"))
        device_basic_dict = dict(telemetryConfig.items("Basic"))
        device_rf_dict = dict(telemetryConfig.items("RF"))
        device_gps_dict = dict(telemetryConfig.items("GPS"))
        device_telemetry_dict = dict(telemetryConfig.items("Telemetry"))

        print device_config_dict
        print device_identification_dict
        print device_basic_dict
        print device_rf_dict
        print device_gps_dict
        print device_telemetry_dict

        #proxy.POST(callsign, nodeid, 2, command_send)
        print "Testing POST"
        return '', 204
    else: #If a GET command
        """

        """
        try:
            pass



        except ValueError as e:
            logger.error("ValueError: " + str(e))
            return json.dumps({"error": str(e)}), 400
        except IndexError as e:
            logger.error("IndexError: " + str(e))
            return json.dumps({"error": str(e)}), 400
        except KeyError as e:
            logger.error("KeyError: " + str(e))
            return json.dumps({"error": str(e)}), 400

        #Return
        return '', 204  # HTTP 204 response cannot have message data


def main():
    """Main function which starts telemery worker thread + Flask server."""
    logger.info('Starting device configuration server')


    # Start the flask server on localhost:8001
    telemetryHost = deviceConfig.get("flask", "host")
    telemetryPort = deviceConfig.getint("flask", "port")

    app.run(host=telemetryHost, port=telemetryPort, threaded=True)

if __name__ == '__main__':
    main()

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
import struct

from flask import Flask
from flask import request

# Can we clean this up?
sys.path.append(os.path.join(os.path.dirname(__file__), "../Faraday_Proxy_Tools/")) #Append path to common tutorial FaradayIO module
from FaradayIO import faradaybasicproxyio
from FaradayIO import telemetryparser
from FaradayIO import faradaycommands
from FaradayIO import deviceconfig

# Global Constants
UART_PORT_APP_COMMAND = 2

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

@app.route('/getconfig', methods=['GET'])
def getconfig():
    if request.method == "POST":
        return '', 204 #Success but nothing to return

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

            proxy.POST(str(callsign), int(nodeid), UART_PORT_APP_COMMAND,
                       faradayCmd.CommandLocalSendReadDeviceConfig())

            time.sleep(2)

            data = proxy.GET(str(callsign), str(nodeid), proxy.CMD_UART_PORT)

            # Create device configuration module object
            device_config_object = deviceconfig.Device_Config_Class()

            # Decode BASE64 JSON data packet into
            data = proxy.DecodeRawPacket(data[0]["data"]) # Get first item

            data = data[0:116]

            print data, len(data)
            parsed_config_dict = device_config_object.parse_config_packet(data)

        except ValueError as e:
            logger.error("ValueError: " + str(e))
            return json.dumps({"error": str(e)}), 400
        except IndexError as e:
            logger.error("IndexError: " + str(e))
            return json.dumps({"error": str(e)}), 400
        except KeyError as e:
            logger.error("KeyError: " + str(e))
            return json.dumps({"error": str(e)}), 400

        #return '', 204  # HTTP 204 response cannot have message data

        data = "Device information..."

        return json.dumps(parsed_config_dict, indent=1), 200, \
               {'Content-Type': 'application/json'}


@app.route('/sendconfig', methods=["POST"])
def sendconfig():
    if request.method == "POST":
        try:
            # Obtain URL parameters (for local unit device callsign/ID assignment)
            callsign = request.args.get("callsign", "%")
            nodeid = request.args.get("nodeid", "%")

            # Read configuration file
            telemetryConfig = ConfigParser.RawConfigParser()
            telemetryConfig.read('faraday_config.ini')

            # Create dictionaries of each config section
            device_basic_dict = dict(telemetryConfig.items("Basic"))
            device_rf_dict = dict(telemetryConfig.items("RF"))
            device_gps_dict = dict(telemetryConfig.items("GPS"))
            device_telemetry_dict = dict(telemetryConfig.items("Telemetry"))

            # Create device configuration module object to use for programming packet creation
            device_config_object = deviceconfig.Device_Config_Class()

            # Update the device configuration object with the fields obtained from the INI configuration files loaded
            device_config_object.update_bitmask_configuration(int(device_basic_dict['configbootbitmask']))
            device_config_object.update_basic(int(1), str(device_basic_dict['callsign']), int(device_basic_dict['id']), int(device_basic_dict['gpio_p3']), int(device_basic_dict['gpio_p4']), int(device_basic_dict['gpio_p5']))
            device_config_object.update_rf(float(device_rf_dict['boot_frequency_mhz']), int(device_rf_dict['boot_rf_power']))
            device_config_object.update_gps(device_config_object.update_bitmask_gps_boot(int(device_gps_dict['gps_boot_bit'])), device_gps_dict['default_lattitude'], device_gps_dict['default_lattitude_direction'], device_gps_dict['default_longitude'], device_gps_dict['default_longitude_direction'], device_gps_dict['default_altitude'], device_gps_dict['default_altitude_units'])
            device_config_object.update_telemetry(device_config_object.update_bitmask_telemetry_boot(int(device_telemetry_dict['rf_telemetry_boot_bit']), int(device_telemetry_dict['uart_telemetry_boot_bit'])), int(device_telemetry_dict['telemetry_default_uart_interval']), int(device_telemetry_dict['telemetry_default_rf_interval']))

            # Create the raw device configuration packet to send to unit
            device_config_packet = device_config_object.create_config_packet()

            # Transmit device configuration to local unit as supplied by the function arguments
            proxy.POST(str(callsign), int(nodeid), UART_PORT_APP_COMMAND, faradayCmd.CommandLocal(faradayCmd.CMD_DEVICECONFIG, device_config_packet))

            return '', 204  # nothing to return but successful transmission

        except ValueError as e:
            logger.error("ValueError: " + str(e))
            return json.dumps({"error": str(e)}), 400

        except IndexError as e:
            logger.error("IndexError: " + str(e))
            return json.dumps({"error": str(e)}), 400

        except KeyError as e:
            logger.error("KeyError: " + str(e))
            return json.dumps({"error": str(e)}), 400


    else: #If a GET command
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
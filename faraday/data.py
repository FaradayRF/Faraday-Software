# Imports - General
import os
import ConfigParser
import json
import base64
import sys
import struct
import logging.config
import argparse
import shutil

from flask import Flask
from flask import request

# Add Faraday library to the Python path.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Imports - Faraday Specific
from faraday.proxyio import faradaybasicproxyio
from faraday.proxyio import commandmodule
#import packet

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

logger = logging.getLogger('Data')

# Load Telemetry Configuration from telemetry.ini file

#Create Proxy configuration file path
dataConfigPath = os.path.join(path, "data.ini")
logger.debug('data.ini PATH: ' + dataConfigPath)

dataConfig = ConfigParser.RawConfigParser()
dataConfig.read(dataConfigPath)

# Command line input
parser = argparse.ArgumentParser(description='Provides a generic data server to proxy.')
parser.add_argument('--init-config', dest='init', action='store_true', help='Initialize Data configuration file')

# Parse the arguments
args = parser.parse_args()

def initializeDataConfig():
    '''
    Initialize Data configuration file from data.sample.ini

    :return: None, exits program
    '''

    logger.info("Initializing Data")
    shutil.copy(os.path.join(path, "data.sample.ini"), os.path.join(path, "data.ini"))
    logger.info("Initialization complete")
    sys.exit(0)


# Now act upon the command line arguments
# Initialize and configure Data
if args.init:
    initializeDataConfig()

# Global variables
packet_struct = struct.Struct('2B 40s')
PACKET_LEN = 42
PAYLOAD_LEN = 40


# Definitions
APP_RFDATAPORT_UART_PORT = 1

# # Setup a Faraday IO object
faraday_1 = faradaybasicproxyio.proxyio()  # default proxy port

# Initialize Flask micro-framework
app = Flask(__name__)

def configparse():
    """ Parses configuration file for callsigns and node ID and returns them in JSON format"""
    local = {}
    units = range(0, config.getint('PROXY', 'UNITS'))

    for unit in units:
        # TODO We don't really check for valid input here yet
        item = "UNIT" + str(unit)
        callsign = config.get(item, "callsign").upper()
        nodeid = config.getint(item, "nodeid")

        local[str(item)] = {
            "callsign": callsign,
            "nodeid": nodeid,
        }

    return local

@app.route('/', methods=['GET', 'POST'])
def rfdataport():
    """
    Flask function that provides the "transmit" and "receive" functionality.
    """
    # If POST
    if request.method == 'POST':
        # Parse Flask arguments
        proxycallsign = request.args.get("localcallsign").upper() # Local device proxy unit
        proxynodeid = request.args.get("localnodeid") # Local device proxy unit
        # Destination device not supported at this time. All transmissions are broadcast 'CQCQCQ' to all units.
        destinationcallsign = request.args.get("destinationcallsign").upper()
        destinationnodeid = request.args.get("destinationnodeid")
        data = request.args.get("data")

        try:
            data = base64.b64decode(data) # All incoming data packets must be BASE64
        except TypeError as e:
            logger.info("BASE64 data error: {0}".format(e))

            # Return status
            return json.dumps(
                {"status": "BASE64 data error."}), 400
        else:

            if len(data) > PAYLOAD_LEN:
                # Fragment data
                fragment_list = fragmentmsg(data, PAYLOAD_LEN)

                for item in fragment_list:
                    # Create rfdataport application packet
                    cmd = 0 # Data Frame
                    seq = 0 # Not used, yet
                    datapacket = packet_struct.pack(cmd, seq, str(item))

                    # Transmit data packet
                    faraday_1.POST(proxycallsign, proxynodeid, APP_RFDATAPORT_UART_PORT, datapacket)

            else:
                # Create rfdataport application packet
                logger.debug("data {0}".format(str(data)))
                cmd = 0  # Data Frame
                seq = 0  # Not used, yet
                datapacket = packet_struct.pack(cmd, seq, str(data))

                # Transmit data packet
                faraday_1.POST(proxycallsign, proxynodeid, APP_RFDATAPORT_UART_PORT, datapacket)


            # Return status
            return json.dumps(
                {"status": "Posted Packet(s)"}), 200


    # If GET
    else:
        # Parse Flask arguments
        proxycallsign = request.args.get("localcallsign").upper()
        proxynodeid = request.args.get("localnodeid")

        # Get data from proxy for specified unit if available.
        rxdata = faraday_1.GET(proxycallsign, proxynodeid, APP_RFDATAPORT_UART_PORT)

        try:
            if rxdata is not None:

                for item in rxdata:
                    unpacked_rxdata = packet_struct.unpack(base64.b64decode(item['data']))
                    item['data'] = base64.b64encode(unpacked_rxdata[2])


                # If data available return as JSON
                return json.dumps(rxdata, indent=1), 200, \
                       {'Content-Type': 'application/json'}
        except:
            # No data available, return error 204 indicating "No Content"
            return '', 204  # HTTP 204 response cannot have message data

        else:
            # No data available, return error 204 indicating "No Content"
            return '', 204  # HTTP 204 response cannot have message data


def fragmentmsg(msg, fragmentsize):
    """
    This function fragments the supplied message into smaller packets or "chunks" that will fit into the
    pre-determined MTU (maximum transmissible unit) of the packet's path. Using an algorithm these fragments can
    be reassembled after reception.

    :param msg: The data to be fragmented

    :returns A list containing the fragmented "chunks" of data of the pre-determined size.
    """
    list_message_fragments = [msg[i:i + fragmentsize] for i in
                              range(0, len(msg), fragmentsize)]
    return list_message_fragments

def main():
    """Main function which starts the Flask server."""

    # Get INI file configuration for Flask server
    host = dataConfig.get("FLASK", "HOST")
    port = dataConfig.get("FLASK", "PORT")

    # Start the flask server
    app.run(host=host, port=port, threaded=True)


if __name__ == '__main__':
    main()

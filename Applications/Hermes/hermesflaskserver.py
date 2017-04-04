import os
import hermesobject as hermesobject
import ConfigParser
import json
import base64
import cPickle

from flask import Flask
from flask import request

# Open configuration INI
config = ConfigParser.RawConfigParser()
filename = os.path.abspath("hermes.ini")
config.read(filename)

# Global variables
dictmsgobj = {}


def configparse():
    """ Parses configuration file for callsigns and node ID and returns them in JSON format"""
    local = {}
    num = int(config.get('PROXY', 'UNITS'))
    units = range(0, num)

    for unit in units:
        # TODO We don't really check for valid input here yet
        item = "UNIT" + str(unit)
        callsign = config.get(item, "callsign").upper()
        nodeid = config.get(item, "nodeid")

        local[str(item)] = \
            {
                "callsign": callsign,
                "nodeid": nodeid,
            }

    local = json.dumps(local)
    return json.loads(local)


# Initialize Flask micro-framework
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def message():
    """
    Flask function that provides the "transmit" and "receive" functionality.

    POST:

    Transmits a provided payload data from a specified local unit to a specific remote unit.

    :param localcallsign: Flask parameter - Local unit callsign to transmit from
    :param localnodeid: Flask parameter - Local unit node ID to transmit from
    :param destinationcallsign: Flask parameter - Remote unit callsign to transmit to
    :param destinationnodeid: Flask parameter - Remote unit node ID to transmit to
    :param data: Flask parameter: Data payload to transmit to remote unit

    :return: Returns JSON success status for Flask server after transmission

    GET:

    Returns a JSON element containing the next received data from the receiver queue of the specified local unit.

    :param localcallsign: Flask parameter - Local unit callsign to transmit from
    :param localnodeid: Flask parameter - Local unit node ID to transmit from

    :return: Returns JSON element containing the next received data from the receiver queue
    """
    # Global variables
    global dictmsgobj

    # If POST
    if request.method == 'POST':
        # Parse Flask arguments
        localcallsign = request.args.get("localcallsign").upper()
        localnodeid = request.args.get("localnodeid")
        destinationcallsign = request.args.get("destinationcallsign").upper()
        destinationnodeid = request.args.get("destinationnodeid")
        data = request.args.get("data")

        # Get hermes TX/RX object from global dictionary
        unitmsgobj = dictmsgobj[localcallsign + '-' + localnodeid]

        # Transmit data to remote device
        unitmsgobj.transmit.send(destinationcallsign, int(destinationnodeid), str(data))

        # Return status
        return json.dumps(
            {"status": "Posted Packet(s)"
             }), 200

    # If GET
    else:
        # Parse Flask arguments
        localcallsign = request.args.get("localcallsign").upper()
        localnodeid = request.args.get("localnodeid")

        # Get hermes TX/RX object from global dictionary
        unitmsgobj = dictmsgobj[localcallsign + '-' + localnodeid]

        # Get next message from RX queue
        received_item = unitmsgobj.receive.getqueueitem()

        # Pickle dictionary data
        received_data_pickle = cPickle.dumps(received_item)

        # Encode to BASE64
        received_item_64 = base64.b64encode(received_data_pickle)

        return json.dumps(received_item_64, indent=1), 200, \
               {'Content-Type': 'application/json'}


@app.route('/queue', methods=['GET'])
def getqueue():
    """
    Flask function that returns the size of the receiver queue of the specified local unit.

    GET:

    :param localcallsign: Flask parameter - Local unit callsign to transmit from
    :param localnodeid: Flask parameter - Local unit node ID to transmit from

    :return:
    """
    # Global variables
    global dictmsgobj

    # Parse Flask arguments
    localcallsign = request.args.get("localcallsign").upper()
    localnodeid = request.args.get("localnodeid")
    unitmsgobj = dictmsgobj[localcallsign + '-' + localnodeid]

    """This function returns the number of packets in the receiver queue."""
    # Check Queue size of Unit #2 and receive packet (if received due to non-ARQ protocol)
    data = {"queuesize": unitmsgobj.receive.getqueuesize()}

    # Pickle dictionary data
    data_pickle = cPickle.dumps(data)

    # Encode to BASE64
    data_64 = base64.b64encode(data_pickle)

    return json.dumps(data_64, indent=1), 200, \
           {'Content-Type': 'application/json'}


def main():
    """Main function which starts the Flask server."""
    # Global variables
    global dictmsgobj

    # Get INI file configuration for Flask server
    config_host = config.get("FLASK", "HOST")
    config_port = config.get("FLASK", "PORT")

    # Start the flask server on localhost:8001
    hermeshost = config_host
    hermesport = config_port

    units = configparse()

    # Parse and save unit callsign-nodeid into global dictionary as keys to hermes objects
    for key in units:
        unitcallsign = units[key]['callsign']
        unitnodeid = units[key]['nodeid']
        unitname = unitcallsign + '-' + unitnodeid
        dictmsgobj[unitname] = hermesobject.MessageObject(unitcallsign, unitnodeid)

    app.run(host=hermeshost, port=hermesport, threaded=True)


if __name__ == '__main__':
    main()

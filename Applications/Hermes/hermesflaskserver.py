import os
import time
import hermesobject as hermesobject
import ConfigParser
import logging.config
import sys
import json
import base64
import cPickle

from flask import Flask
from flask import request

#Open configuration INI
config = ConfigParser.RawConfigParser()
filename = os.path.abspath("hermes.ini")
config.read(filename)

#Definitions

# #Variables
# transmitter_device_callsign = config.get("DEVICES", "UNIT0CALL") # Should match the connected Faraday unit as assigned in Proxy configuration
# transmitter_device_node_id = config.getint("DEVICES", "UNIT0ID") # Should match the connected Faraday unit as assigned in Proxy configuration
# transmitter_device_callsign = str(transmitter_device_callsign).upper()
faradaycallsign = config.get("DEVICES", "UNIT1CALL") # Should match the programmed callsign of the remote Faraday device to be commanded (receive)
faradaynodeid = config.getint("DEVICES", "UNIT1ID") # Should match the programmed callsign of the remote Faraday device to be commanded (receive)
faradaycallsign = str(faradaycallsign).upper()


# Create messaging unit objects with the two device connected to local proxy
faradayhermesobj = hermesobject.MessageObject(faradaycallsign, faradaynodeid)

# Initialize Flask microframework
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def getMessage():
    #If POST
    if request.method == 'POST':
        destcallsign = request.args.get("callsign").upper()
        destnodeid = request.args.get("nodeid")
        faradayhermesobj.transmit.send('KB1LQD', 1, 'test')
        print "POST!", destcallsign, destnodeid

        return json.dumps(
            {"status": "Posted Packet(s)"
                }), 200



    #If GET
    else:
        #Get next message from queue
        received_item = faradayhermesobj.receive.getqueueitem()

        #Pickle dictionary data
        received_data_pickle = cPickle.dumps(received_item)

        #Encode to BASE64
        received_item_64 = base64.b64encode(received_data_pickle)

        return json.dumps(received_item_64, indent=1), 200, \
           {'Content-Type': 'application/json'}


@app.route('/queue', methods=['GET'])
def getQueue():
    """This function returns the number of packets in the receiver queue."""
    #Check Queue size of Unit #2 and receive packet (if recieved due to non-ARQ protocol)
    data = {}
    data['queuesize'] = faradayhermesobj.receive.getqueuesize()


    # Pickle dictionary data
    data_pickle = cPickle.dumps(data)

    # Encode to BASE64
    data_64 = base64.b64encode(data_pickle)

    return json.dumps(data_64, indent=1), 200, \
       {'Content-Type': 'application/json'}

def main():
    """Main function which starts the Flask server."""

    #Get INI file configuration for Flask server
    config_host = config.get("FLASK", "HOST")
    config_port = config.get("FLASK", "PORT")

    # Start the flask server on localhost:8001
    hermesHost = config_host
    hermesPort = config_port


    app.run(host=hermesHost, port=hermesPort, threaded=True)

if __name__ == '__main__':
    main()

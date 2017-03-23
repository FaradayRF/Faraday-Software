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
# faradaycallsign0 = config.get("DEVICES", "UNIT1CALL") # Should match the programmed callsign of the remote Faraday device to be commanded (receive)
# faradaynodeid0 = config.getint("DEVICES", "UNIT1ID") # Should match the programmed callsign of the remote Faraday device to be commanded (receive)
# faradaycallsign0 = str(faradaycallsign0).upper()
#
# faradaycallsign1 = config.get("DEVICES", "UNIT0CALL") # Should match the programmed callsign of the remote Faraday device to be commanded (receive)
# faradaynodeid1 = config.getint("DEVICES", "UNIT0ID") # Should match the programmed callsign of the remote Faraday device to be commanded (receive)
# faradaycallsign1 = str(faradaycallsign1).upper()



# Create messaging unit objects with the two device connected to local proxy
# faradayhermesobj = hermesobject.MessageObject(faradaycallsign0, faradaynodeid0)

dictmsgobj = {}

def callsign2COM():
    """ Associate configuration callsigns with serial COM ports"""
    local = {}
    num = int(config.get('PROXY', 'UNITS'))
    units = range(0, num)

    for unit in units:
        # TODO We don't really check for valid input here yet
        item = "UNIT" + str(unit)
        callsign = config.get(item, "callsign").upper()
        nodeid = config.get(item, "nodeid")

        local[str(item)] =\
            {
            "callsign": callsign,
            "nodeid": nodeid,
            }

    local = json.dumps(local)
    return json.loads(local)

# Initialize Flask microframework
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def getMessage():
    global dictmsgobj

    #If POST
    if request.method == 'POST':
        localcallsign = request.args.get("localcallsign").upper()
        localnodeid = request.args.get("localnodeid")
        destinationcallsign = request.args.get("destinationcallsign").upper()
        destinationnodeid = request.args.get("destinationnodeid")
        data = request.args.get("data")
        unitmsgobj = dictmsgobj[localcallsign + '-' + localnodeid]
        unitmsgobj.transmit.send(destinationcallsign, int(destinationnodeid), str(data))

        return json.dumps(
            {"status": "Posted Packet(s)"
                }), 200

    #If GET
    else:
        localcallsign = request.args.get("localcallsign").upper()
        localnodeid = request.args.get("localnodeid")
        unitmsgobj = dictmsgobj[localcallsign + '-' + localnodeid]

        #Get next message from queue
        received_item = unitmsgobj.receive.getqueueitem()

        #Pickle dictionary data
        received_data_pickle = cPickle.dumps(received_item)

        #Encode to BASE64
        received_item_64 = base64.b64encode(received_data_pickle)

        return json.dumps(received_item_64, indent=1), 200, \
           {'Content-Type': 'application/json'}


@app.route('/queue', methods=['GET'])
def getQueue():

    localcallsign = request.args.get("localcallsign").upper()
    localnodeid = request.args.get("localnodeid")
    unitmsgobj = dictmsgobj[localcallsign + '-' + localnodeid]

    """This function returns the number of packets in the receiver queue."""
    #Check Queue size of Unit #2 and receive packet (if recieved due to non-ARQ protocol)
    data = {}
    data['queuesize'] = unitmsgobj.receive.getqueuesize()


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

    units = callsign2COM()

    # Print units from config
    for key in units:
        unitcallsign = units[key]['callsign']
        unitnodeid = units[key]['nodeid']
        unitname = unitcallsign + '-' + unitnodeid
        dictmsgobj[unitname] = hermesobject.MessageObject(unitcallsign, unitnodeid)

    app.run(host=hermesHost, port=hermesPort, threaded=True)



if __name__ == '__main__':
    main()

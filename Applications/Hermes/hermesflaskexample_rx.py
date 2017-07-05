#!/usr/bin/env python

import requests
import base64
import json
import time
import ConfigParser
import os

# Open configuration INI
config = ConfigParser.RawConfigParser()
filename = os.path.abspath("hermes.ini")
config.read(filename)

localcallsign = config.get('UNIT1', 'CALLSIGN')
localnodeid = int(config.get('UNIT1', 'NODEID'))


def getrxqueuesize(callsign, nodeid):
    """
    :param callsign: Callsign of the local device being queried
    :param nodeid: Node ID of the local device being queried
    :return: The RX queue size
    """

    payload = {'localcallsign': callsign, 'localnodeid': int(nodeid)}
    queuelen = requests.get('http://127.0.0.1:8005/queuelen', params=payload)
    queuesize = json.loads(base64.b64decode(queuelen.json()))

    return queuesize['queuesize']


def main():
    """
    Main function of the receive example of Hermes messaging application using Flask. This function loops continuously
    to check the Hermes Flask server receiver for the intended local Faraday device for new data to retrieve. It checks
    if data is present by querying the receive queue size, if data is present it retrieves ALL data each packet at a
    time until the queue is empty.
    """

    print "Receiver Started On: ", localcallsign.upper() + '-' + str(localnodeid)
    while True:
        # Sleep to release python process
        time.sleep(0.1)

        # Check if items in queue
        while getrxqueuesize(localcallsign, localnodeid) > 0:
            payload = {'localcallsign': localcallsign, 'localnodeid': localnodeid}
            rxdata = requests.get('http://127.0.0.1:8005/', params=payload)
            rx_dataitem = json.loads(base64.b64decode(rxdata.json()))
            print "\nFROM:", rx_dataitem['source_callsign']
            print "Message:", rx_dataitem['message']


if __name__ == '__main__':
    main()

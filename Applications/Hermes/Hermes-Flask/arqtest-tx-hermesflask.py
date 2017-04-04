import ConfigParser
import Queue
import base64
import cPickle
import os

import requests

import arq

##################Test IO Routines and Queues ###########################

# Transmitter
tx_rxtestproxyqueue = Queue.Queue()


def tx_transmitroutine(data):
    print "TX: Transmitting: ", data
    payload = {'localcallsign': localcallsign, 'localnodeid': localnodeid,
               'destinationcallsign': destinationcallsign, 'destinationnodeid': destinationnodeid, 'data': data}
    requests.post('http://127.0.0.1:8005/', params=payload)


def tx_receiveroutine():
    if getrxqueuesize(localcallsign, localnodeid) > 0:
        payload = {'localcallsign': localcallsign, 'localnodeid': localnodeid}
        rxdata = requests.get('http://127.0.0.1:8005/', params=payload)
        rx_b64_pickle = cPickle.loads(base64.b64decode(rxdata.json()))
        print "\nFROM:", rx_b64_pickle['source_callsign']
        print "Message:", rx_b64_pickle['message']
        return rx_b64_pickle['message']


###################################

config = ConfigParser.RawConfigParser()
filename = os.path.abspath("hermes.ini")
config.read(filename)

localcallsign = config.get('UNIT0', 'CALLSIGN')
localnodeid = int(config.get('UNIT0', 'NODEID'))
destinationcallsign = config.get('UNIT1', 'CALLSIGN')
destinationnodeid = int(config.get('UNIT1', 'NODEID'))

# Create ARQ Transmit object
testtxsm = arq.TransmitArqStateMachine(tx_transmitroutine, tx_receiveroutine)


def getrxqueuesize(callsign, nodeid):
    """
    :param callsign: Callsign of the local device being queried
    :param nodeid: Node ID of the local device being queried
    :return: The RX queue size
    """

    payload = {'localcallsign': callsign, 'localnodeid': int(nodeid)}
    queuelen = requests.get('http://127.0.0.1:8005/queue', params=payload)
    queue_b64_pickle = cPickle.loads(base64.b64decode(queuelen.json()))
    return queue_b64_pickle['queuesize']


def main():
    """
    Main function of the transmit example of Hermes messaging application using Flask. This function loops continuously
    getting user input text to transmit to the Flask server for wireless transmission to the intended remote device.
    """
    while 1:
        raw_input("Enter Message: ")

        # Transmit data list
        tx_listdata = ['this ', 'is', ' a', ' test', '.']

        # Insert new data for transmit
        testtxsm.newdataqueue(tx_listdata)


if __name__ == '__main__':
    main()

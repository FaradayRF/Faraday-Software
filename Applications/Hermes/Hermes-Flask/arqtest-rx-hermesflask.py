import ConfigParser
import Queue
import base64
import cPickle
import os

import requests

import arq

# Transmitter
# Receiver
rx_testproxyqueue = Queue.Queue()

config = ConfigParser.RawConfigParser()
filename = os.path.abspath("hermes.ini")
config.read(filename)

localcallsign = config.get('UNIT1', 'CALLSIGN')
localnodeid = int(config.get('UNIT1', 'NODEID'))
destinationcallsign = config.get('UNIT0', 'CALLSIGN')
destinationnodeid = int(config.get('UNIT0', 'NODEID'))


def rx_transmitroutine(data):
    print "RX: Transmitting: ", data, destinationcallsign, destinationnodeid
    # Place data into TX receive
    # tx_rxtestproxyqueue.put(data)
    payload = {'localcallsign': localcallsign, 'localnodeid': localnodeid,
               'destinationcallsign': destinationcallsign, 'destinationnodeid': destinationnodeid, 'data': data}
    requests.post('http://127.0.0.1:8005/', params=payload)


def rx_receiveroutine():
    if getrxqueuesize(localcallsign, localnodeid) > 0:
        payload = {'localcallsign': localcallsign, 'localnodeid': localnodeid}
        rxdata = requests.get('http://127.0.0.1:8005/', params=payload)
        rx_b64_pickle = cPickle.loads(base64.b64decode(rxdata.json()))
        print "\nFROM:", rx_b64_pickle['source_callsign']
        print "Message:", rx_b64_pickle['message']
        return rx_b64_pickle['message']


###################################


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

    # Create ARQ Receive object
    testrxsm = arq.ReceiveArqStateMachine(rx_transmitroutine, rx_receiveroutine)

    # Set state machine to START
    testrxsm.updatestate(arq.STATE_START)


if __name__ == '__main__':
    main()

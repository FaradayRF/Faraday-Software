import arq
import threading
import time
import timer
import Queue
import requests
import os
import ConfigParser

##################Test IO Routines and Queues ###########################

# Transmitter
tx_rxtestproxyqueue = Queue.Queue()

def tx_transmitroutine(data):
    print "TX: Transmitting: ", data
    payload = {'localcallsign': localcallsign, 'localnodeid': localnodeid,
               'destinationcallsign': destinationcallsign, 'destinationnodeid': destinationnodeid, 'data': data}
    requests.post('http://127.0.0.1:8005/', params=payload)

def tx_receiveroutine():
    if tx_rxtestproxyqueue.empty():
        return None
    else:
        data = tx_rxtestproxyqueue.get_nowait()
        return data
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


def main():
    """
    Main function of the transmit example of Hermes messaging application using Flask. This function loops continuously
    getting user input text to transmit to the Flask server for wireless transmission to the intended remote device.
    """
    while 1:
        message = raw_input("Enter Message: ")

        # Transmit data list
        tx_listdata = ['this ', 'is', ' a', ' test', '.']

        # Insert new data for transmit
        testtxsm.newdataqueue(tx_listdata)




if __name__ == '__main__':
    main()










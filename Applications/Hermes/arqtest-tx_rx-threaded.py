import arq
import threading
import time
import timer
import Queue

#Transmit data list
tx_listdata = ['this ', 'is', ' a', ' test', '.']

#Test IO Routines and Queues

# Transmitter
tx_rxtestproxyqueue = Queue.Queue()

def tx_transmitroutine(data):
    print "TX: Transmitting: ", data
    #Place into RX receive queue
    rx_testproxyqueue.put(data)

def tx_receiveroutine():
    if tx_rxtestproxyqueue.empty():
        return None
    else:
        data = tx_rxtestproxyqueue.get_nowait()
        print "TX: Got Data - ", data
        return data


# Receiver
rx_testproxyqueue = Queue.Queue()


def rx_transmitroutine(data):
    print "RX: Transmitting: ", data
    #Place data into TX receive
    tx_rxtestproxyqueue.put(data)

def rx_receiveroutine():
    if rx_testproxyqueue.empty():
        return None
    else:
        return rx_testproxyqueue.get_nowait()

####################################
## Receive
##################################

# Create object
testrxsm = arq.ReceiveArqStateMachine(rx_transmitroutine, rx_receiveroutine)

# Set state machine to START
testrxsm.updatestate(arq.STATE_START)


####################################
## Transmit
##################################

# Create object
testtxsm = arq.TransmitArqStateMachine(tx_listdata, tx_transmitroutine, tx_receiveroutine)

# Insert new data
testtxsm.newdataqueue(tx_listdata)

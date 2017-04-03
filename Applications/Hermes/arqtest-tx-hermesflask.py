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
        return data




####################################
## Transmit
##################################

# Create object
testtxsm = arq.TransmitArqStateMachine(tx_transmitroutine, tx_receiveroutine)



####################################
## Operations
##################################

print "Sleeping prior to transmit"
time.sleep(2)

# Insert new data for transmit
testtxsm.newdataqueue(tx_listdata)

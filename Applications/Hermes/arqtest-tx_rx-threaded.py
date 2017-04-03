import arq
import threading
import time
import timer
import Queue


#Test IO Routines

# Transmitter

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

rx_testproxyqueue = Queue.Queue()


tx_listdata = ['this ', 'is', ' a', ' test', '.']



# Create object
testrxsm = arq.ReceiveArqStateMachine(tx_listdata, rx_transmitroutine, rx_receiveroutine)


# Set state machine to START
print "Updating RX to START State"
testrxsm.updatestate(arq.STATE_START)


####################################
## Transmit
##################################

tx_listdata = ['this ', 'is', ' a', ' test', '.']

tx_rxtestproxyqueue = Queue.Queue()


# Create object
testtxsm = arq.TransmitArqStateMachine(tx_listdata, tx_transmitroutine, tx_receiveroutine)

# Insert new data
testtxsm.newdataqueue(tx_listdata)

#
# time.sleep(6)
# testtxsm.ackreceived()
# time.sleep(2)
# testtxsm.ackreceived()
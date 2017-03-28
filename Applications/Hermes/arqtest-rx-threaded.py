import arq
import threading
import time
import timer


listdata = ['this ', 'is', ' a', ' test', '.']

def transmitroutine( data):
    print "Transmitting: ", data

def receiveroutine():
    print "Receive Function! "
    return "RX Item"

# Create object
testrxsm = arq.ReceiveArqStateMachine(listdata, transmitroutine, receiveroutine)

# Add data to RX queue
testrxsm.putrxqueue("This")
testrxsm.putrxqueue("Is A")
testrxsm.putrxqueue("Test.")

# Set state machine to START
testrxsm.updatestate(arq.STATE_START)
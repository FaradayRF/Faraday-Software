import arq
import threading
import time
import timer
import Queue

testrxproxyqueue = Queue.Queue()


listdata = ['this ', 'is', ' a', ' test', '.']

def transmitroutine( data):
    print "Transmitting: ", data

def receiveroutine():
    if testrxproxyqueue.empty():
        return None
    else:
        return testrxproxyqueue.get_nowait()

# Create object
testrxsm = arq.ReceiveArqStateMachine(listdata, transmitroutine, receiveroutine)

# Add data to Fake RX Proxy queue
#testrxsm.putrxqueue("This")
#testrxsm.putrxqueue("Is A")
#testrxsm.putrxqueue("Test.")
testrxproxyqueue.put_nowait("This")
testrxproxyqueue.put_nowait("is")
testrxproxyqueue.put_nowait("a")
testrxproxyqueue.put_nowait("test")
testrxproxyqueue.put_nowait(".")

# Set state machine to START
print "Updating to START State"
testrxsm.updatestate(arq.STATE_START)
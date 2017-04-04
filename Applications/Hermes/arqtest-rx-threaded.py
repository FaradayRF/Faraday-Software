import arq
import time
import Queue

testrxproxyqueue = Queue.Queue()

listdata = ['this ', 'is', ' a', ' test', '.']


def transmitroutine(data):
    print "Transmitting: ", data


def receiveroutine():
    if testrxproxyqueue.empty():
        return None
    else:
        return testrxproxyqueue.get_nowait()


# Create object
testrxsm = arq.ReceiveArqStateMachine(transmitroutine, receiveroutine)

# Set state machine to START
print "Updating to START State"
testrxsm.updatestate(arq.STATE_START)

# Add data to Fake RX Proxy queue
testrxproxyqueue.put_nowait("This")
time.sleep(2)
testrxproxyqueue.put_nowait("is")
time.sleep(1)
testrxproxyqueue.put_nowait("a")
time.sleep(3)
testrxproxyqueue.put_nowait("test")
time.sleep(1)
testrxproxyqueue.put_nowait(".")

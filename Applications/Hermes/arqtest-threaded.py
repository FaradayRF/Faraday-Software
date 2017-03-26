import arq
import threading
import time
import timer




listdata = ['this ', 'is', ' a', ' test', '.']

def transmitroutine( data):
    print "Transmitting: ", data

# Create object
testtxsm = arq.TransmitArqStateMachine(listdata, transmitroutine)

# Insert new data
testtxsm.newdataqueue(listdata)


time.sleep(6)
testtxsm.ackreceived()
time.sleep(2)
testtxsm.ackreceived()
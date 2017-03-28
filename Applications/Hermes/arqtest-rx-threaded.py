import arq
import threading
import time
import timer




listdata = ['this ', 'is', ' a', ' test', '.']

def transmitroutine( data):
    print "Transmitting: ", data

def receiveroutine():
    print "Receive Function! "

# Create object
testrxsm = arq.ReceiveArqStateMachine(listdata, transmitroutine, receiveroutine)


import arq
import threading
import time
import timer




listdata = ['this ', 'is', ' a', ' test', '.']

def transmitroutine( data):
    print "Transmitting: ", data

def tx():
    print "TX'ing!"

tmr = timer.TimerClass(tx)
tmr.start()

time.sleep(3)

tmr.stop()

# Create object
testtxsm = arq.TransmitArqStateMachine(listdata, transmitroutine)

# Insert new data
testtxsm.newdataqueue(listdata)



# # Set state machine to start
# testtxsm.updatestate(arq.STATE_START)
#
# # Run state machine operations - START
# testtxsm.runstate()
# print "1"
#
# # Run state machine operations - next Data
# testtxsm.runstate()
# print "2"
#
# # Run state machine operations - TX
# testtxsm.runstate()
# print '3'
#
# # Run state machine operations - Get ACK
# testtxsm.runstate()
# print '4'
# # Receive ACK
# testtxsm.ackreceived()
# print '5'
# testtxsm.runstate() # ACK RX'd now moving to next data
#
# print '6'
#
# # Get next data
# testtxsm.runstate()
# testtxsm.runstate()
# testtxsm.runstate()
# testtxsm.ackreceived()
# testtxsm.runstate()
# testtxsm.runstate()
# testtxsm.runstate()
# testtxsm.ackreceived()
# testtxsm.runstate()
# testtxsm.runstate()
# testtxsm.runstate()
# testtxsm.ackreceived()
# testtxsm.runstate()
# testtxsm.runstate()
# testtxsm.runstate()
# testtxsm.ackreceived()
# testtxsm.runstate()
# testtxsm.runstate()
# testtxsm.runstate()
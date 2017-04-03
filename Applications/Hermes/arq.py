import time
import threading
import Queue
import timer

# Definitions
STATE_IDLE = 0 # IDLE state to wait for commanded start state
STATE_START = 1 # Reset counters/variables/etc... to default
STATE_GETNEXTDATA = 2 # Get the next data item to be transmitted
STATE_TX = 3 # Transmit data
STATE_GETACK = 4 # Wait for acknowledgement from receiver
STATE_RETRY = 5 # Retry current transmission data, update/check counters in case of timeout
STATE_SENDACK = 6 # Send acknowledgement to transmitter

ACK_MSG = "ACK" # Acknowledgement message

MAXRETRIES = 3 # Maximum number of retries to attempt before timing out
ACKINTERVAL = 3 # Time to wait for the receiver to send ACK


class TransmitArqStateMachine(object):

    def __init__(self, datalist, funcptr_tx, funcptr_rx):
        """
        This class provides the state machine functionality for the transmitter portion of a basic stop-and-wait ARQ
        protocol.
        """
        self.functionpointer_tx = funcptr_tx
        self.functionpointer_rx = funcptr_rx
        self.state = STATE_IDLE
        self.retries = 0
        self.dataqueue = Queue.Queue()
        self.currentdata = ''
        self.acksuccess = False

        self.statedict = {
            STATE_IDLE: self.stateidle,
            STATE_START: self.statestart,
            STATE_GETNEXTDATA: self.stategetnextdata,
            STATE_TX: self.statetx,
            STATE_GETACK: self.stategetack,
            STATE_RETRY: self.stateretry,
        }

        # Initialize data into queue
        self.newdataqueue(datalist)

        # Create ARQ timer object to run the ARQ objects "runstate()" function periodically
        self.arqtimer = timer.TimerClass(self.runstate, 0.5)
        self.arqtimer.start()
        self.arqstarttime = time.time()

    def newdataqueue(self, datalist):
        """
        Reset and fill data queue with new data.
        :param datalist: A list of data packets to transmit from index [0] to max index
        :return:
        """
        self.dataqueue.queue.clear()
        self.retries = 0
        for item in datalist:
            self.dataqueue.put(item)

        # Updated state to START
            self.updatestate(STATE_START)

    def runstate(self):
        """
        Check the current state and run the states function.
        :return:
        """
        # Use the current objects state to run the intended state function
        self.statedict[self.state]()

    def updatestate(self, state):
        """
        Change the current state of the state machine object.
        :param state: The new state of the state machine object to change too
        :return:
        """
        self.state = state

    def stateidle(self):
        """
        IDLE state function:

        IDLE simple waits for a commanded START state.
        :return:
        """
        #print "IDLE"

    def statestart(self):
        """
        START State Function:

        * Reset variables/counters/etc... to default values
        :return:
        """

        print "TX: START"

        self.acksuccess = False

        # Updated state
        self.updatestate(STATE_GETNEXTDATA)


    def stategetnextdata(self):
        """
        This function retrieves the next data packet to transmit.
        :return:
        """
        print "NEXT DATA"

        if self.dataqueue.empty():
            # No more data
            self.updatestate(STATE_IDLE)
        else:
            # Get next data packet
            self.currentdata = self.dataqueue.get_nowait()
            # Updated state
            self.updatestate(STATE_TX)



    def statetx(self):
        """
        Transmit the current data packet.

        :return:
        """

        print "TX: "
        self.functionpointer_tx(self.currentdata)

        # Reset the ARQ base time
        self.arqstarttime = time.time()

        # Updated state
        self.updatestate(STATE_GETACK)

    def stategetack(self):
        """
        Wait to receive the ACK from the receiver for the current data transmission.

        :return:
        """

        # Compute ARQ timeout time
        timeouttime = time.time() - self.arqstarttime

        #print "GET ACK", timeouttime

        # Get any received packets
        rxdata = self.functionpointer_rx()

        if rxdata is not None:
            if rxdata == ACK_MSG:
                print "TX: GOT ACK"
                self.ackreceived()

        if timeouttime > ACKINTERVAL:
            # Retry
            self.updatestate(STATE_RETRY)
        else:
            # Check for ACK
            if self.acksuccess:
                # ACK received - Reset ACK flag and get next data
                self.acksuccess = False
                self.updatestate(STATE_GETNEXTDATA)
            else:
                # ACK not received
                pass



    def stateretry(self):
        """
        Prior transmission failed to receive an ACK from receiver. Update counters and retry transmission unless max
        retry count has been reached.

        :return:
        """

        print "TX: Retry", self.retries
        # Check retry count
        if self.retries > MAXRETRIES:
            # Timeout
            self.arqtimer.stop()
            print "TX: TIMED OUT!"
        else:
            # Update retry count and retry transmission
            self.retries += 1
            self.updatestate(STATE_TX)

    def ackreceived(self):
        print "TX: ACK RECEIVED!"
        self.acksuccess = True


class ReceiveArqStateMachine(object):

    def __init__(self, funcptr_tx, funcptr_rx):
        """
        This class provides the state machine functionality for the receiver portion of a basic stop-and-wait ARQ
        protocol.
        """
        self.functionpointer_tx = funcptr_tx
        self.functionpointer_rx = funcptr_rx
        self.state = STATE_IDLE
        self.retries = 0
        self.dataqueue = Queue.Queue()

        self.statedict = {
            STATE_IDLE: self.stateidle,
            STATE_START: self.statestart,
            STATE_SENDACK: self.statesendack,
        }

        # Create ARQ timer object to run the ARQ objects "runstate()" function periodically
        self.arqtimer = timer.TimerClass(self.runstate, 0.5)
        self.arqtimer.start()
        self.arqstarttime = time.time()


    def runstate(self):
        """
        Check the current state and run the states function.
        :return:
        """
        # Use the current objects state to run the intended state function
        self.statedict[self.state]()

    def updatestate(self, state):
        """
        Change the current state of the state machine object.
        :param state: The new state of the state machine object to change too
        :return:
        """
        self.state = state

    def stateidle(self):
        """
        IDLE state function:

        IDLE simple waits for a commanded START state.
        :return:
        """
        print "RX: IDLE"

    def statestart(self):
        """
        START State Function:

        * Reset variables/counters/etc... to default values
        :return:
        """

        #print "START"
        self.getreceiveitem()



    def statesendack(self):
        """
        Send ACK to transmitter
        :return:
        """
        self.functionpointer_tx(ACK_MSG)

        # Update state to START
        self.updatestate(STATE_START)

    def putrxqueue(self, rxdata):
        """
        Inserts the supplied data into the receive data queue in the class object.
        :return:
        """

        self.dataqueue.put_nowait(rxdata)

    def getrxqueue(self):
        """
        This function interacts with the class objects receive data Queue and returns the next item in the queue. It
        returns False if nothing is to be returned.
        :return:
        """

        if self.dataqueue.empty():
            # Nothing to return, return False
            return False
        else:
            # Return next data item
            return self.dataqueue.get_nowait()

    def getreceiveitem(self):
        """
        Attempt to get the next item waiting to be received. This function assumes the functionpointer_rx() returns
        the next received item or False if no items are waiting to be retrieved.
        :return:
        """
        rxitem = self.functionpointer_rx()
        if rxitem == None:
            pass #print "RX: None Item"
        else:
            self.putrxqueue(rxitem)
            print "RX: Placed:", rxitem

            # Send ACK
            self.updatestate(STATE_SENDACK)

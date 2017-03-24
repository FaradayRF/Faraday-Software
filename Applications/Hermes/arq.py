import time
import threading
import Queue


# Definitions
STATE_IDLE = 0 # IDLE state to wait for commanded start state
STATE_START = 1 # Reset counters/variables/etc... to default
STATE_GETNEXTDATA = 2 # Get the next data item to be transmitted
STATE_TX = 3 # Transmit data
STATE_GETACK = 4 # Wait for acknowledgement from receiver
STATE_RETRY = 5 # Retry current transmission data, update/check counters in case of timeout

MAXRETRIES = 3 # Maximum number of retries to attempt before timing out
ACKINTERVAL = 5 # Time to wait for the receiver to send ACK


class TransmitArqStateMachine(object):

    def __init__(self, funcptr_tx):
        """
        This class provides the state machine functionality for the transmitter portion of a basic stop-and-wait ARQ
        protocol.
        """
        self.functionpointer_tx = funcptr_tx
        self.state = STATE_IDLE
        self.retries = 0
        self.dataqueue = Queue.Queue()
        self.currentdata = ''
        self.statedict = {
            STATE_IDLE: self.stateidle,
            STATE_START: self.statestart,
            STATE_GETNEXTDATA: self.stategetnextdata,
            STATE_TX: self.statetx,
            STATE_GETACK: self.stategetack,
            STATE_RETRY: self.stateretry,
        }

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
        print "IDLE"

    def statestart(self):
        """
        START State Function:

        * Reset variables/counters/etc... to default values
        :return:
        """

        print "START"

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

        print "TX"
        self.functionpointer_tx()

        # Updated state
        self.updatestate(STATE_GETACK)

    def stategetack(self):
        """
        Wait to receive the ACK from the receiver for the current data transmission.

        :return:
        """

        print "GET ACK"

    def stateretry(self):
        """
        Prior transmission failed to receive an ACK from receiver. Update counters and retry transmission unless max
        retry count has been reached.

        :return:
        """

        print "Retry"


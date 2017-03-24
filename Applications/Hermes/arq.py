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



class TransmitArqStateMachine(object):

    def __init__(self):
        """
        This class provides the state machine functionality for the transmitter portion of a basic stop-and-wait ARQ
        protocol.
        """
        self.state = STATE_IDLE

    def updatestate(self, state):
        """
        Change the current state of the state machine object.
        :param state: The new state of the state machine object to change too
        :return:
        """
        self.state = state


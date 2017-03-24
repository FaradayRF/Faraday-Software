import time
import threading
import Queue


# Definitions
STATE_IDLE = 0

class transmitArqStateMachine(object):

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

    
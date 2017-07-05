#-------------------------------------------------------------------------------
# Name:        layer_2_protocol
# Purpose:
#
# Author:      Brent
#
# Created:     14/07/2015
# Copyright:   (c) Brent 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import layer_2_protocol
import threading
import time
import Queue
import logging

# Get configured logger
logger = logging.getLogger('UARTStack')


class Layer2ServiceObject(threading.Thread):
    def __init__(self, port, baud, timeout):
        test_ser_queue_1 = Queue.Queue()  # Infinite
        test_ser_queue_2 = Queue.Queue()  # Infinite
        self.protocol_object = layer_2_protocol.layer_2_object(port, baud, timeout)
        self.layer_initialized = True
        #Initialize class variables
        self.tx = layer_2_protocol.Faraday_Datalink_Device_Transmit_Class(test_ser_queue_1, self.protocol_object)
        self.rx = layer_2_protocol.Receiver_Datalink_Device_Class(test_ser_queue_2, self.protocol_object)
        self.enabled = True
        #Start
        threading.Thread.__init__(self)
        self.start()  #Starts the run() function and thread

    def POST(self, payload_data):
        try:
            self.tx.insert_data(payload_data)
        except:
            logger.error("Layer2ServiceObject POST() error")

    def GET(self):
        """
        Gets the next received Layer 2 datagram in the FIFO
        """
        try:
            return self.rx.GET()
        except:
            logger.error("Layer2ServiceObject GET() error")

    def IsEmpty(self):
        """
        Returns True if FIFO is empty, returns False if item(s) in FIFO.
        """
        try:
            return self.rx.IsEmpty()
        except:
            logger.error("Layer2ServiceObject isEmpty() error")

    def Abort(self):
        logger.error("Aborting Layer2ServiceObject!")
        #Self abort
        self.enabled = False

        #Lower Functions
        self.protocol_object.serial_physical_obj.abort()  #layer_2_protocol
        self.tx.abort()  #Faraday_Datalink_Device_Transmit_Class
        self.tx.insert_data_class.abort()  #Transmit_Insert_Data_Queue_Class
        self.rx.Abort()  #Receiver_Datalink_Device_Class
        self.rx.receiver_class.abort()  #Receiver_Datalink_Device_State_Parser_Class

    def run(self):
        while(self.enabled):
            time.sleep(0.001)

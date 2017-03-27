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

#test_tx = layer_2_protocol.Faraday_Datalink_Device()
#test_rx = layer_2_protocol.Faraday_Datalink_Device_Receive_2()

#Globals
#layer_initialized = False
#device = ''
#DATALINK_PAYLOAD_LENGTH = 125



class Layer2Object(object):
    def __init__(self, port, baud, timeout):
        self.protocol_object = layer_2_protocol.layer_2_object(port, baud, timeout)
        self.service_object = device_1(self.protocol_object)
        self.layer_initialized = True

class Layer2ServiceObject(threading.Thread):
    def __init__(self, port, baud, timeout):
        test_ser_queue_1 = Queue.Queue() # Infinite
        test_ser_queue_2 = Queue.Queue() # Infinite
        self.protocol_object = layer_2_protocol.layer_2_object(port, baud, timeout)
        self.layer_initialized = True
        #Initialize class variables
        self.tx = layer_2_protocol.Faraday_Datalink_Device_Transmit_Class(test_ser_queue_1, self.protocol_object)
        self.rx = layer_2_protocol.Receiver_Datalink_Device_Class(test_ser_queue_2, self.protocol_object)
        self.enabled = True
        #Start
        threading.Thread.__init__(self)
        self.start() #Starts the run() function and thread

    def POST(self, payload_data):
        self.tx.insert_data(payload_data)

    def GET(self):
        """
        Gets the next received Layer 2 datagram in the FIFO
        """
        return self.rx.GET()

    def IsEmpty(self):
        """
        Returns True if FIFO is empty, returns False if item(s) in FIFO.
        """
        return self.rx.IsEmpty()

    def Abort(self):
        #Self abort
        self.enabled = False

        #Lower Functions
        self.protocol_object.serial_physical_obj.abort() #layer_2_protocol
        self.tx.abort() #Faraday_Datalink_Device_Transmit_Class
        self.tx.insert_data_class.abort() #Transmit_Insert_Data_Queue_Class
        self.rx.Abort() #Receiver_Datalink_Device_Class
        self.rx.receiver_class.abort() #Receiver_Datalink_Device_State_Parser_Class




    def run(self):
        while(self.enabled):
            time.sleep(0.001)



##def uart_datalink_receive_datagram():
##    global layer_initialized, device
##    if(layer_initialized):
##        if(not device.rx.rx_data_payload_queue.empty()):
##            return device.rx.rx_data_payload_queue.get()
##        else:
##            return False
##    else:
##        print "Layer not initialized!"
##
##def uart_datalink_transmit_datagram(payload):
##    global layer_initialized, device
##    if(layer_initialized):
##        #time.sleep(0.25)
##        if(len(payload)<=DATALINK_PAYLOAD_LENGTH):
##            #print "TX Length:", len(payload)
##            device.tx.insert_data(payload)
##        else:
##            print "Payload Too Long!", len(payload)
##    else:
##            print "Layer not initialized!"


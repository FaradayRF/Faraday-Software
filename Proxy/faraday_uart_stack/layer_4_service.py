#-------------------------------------------------------------------------------
# Name:        module2
# Purpose:
#
# Author:      Brent
#
# Created:     27/09/2015
# Copyright:   (c) Brent 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import layer_4_protocol
import layer_2_service
import threading
import time
import Queue
import struct


DEBUG = False


#####################################################
##
## uart_interface_class()
##
## This class implements the uart datalink layer as the layer beneath
## It creates a thread that can send and receive datagrams that represent
## a payload and a respective "service number" which is much like a TCP socket "port"
## This is a completely connenction-less and un-reliable packet based layer.
##
## This layer is extreamly simple and  serves mainly as an organizing tool
## for traffic in the network stack. For example, ADC data, commands, and other data
## can be separated into specific "lanes" of data. This allows a single datalink layer
## to easily interface to multiple "interfaces" above such as multiple applications with
## respective data formats and meanings.
##
## Protocol Packet Format: [Payload[], Service Number (0-255)]
##
## Work should be done to improve protocol layer modularity and isolation from other layers
## Ideas:
##        - Implement a "notify" type system (or semi implemented with a housekeeper)
##
##
## To-Do:
##        - Update to match Faraday limited "queue"
##        - Queue overflow reaction needs to match Faraday
##
#####################################################
class faraday_uart_object(threading.Thread):
    def __init__(self, port, baud, timeout):
        self.uart_device = ''
        self.rx_unparsed = ''
        self.enabled = True
        self.uart_layer_output_status = True
        self.transmit_datagram_queue = Queue.Queue(0)
        self.receive_datagram_queue = Queue.Queue(0)
        self.receive_parsed_queue_dict = {} #Dictionary to manage multiple queues spurred
        self.layer_2_object = layer_2_service.Layer2ServiceObject(port, baud, timeout)
        self.transport_packet_struct = struct.Struct('BB123s')
        self.TRANPORT_PACKET_LENGTH = 125
        self.TRANPORT_PAYLOAD_LENGTH = 123
        self.QUEUE_SIZE_DEFAULT = 100

        #Start
        threading.Thread.__init__(self)
        self.start() #Starts the run() function and thread

    def POST(self, service_number, payload_length, payload):
        """
        Places a given payload data to the given UART service number to be transmited to the UART device. This places the item in the transmit FIFO.
        """

        #Calculation protocol violations before trying to create a transport packet
        payload_check = len(payload) < self.TRANPORT_PAYLOAD_LENGTH
        service_number_check = service_number < 256
        payload_len_check = payload_length <= self.TRANPORT_PAYLOAD_LENGTH

        #Check to make sure the payload isn't larger than maximum allowed per protocol
        if(service_number_check and service_number_check and payload_len_check):
            #Create transport packet raw
            transport_packet = layer_4_protocol.create_packet(service_number, payload_length, payload)
            #Pad fixed length packet to correct fixed size
            transport_packet_padded = transport_packet + chr(0xff)*(self.TRANPORT_PAYLOAD_LENGTH - len(payload))
            self.transmit_datagram_queue_put(transport_packet_padded)
        else:
            print "ERROR: Transport protocol violation"
            print "Payload Length", payload_check, len(payload)
            print "Payload Length Byte", payload_len_check, payload_length
            print "Service Number Check", service_number_check, service_number

    def GET(self, service_port):
        """
        Returns the next received datagram payload from the FIFO for the given UART service port number. Returns False if no items to be retrieved.

        """
        try:
            rx_data = self.receive_parsed_queue_dict[service_port].get_nowait()
            return rx_data
        except:
            return False

    def transmit_datagram_queue_put(self, item):
        self.transmit_datagram_queue.put(item)

    def transmit_datagram_queue_get(self):
        if(not self.transmit_datagram_queue.empty()):
            return self.transmit_datagram_queue.get()

    def transmit_datagram_queue_inwait(self):
        return self.transmit_datagram_queue.qsize()

    def transmit_datagram_queue_hasitem(self):
        return not self.transmit_datagram_queue.empty()

    def receive_datagram_queue_put(self, item):
        self.receive_datagram_queue.put(item)

    def receive_datagram_queue_get(self):
        if(not self.layer_2_object.IsEmpty()):
            #return self.receive_datagram_queue.get()
            return self.layer_2_object.GET()
        else:
            return False

    def receive_datagram_queue_inwait(self):
        return self.receive_datagram_queue.qsize()

    def receive_datagram_queue_hasitem(self):
        return not self.layer_2_object.IsEmpty()
        #return not self.receive_datagram_queue.empty()

    def process_received_datagram(self, datagram):
        parsed_datagram_dict = layer_4_protocol.parse_packet(datagram)
        if DEBUG:
            print "RX'd:", parsed_datagram_dict

    def RxPortHasItem(self,service_number):
        try:
            return not self.receive_parsed_queue_dict[service_number].empty()
        except:
            self.receive_service_queue_open(service_number, self.QUEUE_SIZE_DEFAULT)
            pass

    def receive_service_queue_open(self, service_number, queue_size):
        self.receive_parsed_queue_dict[service_number] = Queue.Queue(queue_size)

    def receive_service_queue_put(self, payload, service_number):
        # THIS FUNCTION POPS OLD DATA AND REPLACES WITH NEW DATA. WHY?
        #print "#", service_number, str(service_number).encode('hex')
        try:
            if(self.receive_parsed_queue_dict[service_number].full()):
                #Pop old data off then insert new data
                self.receive_parsed_queue_dict[service_number].get_nowait()
                self.receive_parsed_queue_dict[service_number].put_nowait(payload)
            else:
                #Insert new data
                self.receive_parsed_queue_dict[service_number].put_nowait(payload)

        except:
            #To match MSP430 current limitation in firmware require the service to be "opened" first
            #Service not opened , ignore payload
            self.receive_service_queue_open(service_number, self.QUEUE_SIZE_DEFAULT)
            if(self.receive_parsed_queue_dict[service_number].full()):
                #Pop old data off then insert new data
                self.receive_parsed_queue_dict[service_number].get_nowait()
                self.receive_parsed_queue_dict[service_number].put_nowait(payload)
            else:
                #Insert new data
                self.receive_parsed_queue_dict[service_number].put_nowait(payload)
            pass

    def receive_service_queue_get(self, service_number):
        try:
            return self.receive_parsed_queue_dict[service_number].get_nowait()
        except:
            #Nothing in queue
            print "Nothing in queue"
            return False
    def uart_layer_receive_link(self):
        rx_item = self.layer_2_object.GET()
        if(rx_item != False):
            try:
                unpacked_transport = self.transport_packet_struct.unpack(rx_item)
                rx_service_number = int(unpacked_transport[0])
                length = unpacked_transport[1]
                try:
                    transport_payload = unpacked_transport[2][:length]#.encode('hex')
                    self.receive_service_queue_put(transport_payload, rx_service_number)
                except:
                    print "data fail"
            except:
                print "transport fail"
        else:
            pass


    def Abort(self):
        self.layer_2_object.Abort()#Abort lower layers
        self.enabled = False

    def run(self):
        while(self.enabled):
            #Delay to allow CPU utilization relaxing
            time.sleep(0.001)
            #check for transmit items
            if(self.transmit_datagram_queue_hasitem()):
                tx_datagram = self.transmit_datagram_queue_get()
                self.layer_2_object.POST(tx_datagram)
            #check for receive items
            if(self.receive_datagram_queue_hasitem() != False):
                rx_datagram = self.receive_datagram_queue_get()
                try:
                    parsed_l4_packet = layer_4_protocol.parse_packet(rx_datagram)
                    self.receive_service_queue_put(parsed_l4_packet[2], parsed_l4_packet[0])

                except:
                    print "FAILED PARSING", rx_datagram
                    pass
            #Check uart datalink receive for new datagrams to parse
            self.uart_layer_receive_link()

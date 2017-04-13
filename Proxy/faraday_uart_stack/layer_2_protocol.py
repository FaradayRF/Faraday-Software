#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Brent
#
# Created:     12/07/2015
# Copyright:   (c) Brent 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import serial
import threading
import Queue
import time
import struct
#test_ser_queue_1 = Queue.Queue() # Infinite
#test_ser_queue_2 = Queue.Queue() # Infinite

#Globals
#serial_physical_obj = ''

#def init_layer(port, baud, timeout):
#    global serial_physical_obj
#    serial_physical_obj = test_physical_layer_class(port, baud, timeout)


class layer_2_object(object):
    def __init__(self, port, baud, timeout):
        self.serial_physical_obj = layer_2_protocol(port, baud, timeout)


class layer_2_protocol(threading.Thread):
    def __init__(self, com, baud, timeout_time):
        self.ser = serial.Serial(com, baud, timeout=timeout_time)
        self.serial_rx_queue = Queue.Queue()  # Infinite
        self.serial_tx_queue = Queue.Queue()  # Infinite
        self.enabled = True

        #Start
        threading.Thread.__init__(self)
        self.start()  #Starts the run() function and thread

    def abort(self):
        self.enabled = False
        print "Aborting Layer 2 Class Main"
        self.ser.close()

    def close_connection(self):
        self.ser.close()

    ## EDIT BSALMI: 1-21-2016
    def get_byte(self):
        if(not self.serial_rx_queue.empty()):
            rx_byte = self.serial_rx_queue.get()
            return rx_byte
        else:
            return False

    def send_byte(self, databyte):
        self.serial_tx_queue.put(databyte)

    def rx_buffer_count(self):
        return self.ser.inWaiting()

    def run(self):
        while self.enabled:
            #Delay to allow threaded CPU utilization relaxing
            time.sleep(0.001)  #Shouldn't need this! BSALMI 6/13/16
            if(self.enabled):
                #Check for bytes to transmit over serial
                if(not self.serial_tx_queue.empty()):
                    while(not self.serial_tx_queue.empty()):
                        self.ser.write(self.serial_tx_queue.get())
                #Check for bytes to receive from serial
                if self.ser.inWaiting() > 0:
                    rx_buffer_inwaiting = self.ser.inWaiting()
                    self.serial_rx_queue.put(self.ser.read(rx_buffer_inwaiting))


##class test_physical_layer_class(threading.Thread):
##    def __init__(self, com, baud,timeout_time):
##        self.ser = serial.Serial(com, baud, timeout = timeout_time)
##        self.serial_rx_queue = Queue.Queue() # Infinite
##        self.serial_tx_queue = Queue.Queue() # Infinite
##        self.enabled = True
##
##        #Start
##        threading.Thread.__init__(self)
##        self.start() #Starts the run() function and thread
##
##
##    def abort(self):
##        self.enabled = False
##
##    def close_connection(self):
##        self.ser.close()
##
##    ## EDIT BSALMI: 1-21-2016
##    def get_byte(self):
##        if(not self.serial_rx_queue.empty()):
##            rx_byte = self.serial_rx_queue.get()
##            return rx_byte
##        else:
##            return False
##
##
##    def send_byte(self, databyte):
##        self.serial_tx_queue.put(databyte)
##
##    def rx_buffer_count(self):
##        return self.ser.inWaiting()
##
##    def run(self):
##        while(self.enabled):
##            #Delay to allow threaded CPU utilization relaxing
##            time.sleep(0.001) #Shouldn't need this! BSALMI 6/13/16
##            #Check for bytes to transmit over serial
##            if(not self.serial_tx_queue.empty()):
##                while(not self.serial_tx_queue.empty()):
##                    self.ser.write(self.serial_tx_queue.get())
##            #Check for bytes to receive from serial
##            if((self.ser.inWaiting()>0)):
##                rx_buffer_inwaiting = self.ser.inWaiting()
##                self.serial_rx_queue.put(self.ser.read(rx_buffer_inwaiting))


################################################################################
# Faraday_Datalink_Device_Transmit_Class() CLASS
# Description:
################################################################################
class Faraday_Datalink_Device_Transmit_Class(threading.Thread):
    """
    This class object is the front end of the Faraday to computer
     data-link layer protocol. This class provides SERVICES for the datalink layer
     between a local Faraday and a host computer, primaraly over USB serial COM port.
    """

    def __init__(self, output_channel, serial_physical_obj):
        """
        This function initializes the class and it's variables.
        """

        #Initialize class variables
        self.enable_flag = True  #Class flag to keep loop running when True, aborts when False
        self.encapsulate_startbyte = chr(0x7b)  #Ensure these are the same as the self.insert_data_class escapes!
        self.encapsulate_stopbyte = chr(0x7c)  #Ensure these are the same as the self.insert_data_class escapes!
        self.encapsulate_escapebyte = chr(0x7d)  #Ensure these are the same as the self.insert_data_class escapes!
        self.insert_data_class = Transmit_Insert_Data_Queue_Class()
        self.output_channel = output_channel
        self.serial_physical_obj = serial_physical_obj
        #global serial_physical_obj

        #Start
        threading.Thread.__init__(self)
        self.start()  #Starts the run() function and thread

    def abort(self):
        """
        Perform needed actions to stop the class object while(1) loop.
        """
        self.enable_flag = False
        print "Aborting Layer 2 Transmit Class!"

    def insert_data(self, payload):
        """
        Accepts a bytearray/string as a payload to transmit. The service will fragment and encapsulate the data payload as needed and reassemble with the respective receiving service.
        """
        self.insert_data_class.tx_data_queue.put(payload)

    def Send_Flow_Control_Stop_CMD(self, command):  #INVALID
        """
        Invalid? Not actually implemented?
        """
        self.insert_data_class.Encapsulate_Data_CMD(self.encapsulate_startbyte, self.encapsulate_stopbyte, self.encapsulate_escapebyte, command)

    def run(self):
        """
        Main class run function to perform a while(1) loop to retrieve waiting data to transmit and transmit it.
        """
        while self.enable_flag:
            #Delay to allow threaded CPU utilization relaxing
            time.sleep(0.01)

            #Check for new data to transmit
            if not self.insert_data_class.tx_packet_queue.empty():
                #  Loop through all known queue data and transmit
                for i in range(0, self.insert_data_class.tx_packet_queue.qsize()):
                    #New data available, retrieve single data "packet"
                    packet = self.insert_data_class.tx_packet_queue.get()

                    #Transmit
                    for i in range(0, len(packet), 1):
                        self.output_channel.put(packet[i])
                        self.serial_physical_obj.serial_physical_obj.send_byte(packet[i])


################################################################################
# Transmit_Insert_Data_Queue_Class() CLASS
# Description:
################################################################################
class Transmit_Insert_Data_Queue_Class(threading.Thread):
    """
    This class object provides the lower level functionality to create the services provided.
    This additional class member allows for a specific threads to be created the lower level
    functions that fragment, frame, and other low level functionality to provide the higher
    level class the service function(s).
    """

    def __init__(self):
        """
        This function initializes the class and it's variables.
        """
        #Initialize class variables
        self.tx_data_queue = Queue.Queue()  #Queue FIFO with MAXSIZE=infinite - Queue to hold payload data raw
        self.tx_packet_queue = Queue.Queue()  #Queue FIFO with MAXSIZE=infinite - Queue to hold fragmented and encapsulated data
        self.enable_flag = True  #Class flag to keep loop running when True, aborts when False
        self.max_payload_size = 5
        self.tx_queue_item = ''
        self.fragment_data_list = []
        self.framing_startbyte = chr(0x7b)
        self.framing_stopbyte = chr(0x7c)
        self.framing_escapebyte = chr(0x7d)
        self.datalink_packet_format = 'c' + str(self.max_payload_size) + 'c' + 'c'

        #Start
        threading.Thread.__init__(self)
        self.start()  #Starts the run() function and thread

    def abort(self):
        """
        Perform needed actions to stop the class object while(1) loop.
        """
        self.enable_flag = False
        print "Aborting Layer 2 Transmit Protocol!"

    def run(self):
        """
        Main while(1) loop for the class object to check for new data to transmit.
        """
        while self.enable_flag:
            #Check if new data is avaliable in the Queue
            if(not self.tx_data_queue.empty()):
                for i in range(0, self.tx_data_queue.qsize()):
                    #Get next queue item to transmit
                    self.datalink_payload = self.tx_data_queue.get()
                    #print "transmit L2", self.tx_queue_item

                    #Create datalink packet
                    datalink_packet = self.create_datalink_packet(0xff, 0xff, self.datalink_payload)

                    #Frame datalink packet with byte escaping characters
                    framed_datalink_packet = self.Byte_Escape_Data_Fixed_Length(self.framing_startbyte, self.framing_stopbyte, self.framing_escapebyte, datalink_packet)

                    #Place datalink packet into transmit queue
                    self.tx_packet_queue.put(framed_datalink_packet)

            #Small sleep to unload python process resources from CPU
            time.sleep(0.01)

    def create_datalink_packet(self, packet_type, packet_config, payload):
        """
        This function creates a datalink packet from the provided data and packet information.
        """
        #Calculate payload length
        payload_len = len(payload)
        #Create header
        header = chr(packet_type) + chr(packet_config) + chr(payload_len)
        #Create footer
        footer = ''
        #Create datalink packet
        datalink_pkt = header + payload + footer
        #Return datalink packet
        return datalink_pkt

    def Fragment_Data(self, fragmentsize, data):  #INVALID?
        """
        This function breaks a provided "packet" into defined "chunks" of data of defined size.

        """
        #Clear self.fragment_data_list
        self.fragment_data_list = []
        #Break the data payload supplied into smaller "fragments"
        for i in range(0, len(data), fragmentsize):
            self.fragment_data_list.append(data[i:i + fragmentsize])

    def Add_Header_Footer(self, data_fragment_list):  # INVALID
        """
        This function adds header/footer info for fragmentation assembly.
        """
        #Footer contains a simple "CMD" byte that can be used to order the
        #fragmented data, flow control, etc...

        #Fragmentation Control - Identify start packet, data packets, and last packet
        #Start of data = 7
        #End of data = 8
        #Contents (non first or last data) = 0..6
        #Any packet can drop, data will resyn on new 7 (Start)
        # [START DATA, DATA..., DATA..., END DATA]
        data_fragment_list[0] = data_fragment_list[0] + chr(7)
        for i in range(1, len(data_fragment_list) - 2, 1):
            data_fragment_list[i] = data_fragment_list[i] + chr(i % 6)
        data_fragment_list[len(data_fragment_list) - 1] = data_fragment_list[len(data_fragment_list) - 1] + chr(8)

    def Encapsulate_Data(self, startbyte, stopbyte, escapebyte):  #INVALID
        """
        Byte framing routing for fragmented data packets. This is NO LONGER IMPLEMENTED.

        This function byte stuffs a simple encapsulation framing protocol around a provided data packet.
        Byte framing and escaping allows data to safely traverse the transmission medium with defined
        packet start and stop boundries for parsing.
        """
        #NOTE: FRAGMENTATION NO LONGER USED

        #Fragmentation Control - Identify start packet, data packets, and last packet
        #Start of data = 7
        #End of data = 8
        #Contents (non first or last data) = 0..6
        #Any packet can drop, data will resync on new 7 (Start)
        #[Payload Len, Data..., CMD Byte]
        # CMD =  [START DATA, DATA..., DATA..., END DATA]

        if(len(self.fragment_data_list) == 1):
            #First packet
            self.fragment_data_list[0] = chr(len(self.fragment_data_list[0])) + self.fragment_data_list[0] + chr(7)
            #Final Packet
            self.fragment_data_list.append(chr(0) + chr(8))  #SEND EMPTY PAYLOAD WITH END BYTE CMD

        elif(len(self.fragment_data_list) == 2):
            #First packet
            self.fragment_data_list[0] = chr(len(self.fragment_data_list[0])) + self.fragment_data_list[0] + chr(7)
            #Final Packet
            self.fragment_data_list[1] = chr(len(self.fragment_data_list[len(self.fragment_data_list) - 1])) + self.fragment_data_list[len(self.fragment_data_list) - 1] + chr(8)

        elif(len(self.fragment_data_list) > 2):
            #First packet
            self.fragment_data_list[0] = chr(len(self.fragment_data_list[0])) + self.fragment_data_list[0] + chr(7)
            #Content Packets
            for i in range(1, len(self.fragment_data_list) - 1, 1):
                self.fragment_data_list[i] = chr(len(self.fragment_data_list[i])) + self.fragment_data_list[i] + chr(i % 6)
            #Final Packet
            self.fragment_data_list[len(self.fragment_data_list) - 1] = chr(len(self.fragment_data_list[len(self.fragment_data_list) - 1])) + self.fragment_data_list[len(self.fragment_data_list) - 1] + chr(8)

        #Iterate through the fragmented data list and insert escape bytes for framing protocol
        for i in range(0, len(self.fragment_data_list), 1):
            #If escapebyte is located in the payload insert the escape byte prior (Escape must be first or it'll add more than needed)
            self.fragment_data_list[i] = self.fragment_data_list[i].replace(escapebyte, escapebyte + escapebyte)
            #If startbyte is located in the payload insert the escape byte prior
            self.fragment_data_list[i] = self.fragment_data_list[i].replace(startbyte, escapebyte + startbyte)
            #If stopbyte is located in the payload insert the escape byte prior
            self.fragment_data_list[i] = self.fragment_data_list[i].replace(stopbyte, escapebyte + stopbyte)
            #Insert start byte to the front of the payload
            self.fragment_data_list[i] = startbyte + self.fragment_data_list[i]
            #Insert stop byte to the end of the payload
            self.fragment_data_list[i] = self.fragment_data_list[i] + stopbyte
            self.tx_packet_queue.put(self.fragment_data_list[i])

    def Byte_Escape_Data_Fixed_Length(self, startbyte, stopbyte, escapebyte, packet):
        """
        This function byte stuffs a simple byte escape framing protocol around a provided data packet.
        Byte framing and escaping allows data to safely traverse the transmission medium with defined
        packet start and stop boundries for parsing.

        This function inputs a packet and returns a packet with escaped bytes per protocol inserted.
        """
        #If escapebyte is located in the payload insert the escape byte prior (Escape must be first or it'll add more than needed)
        packet = packet.replace(escapebyte, escapebyte + escapebyte)
        #If startbyte is located in the payload insert the escape byte prior
        packet = packet.replace(startbyte, escapebyte + startbyte)
        #If stopbyte is located in the payload insert the escape byte prior
        packet = packet.replace(stopbyte, escapebyte + stopbyte)
        #Insert start byte to the front of the payload
        packet = startbyte + packet
        #Insert stop byte to the end of the payload
        packet = packet + stopbyte
        return packet

    def Encapsulate_Data_CMD(self, startbyte, stopbyte, escapebyte, command):  #INVALID?

        #Fragmentation Control - Identify start packet, data packets, and last packet
        #Start of data = 7
        #End of data = 8
        #Contents (non first or last data) = 0..6
        #Any packet can drop, data will resync on new 7 (Start)
        #[Payload Len, Data..., CMD Byte]
        # CMD =  [START DATA, DATA..., DATA..., END DATA]
        #Clear self.fragment_data_list
        self.fragment_data_list = []
        self.fragment_data_list.append(chr(0))  #Dummy list write

        if(len(chr(command)) == 1):
            self.fragment_data_list.append(chr(0) + chr(command))  #SEND EMPTY PAYLOAD WITH END BYTE CMD

        else:
            return "ERROR - Command Attempt Length"

        #Iterate through the fragmented data list and insert escape bytes for framing protocol
        for i in range(0, len(self.fragment_data_list), 1):
            #If escapebyte is located in the payload insert the escape byte prior (Escape must be first or it'll add more than needed)
            self.fragment_data_list[i] = self.fragment_data_list[i].replace(escapebyte, escapebyte + escapebyte)
            #If startbyte is located in the payload insert the escape byte prior
            self.fragment_data_list[i] = self.fragment_data_list[i].replace(startbyte, escapebyte + startbyte)
            #If stopbyte is located in the payload insert the escape byte prior
            self.fragment_data_list[i] = self.fragment_data_list[i].replace(stopbyte, escapebyte + stopbyte)
            #Insert start byte to the front of the payload
            self.fragment_data_list[i] = startbyte + self.fragment_data_list[i]
            #Insert stop byte to the end of the payload
            self.fragment_data_list[i] = self.fragment_data_list[i] + stopbyte
            self.tx_packet_queue.put(self.fragment_data_list[i])


################################################################################
# Receiver_Datalink_Device_Class() CLASS
# Description: This class object provides the datalink layer SERVICES for the
#              receiver functionality.
#
# SERVICES Provided:
# - Check_Received_Data(): True if data is recieved and waiting for retrieval
# - Retrieve_Received_Data(): Returns the next (FIFO) recieved payload (after
#                             fragmentation reassembly) data.
################################################################################
class Receiver_Datalink_Device_Class(threading.Thread):
    ################################################################################
    # __init__()
    # Description: This function initializes the class and it's variables.
    # INPUTS: None
    ################################################################################
    def __init__(self, input_channel, serial_physical_obj):
        #Initialize class variables
        self.rx_packet_queue = Queue.Queue()
        self.rx_data_payload_queue = Queue.Queue()
        self.logic_startbyte_received = False
        self.logic_escapebyte_received = False
        self.logic_stopbyte_received = False
        self.receiver_class = Receiver_Datalink_Device_State_Parser_Class(input_channel, serial_physical_obj)
        self.enable_flag = True
        self.max_payload_size = 6
        self.datalink_packet_format = 'c' + str(self.max_payload_size) + 'c' + 'c'
        self.reconstruct_data = ''
        self.timer_interval = 5
        self.timer = threading.Timer(self.timer_interval, self.timer_trip)
        self.datalink_packet_struct = struct.Struct('BBB125s')

        #Start
        threading.Thread.__init__(self)
        self.start()  #Starts the run() function and thread

    def timer_trip(self):
        #At periodic intervals transmit a "ready for data" packet to ensure the TX
        #device knows this receiver is ready.
        #test_ser_queue_2.put("trip!")
        self.timer = threading.Timer(self.timer_interval, self.timer_trip)
        self.timer.start()

    ################################################################################
    # abort()
    # Description: This function performs the actions needed to .
    # INPUTS: None
    ################################################################################
    def Abort(self):
        self.enable_flag = False
        print "Aborting Layer 2 Protocol!"

##    def Parse_Datalink_Packet_Variable_Len(self, packet):
##        header = struct.unpack('c', packet[0:1])
##        payload_len = int(header[0].encode('hex'), 16)
##        packet_parsed = struct.unpack('c' + str(payload_len) + 's' + 'c', packet)
##        return packet_parsed

    def IsEmpty(self):
        """
        Returns True if recevier FIFO empty. Returns False if there is one or more items in the FIFO.
        """
        return self.rx_data_payload_queue.empty()

    def GET(self):
        """
        Returns the next item in the recevier FIFO. Items returned will be parse layer 2 datagram packets. Returns False if no items in the FIFO to return
        """
        if not self.rx_data_payload_queue.empty():
            return self.rx_data_payload_queue.get()
        else:
            return False

    def run(self):
        while self.enable_flag:
            time.sleep(0.01)
            if not self.receiver_class.rx_packet_queue.empty():
                #  Loop through all known queue data and receive
                for i in range(0, self.receiver_class.rx_packet_queue.qsize()):
                    data = self.receiver_class.rx_packet_queue.get()
                    try:
                        unpacked_datalink = self.datalink_packet_struct.unpack(data)
                        #Place datalink payload into payload queue
                        self.rx_data_payload_queue.put(unpacked_datalink[3])
                    except:
                        print "FAIL"
                        pass  #print "Failed parsing" !!!!!FIX!!!!!


################################################################################
# Receiver_Datalink_Device_State_Parser_Class() CLASS
# Description: This class object provides the lower level functionality to create
#              the services provided. This additional class member allows for a
#              specific thread to be created that constantly loops through a
#              byte frame parsing state machine as each byte of the potential
#              datalink layer frame is received. The state machine de-frames,
#              re-assembles, and completes addition low level actions for the
#              receiver service(s).
################################################################################
class Receiver_Datalink_Device_State_Parser_Class(threading.Thread):
    ################################################################################
    # __init__()
    # Description: This function initializes the class and it's variables.
    # INPUTS: None
    ################################################################################
    def __init__(self, input_channel, serial_physical_obj):
        #Initialize class variables
        self.rx_packet_queue = Queue.Queue()
        self.enable_flag = True  #Class flag to keep loop running when True, aborts when False
        self.encapsulate_startbyte = chr(0x7b)  #Ensure these are the same as the self.insert_data_class escapes!
        self.encapsulate_stopbyte = chr(0x7c)  #Ensure these are the same as the self.insert_data_class escapes!
        self.encapsulate_escapebyte = chr(0x7d)  #Ensure these are the same as the self.insert_data_class escapes!
        self.partial_packet = ''
        self.logic_startbyte_received = False
        self.logic_escapebyte_received = False
        self.logic_stopbyte_received = False
        self.input_channel = input_channel
        self.serial_physical_obj = serial_physical_obj
        #global serial_physical_obj

        #Start
        threading.Thread.__init__(self)
        self.start()  #Starts the run() function and thread

    ################################################################################
    # abort()
    # Description: This function performs the actions needed to .
    # INPUTS: None
    ################################################################################
    def abort(self):
        self.enable_flag = False
        print "Aborting Layer 2 Protocol!"

    def run(self):
        while self.enable_flag:
            time.sleep(0.01)
            if not self.serial_physical_obj.serial_physical_obj.serial_rx_queue.empty():
                rx_byte_raw = self.serial_physical_obj.serial_physical_obj.get_byte()
                #Get next byte
                for i in range(0, len(rx_byte_raw), 1):
                    rx_byte = rx_byte_raw[i]
                    #PARSE BYTES
                    #Check PACKET STARTED Flag = FALSE (Packet NOT already started)
                    if not self.logic_startbyte_received:
                        #Received byte is start byte - New Packet!
                        if (rx_byte == self.encapsulate_startbyte):
                            self.logic_startbyte_received = True
                            self.partial_packet = ''  #Clear partial packet contents for new packet
                        #Noise or curruption data, skip.
                        else:
                            pass
                    #Check PACKET STARTED Flag = True (Packet already started and being recieved)
                    elif self.logic_startbyte_received:
                        #Check if current BYTE is being escaped (framing) - FALSE
                        if not self.logic_escapebyte_received:
                            #Non-Escaped DATA BYTE received
                            if ((rx_byte != self.encapsulate_escapebyte) and (rx_byte != self.encapsulate_startbyte) and (rx_byte != self.encapsulate_stopbyte)):
                                self.partial_packet += rx_byte
                            #Escape byte received
                            elif(rx_byte == self.encapsulate_escapebyte):
                                self.logic_escapebyte_received = True
                            #Stop byte received
                            elif(rx_byte == self.encapsulate_stopbyte):
                                self.logic_startbyte_received = False
                                self.rx_packet_queue.put(self.partial_packet)
                            #Received byte is start byte - Current packet is currupted and found next packet header (potentially)!
                            elif (rx_byte == self.encapsulate_startbyte):
                                self.logic_startbyte_received = True
                                self.partial_packet = ''  #Clear partial packet contents for new packet
                            #Unknown State - Error
                            else:
                                print"ERROR:", self.partial_packet
                        #Check if current BYTE is being escaped (framing) - TRUE
                        elif self.logic_escapebyte_received:
                            #Escaped Packet data received
                            if ((rx_byte == self.encapsulate_escapebyte) or (rx_byte == self.encapsulate_startbyte) or (rx_byte == self.encapsulate_stopbyte)):
                                self.logic_escapebyte_received = False
                                self.partial_packet += rx_byte
                            #Unknown State - Error
                            else:
                                print"ERROR:", self.partial_packet
                    #Unknown State - Error
                    else:
                        print"ERROR:", self.partial_packet
            #No new databyte to parse
            else:
                    pass  #No new data

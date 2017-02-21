import os
import faraday_msg
import ConfigParser

#Open configuration INI
config = ConfigParser.RawConfigParser()
filename = os.path.abspath("configuration.ini")
config.read(filename)

#Definitions

#Variables
transmitter_device_callsign = config.get("DEVICES", "UNIT0CALL") # Should match the connected Faraday unit as assigned in Proxy configuration
transmitter_device_node_id = config.getint("DEVICES", "UNIT0ID") # Should match the connected Faraday unit as assigned in Proxy configuration
transmitter_device_callsign = str(transmitter_device_callsign).upper()
receiver_device_callsign = config.get("DEVICES", "UNIT1CALL") # Should match the programmed callsign of the remote Faraday device to be commanded (receive)
receiver_device_node_id = config.getint("DEVICES", "UNIT1ID") # Should match the programmed callsign of the remote Faraday device to be commanded (receive)
receiver_device_callsign = str(receiver_device_callsign).upper()

#Set constants
rx_uart_service_port_application_number = 3
GETWAIT_TIMEOUT = 2

# Create receiver application object
faraday_rx_msg_object = faraday_msg.MessageAppRx(receiver_device_callsign, receiver_device_node_id)

#Print debug information about proxy port listening
print "Receiver (Proxy):", receiver_device_callsign + '-' + str(receiver_device_node_id)
print "\n"

# Loop continuously through the faraday experimental RF command message application RX routine
while 1:
    rx_message_dict = faraday_rx_msg_object.rxmsgloop(receiver_device_callsign, receiver_device_node_id, rx_uart_service_port_application_number, GETWAIT_TIMEOUT)
    if rx_message_dict != None:
        print '***************************************'
        print "FROM:", rx_message_dict['source_callsign']
        print '\n'
        print rx_message_dict['message']
        print '\n***************************************'
        rx_message_dict = None
    else:
        pass # No messages received

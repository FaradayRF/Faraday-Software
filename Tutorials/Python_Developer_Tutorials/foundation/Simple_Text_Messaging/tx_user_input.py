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


# Create messaging application objects needed for transmissions
faraday_tx_msg_sm = faraday_msg.MsgStateMachineTx()  # Transmit state machine object used to fragment data
faraday_tx_msg_object = faraday_msg.MessageAppTx(transmitter_device_callsign, transmitter_device_node_id, receiver_device_callsign, receiver_device_node_id)  # Transmit object from the Faraday MSG application module

# Update destination Callsign and ID for transmission addressing purposes
faraday_tx_msg_object.updatedestinationstation(receiver_device_callsign, receiver_device_node_id)

# Create message global variable
message = ''

# Loop while waiting for user input text to transmit
while 1:
    # Get user input text
    message = raw_input("Transmit Message: ")

    # Create start, stop, and data packets (fragmented) from user input data using state machine tool
    faraday_tx_msg_sm.createmsgpackets(transmitter_device_callsign, transmitter_device_node_id, message)

    print "Packet Fragments Created:"

    # Iterate through list of packets and transmit each
    for i in range(0, len(faraday_tx_msg_sm.list_packets), 1):
        print 'Fragment', i, faraday_tx_msg_sm.list_packets[i]
        faraday_tx_msg_object.transmitframe(faraday_tx_msg_sm.list_packets[i])
    print "\n"





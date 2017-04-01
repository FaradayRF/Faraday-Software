import faraday_msg
import ConfigParser

# Load configuration from transmitter INI file
transmitter_config = ConfigParser.RawConfigParser()
transmitter_config.read('transmiter_configuration.ini')

#Variables
local_device_callsign = transmitter_config.get("local", "callsign")  # Callsign of the local unit to connect to (COM port assignment)
local_device_node_id = transmitter_config.getint("local", "id")  # Callsign ID of the local unit to connect to (COM port assignment)
remote_device_callsign = transmitter_config.get("remote", "callsign")  # Callsign of the local unit to connect to (COM port assignment)
remote_device_node_id = transmitter_config.getint("remote", "id")  # Callsign ID of the local unit to connect to (COM port assignment)

# Create messaging application objects needed for transmissions
faraday_tx_msg_sm = faraday_msg.MsgStateMachineTx()  # Transmit state machine object used to fragment data
faraday_tx_msg_object = faraday_msg.MessageAppTx(local_device_callsign, local_device_node_id, remote_device_callsign, remote_device_node_id)  # Transmit object from the Faraday MSG application module

# Update destination Callsign and ID for transmission addressing purposes
faraday_tx_msg_object.updatedestinationstation(remote_device_callsign, remote_device_node_id)

# Create message global variable
message = ''

# Loop while waiting for user input text to transmit
while 1:
    # Get user input text
    message = raw_input("Message: ")

    # Create start, stop, and data packets (fragmented) from user input data using state machine tool
    faraday_tx_msg_sm.createmsgpackets(local_device_callsign, local_device_node_id, message)

    # Iterate through list of packets and transmit each
    for i in range(0, len(faraday_tx_msg_sm.list_packets), 1):
        print 'TX', i, faraday_tx_msg_sm.list_packets[i]
        faraday_tx_msg_object.transmitframe(faraday_tx_msg_sm.list_packets[i])

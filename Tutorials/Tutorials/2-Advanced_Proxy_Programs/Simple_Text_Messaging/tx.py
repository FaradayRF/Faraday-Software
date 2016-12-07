import faraday_msg
import ConfigParser

# Load configuration from transmitter INI file
transmitter_config = ConfigParser.RawConfigParser()
transmitter_config.read('transmiter_configuration.ini')

#Variables
local_device_callsign = transmitter_config.get("local", "callsign")  # Callsign of the local unit to connect to (COM port assignment)
local_device_node_id = transmitter_config.getint("local", "id")  # Callsign ID of the local unit to connect to (COM port assignment)

remote_device_callsign = transmitter_config.get("remote", "callsign")  # Callsign of the remote unit to address RF packets too
remote_device_node_id = transmitter_config.getint("remote", "id")  # Callsign ID of the local unit to address RF packets too

# Create messaging application objects needed for transmissions
faraday_tx_msg_sm = faraday_msg.MsgStateMachineTx()  # Transmit state machine object used to fragment data
faraday_tx_msg_object = faraday_msg.MessageAppTx(local_device_callsign, local_device_node_id, remote_device_callsign, remote_device_node_id)  # Transmit object from the Faraday MSG application module

# Update destination callsign (not needed but here for example)
faraday_tx_msg_object.updatedestinationstation(remote_device_callsign, remote_device_node_id)

# Create message to transmit
message = 'This is a test of a very long message that will be fragmented and reassembled!'

# Create message fragments
faraday_tx_msg_sm.createmsgpackets(local_device_callsign, local_device_node_id, message)

#Iterate through start, stop, and data fragment packets and transmit
for i in range(0, len(faraday_tx_msg_sm.list_packets), 1):
    print "TX:", repr(faraday_tx_msg_sm.list_packets[i])
    faraday_tx_msg_object.transmitframe(faraday_tx_msg_sm.list_packets[i])



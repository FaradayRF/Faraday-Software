import faraday_msg

#Variables
local_device_callsign = 'kb1lqd'  # Callsign of the local unit to connect to (COM port assignment)
local_device_node_id = 1  # Callsign ID of the local unit to connect to (COM port assignment)

#Remote device information
remote_callsign = 'kb1lqd'  # Callsign of the remote unit to transmit to
remote_id = 2  # Callsign ID of the remote unit to connect to transmit to

# Create messaging application objects needed for transmissions
faraday_tx_msg_sm = faraday_msg.MsgStateMachineTx()  # Transmit state machine object used to fragment data
faraday_tx_msg_object = faraday_msg.MessageAppTx(local_device_callsign, local_device_node_id, remote_callsign, remote_id)  # Transmit object from the Faraday MSG application module

# Update destination callsign (not needed but here for example)
faraday_tx_msg_object.updatedestinationstation(remote_callsign, remote_id)

# Create message to transmit
message = '0123456789'*25

# Create message fragments
faraday_tx_msg_sm.createmsgpackets('kb1lqd', 1, message)

#Iterate through start, stop, and data fragment packets and transmit
for i in range(0, len(faraday_tx_msg_sm.list_packets), 1):
    print "TX:", repr(faraday_tx_msg_sm.list_packets[i])
    faraday_tx_msg_object.transmitframe(faraday_tx_msg_sm.list_packets[i])



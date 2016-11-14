import faraday_msg

#Variables
local_device_callsign = 'kb1lqc'
local_device_node_id = 1

#Remote device information
remote_callsign = 'kb1lqd'
remote_id = 1

# Create messaging application objects needed for transmissions
faraday_tx_msg_sm = faraday_msg.Msg_State_Machine_Tx()  # Transmit state machine object used to fragment data
faraday_tx_msg_object = faraday_msg.message_app_Tx(local_device_callsign, local_device_node_id, remote_callsign, remote_id)  # Transmit object from the Faraday MSG application module

# Update destination callsign (not needed but here for example)
faraday_tx_msg_object.UpdateDestinationStation(remote_callsign, remote_id)

# Create message to transmit
message = '0123456789'*25

# Create message fragments
faraday_tx_msg_sm.CreateMsgPackets('kb1lqd', 1, message)

#Iterate through start, stop, and data fragment packets and transmit
for i in range(0, len(faraday_tx_msg_sm.list_packets), 1):
    faraday_tx_msg_object.TransmitFrame(faraday_tx_msg_sm.list_packets[i])



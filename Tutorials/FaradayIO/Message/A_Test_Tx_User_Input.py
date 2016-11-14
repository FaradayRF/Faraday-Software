import faraday_msg


#Variables
local_device_callsign = 'kb1lqc'# Callsign of the local unit to connect to (COM port assignment)
local_device_node_id = 1  # Callsign ID of the local unit to connect to (COM port assignment)

#Remote device information
remote_callsign = 'kb1lqd'  # Callsign of the remote unit to transmit to
remote_id = 1  # Callsign ID of the remote unit to connect to transmit to

# Create messaging application objects needed for transmissions
faraday_tx_msg_sm = faraday_msg.Msg_State_Machine_Tx()  # Transmit state machine object used to fragment data
faraday_tx_msg_object = faraday_msg.message_app_Tx(local_device_callsign, local_device_node_id, remote_callsign, remote_id)  # Transmit object from the Faraday MSG application module

# Update destination Callsign and ID for transmission addressing purposes
faraday_tx_msg_object.UpdateDestinationStation(remote_callsign, remote_id)

# Create message global variable
message = ''

# Loop while waiting for user input text to transmit
while 1:
    # Get user input text
    message = raw_input("Message: ")

    # Create start, stop, and data packets (fragmented) from user input data using state machine tool
    faraday_tx_msg_sm.CreateMsgPackets(local_device_callsign, local_device_node_id, message)

    # Iterate through list of packets and transmit each
    for i in range(0, len(faraday_tx_msg_sm.list_packets), 1):
        print 'TX', i, faraday_tx_msg_sm.list_packets[i]
        faraday_tx_msg_object.TransmitFrame(faraday_tx_msg_sm.list_packets[i])





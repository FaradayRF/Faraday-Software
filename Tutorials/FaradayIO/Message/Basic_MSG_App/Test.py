import faraday_msg
faraday_msg_sm = faraday_msg.Msg_State_Machine_Tx()
faraday_msg_object = faraday_msg.message_app()

faraday_msg_object.UpdateDestinationStation('KB1LQC', 1)
message = 'This is a test of very long messages that should be longer than a single packet!'
faraday_msg_sm.CreateMsgPackets('kb1lqd', 7, message)

for i in range(0, len(faraday_msg_sm.list_packets), 1):
    faraday_msg_object.TransmitFrame(faraday_msg_sm.list_packets[i])
    #print repr(faraday_msg_sm.list_packets[i])

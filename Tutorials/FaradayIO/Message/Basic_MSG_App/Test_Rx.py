from FaradayIO import faradaybasicproxyio
import faraday_msg

faraday_rx_msg_object = faraday_msg.message_app_Rx()
faraday_rx_msg_sm = faraday_msg.Msg_State_Machine_Tx()
faraday_io = faradaybasicproxyio.proxyio(80)




while(1):
    faraday_rx_msg_object.RxMsgLoop()
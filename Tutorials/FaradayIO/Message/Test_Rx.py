
import faraday_msg
import sys
import time

#sys.path.append(os.path.join(os.path.dirname(__file__), "../../")) #Append path to common tutorial FaradayIO module
#from FaradayIO import faradaybasicproxyio

faraday_rx_msg_object = faraday_msg.message_app_Rx()
#faraday_rx_msg_sm = faraday_msg.Msg_State_Machine_Tx()
#faraday_io = faradaybasicproxyio.proxyio()

while 1:
    faraday_rx_msg_object.RxMsgLoop()

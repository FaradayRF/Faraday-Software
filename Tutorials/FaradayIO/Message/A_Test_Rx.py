
import faraday_msg
import sys
import time

#sys.path.append(os.path.join(os.path.dirname(__file__), "../../")) #Append path to common tutorial FaradayIO module
#from FaradayIO import faradaybasicproxyio

#Variables
local_device_callsign = 'kb1lqc'
local_device_node_id = 1
uart_service_port_application_number = 3
GETWAIT_TIMEOUT = 2

faraday_rx_msg_object = faraday_msg.message_app_Rx()
#faraday_rx_msg_sm = faraday_msg.Msg_State_Machine_Tx()
#faraday_io = faradaybasicproxyio.proxyio()

while 1:
    faraday_rx_msg_object.RxMsgLoop(local_device_callsign, local_device_node_id, uart_service_port_application_number, GETWAIT_TIMEOUT)

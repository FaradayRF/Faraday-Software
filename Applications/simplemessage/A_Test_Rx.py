
import faraday_msg

#sys.path.append(os.path.join(os.path.dirname(__file__), "../../")) #Append path to common tutorial FaradayIO module
#from FaradayIO import faradaybasicproxyio

#Variables
local_device_callsign = 'kb1lqc'  # Callsign of the local unit to connect to (COM port assignment)
local_device_node_id = 1  # Callsign ID of the local unit to connect to (COM port assignment)
uart_service_port_application_number = 3
GETWAIT_TIMEOUT = 2

# Create receiver application object
faraday_rx_msg_object = faraday_msg.MessageAppRx()

# Loop continuously through the faraday experimental RF command message application RX routine
while 1:
    rx_message_dict = faraday_rx_msg_object.rxmsgloop(local_device_callsign, local_device_node_id, uart_service_port_application_number, GETWAIT_TIMEOUT)
    if rx_message_dict is not None:
        print '***************************************'
        print "FROM:", rx_message_dict['source_callsign']
        print '\n'
        print rx_message_dict['message']
        print '\n***************************************'
        rx_message_dict = None
    else:
        pass  # No messages received

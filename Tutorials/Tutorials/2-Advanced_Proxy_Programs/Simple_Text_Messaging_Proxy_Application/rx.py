import faraday_msg
import ConfigParser
import threading
import time
import Queue

# Load configuration from receiver INI file
receiver_config = ConfigParser.RawConfigParser()
receiver_config.read('receiver_configuration.ini')

#Variables
local_device_callsign = receiver_config.get("local", "callsign")  # Callsign of the local unit to connect to (COM port assignment)
local_device_node_id = receiver_config.getint("local", "id")  # Callsign ID of the local unit to connect to (COM port assignment)

#Set constants
rx_uart_service_port_application_number = 3
GETWAIT_TIMEOUT = 0.5

# Create receiver application object
faraday_rx_msg_object = faraday_msg.MessageAppRx()

# Print initialization completed message
print "Faraday Simple Messaging Receiver Started!"
class receiver(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.fifo = Queue.Queue(0)
        return

    def run(self):
        # Loop continuously through the faraday experimental RF command message application RX routine
        while 1:
            #print "RX'ing"
            rx_message_dict = faraday_rx_msg_object.rxmsgloop(local_device_callsign, local_device_node_id, rx_uart_service_port_application_number, GETWAIT_TIMEOUT)
            if rx_message_dict != None:
                print '***************************************'
                print "FROM:", rx_message_dict['source_callsign']
                print '\n'
                print rx_message_dict['message']
                print '\n***************************************'
                self.fifo.put_nowait(rx_message_dict)
                print "Queue:", self.fifo.qsize()
                rx_message_dict = None
            else:
                pass # No messages received

test = receiver()
t = receiver()
t.start()
import faraday_msg
import ConfigParser
import threading
import Queue

# Load configuration from transmitter INI file
transmitter_config = ConfigParser.RawConfigParser()
transmitter_config.read('configuration.ini')


class transmit_object(object):
    def __init__(self, local_device_callsign, local_device_node_id):
        self.local_device_callsign = local_device_callsign
        self.local_device_node_id = local_device_node_id
        # Create messaging application objects needed for transmissions
        self.faraday_tx_msg_sm = faraday_msg.MsgStateMachineTx()  # Transmit state machine object used to fragment data
        self.faraday_tx_msg_object = faraday_msg.MessageAppTx(self.local_device_callsign, self.local_device_node_id)  # Transmit object from the Faraday MSG application module
        # Create receiver application object
        self.faraday_rx_msg_object = faraday_msg.MessageAppRx()
        self.rx_uart_service_port_application_number = 3
        self.GETWAIT_TIMEOUT = 2

    def send(self, dest_callsign, dest_id, payload):
        # Create message fragments
        self.faraday_tx_msg_sm.createmsgpackets(self.local_device_callsign, self.local_device_node_id, payload)

        #Iterate through start, stop, and data fragment packets and transmit
        for i in range(0, len(self.faraday_tx_msg_sm.list_packets), 1):
            #print "TX:", repr(self.faraday_tx_msg_sm.list_packets[i])
            self.faraday_tx_msg_object.transmitframe(self.faraday_tx_msg_sm.list_packets[i], dest_callsign, dest_id)


class receive_object(threading.Thread):
    def __init__(self, local_device_callsign, local_device_node_id):
        self.local_device_callsign = local_device_callsign
        self.local_device_node_id = local_device_node_id
        # Set constants
        self.rx_uart_service_port_application_number = 3
        self.GETWAIT_TIMEOUT = 0.5

        # Create receiver application object
        self.faraday_rx_msg_object = faraday_msg.MessageAppRx()
        threading.Thread.__init__(self)
        self.fifo = Queue.Queue(0)
        return

    def run(self):
        # Loop continuously through the faraday experimental RF command message application RX routine
        while 1:
            rx_message_dict = self.faraday_rx_msg_object.rxmsgloop(self.local_device_callsign, self.local_device_node_id, self.rx_uart_service_port_application_number, self.GETWAIT_TIMEOUT)
            if rx_message_dict != None:
                self.fifo.put(rx_message_dict)
                rx_message_dict = None
            else:
                pass # No messages received

    def GetQueueSize(self):
        return self.fifo.qsize()

    def GetQueueItem(self):
        return self.fifo.get_nowait()



class message_object(object):
    def __init__(self, local_device_callsign, local_device_node_id):
        self.transmit = transmit_object(local_device_callsign, local_device_node_id)
        self.receive = receive_object(local_device_callsign, local_device_node_id)
        self.receive.start()
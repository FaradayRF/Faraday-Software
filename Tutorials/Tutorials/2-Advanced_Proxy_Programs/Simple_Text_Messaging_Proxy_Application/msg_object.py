import faraday_msg
import threading
import Queue


class TransmitObject(object):
    """
    This is the receiver object that provided receive function interface and buffering.

    :param local_device_callsign: The callsign of the proxy assigned local Faraday device to connect to
    :param local_device_node_id: The callsign ID number of the proxy assigned local Faraday device to connect to
    """
    def __init__(self, local_device_callsign, local_device_node_id):
        self.local_device_callsign = local_device_callsign
        self.local_device_node_id = local_device_node_id
        # Create messaging application objects needed for transmissions
        self.faraday_tx_msg_sm = faraday_msg.MsgStateMachineTx()
        self.faraday_tx_msg_object = faraday_msg.MessageAppTx(self.local_device_callsign,
                                                              self.local_device_node_id)
        # Create receiver application object
        self.faraday_rx_msg_object = faraday_msg.MessageAppRx()
        self.rx_uart_service_port_application_number = 3
        self.GETWAIT_TIMEOUT = 2

    def send(self, dest_callsign, dest_id, payload):
        """
        This function transmits a supplied function argument message (text/binary) to the intended remote Faraday
        unit.

        :param dest_callsign: The callsign of the remote Faraday unit to address the transmission to
        :param dest_id: The callsign ID number of the remote Faraday unit to address the transmission to
        :param payload: The data (text/binary) to send to the remote Faraday unit

        """
        # Create message fragments
        self.faraday_tx_msg_sm.createmsgpackets(self.local_device_callsign, self.local_device_node_id, payload)

        # Iterate through start, stop, and data fragment packets and transmit
        for i in range(0, len(self.faraday_tx_msg_sm.list_packets), 1):
            # print "TX:", repr(self.faraday_tx_msg_sm.list_packets[i])
            self.faraday_tx_msg_object.transmitframe(self.faraday_tx_msg_sm.list_packets[i], dest_callsign, dest_id)


class ReceiveObject(threading.Thread):
    """
    This is the receiver object that provided receive function interface and buffering.

    :param local_device_callsign: The callsign of the proxy assigned local Faraday device to connect to
    :param local_device_node_id: The callsign ID number of the proxy assigned local Faraday device to connect to
    """
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
        """
            This is the main threaded loop that the receiver program runs to obtain new received data packets from
            the proxy interface. Received data packets are saved in to FIFO for later retrieval.
            """
        # Loop continuously through the faraday experimental RF command message application RX routine
        while 1:
            rx_message_dict = self.faraday_rx_msg_object.rxmsgloop(self.local_device_callsign,
                                                                   self.local_device_node_id,
                                                                   self.rx_uart_service_port_application_number,
                                                                   self.GETWAIT_TIMEOUT)
            if rx_message_dict is not None:
                self.fifo.put(rx_message_dict)
                rx_message_dict = None
            else:
                pass  # No messages received

    def getqueuesize(self):
        """
        This function returns the estimated number of data packets that have been received and are able to be
        retrieved from the receive FIFO.

        :returns self.fifo.qsize()

        """
        return self.fifo.qsize()

    def getqueueitem(self):
        """
        This function returns the next data item from the receiver FIFO. If no items are available the function will
        return False.

        :returns self.fifo.get_nowait()

        """
        return self.fifo.get_nowait()


class MessageObject(object):
    """
    This object is used to create a single transmit/receive object for a single connected proxy Faraday device.
    """
    def __init__(self, local_device_callsign, local_device_node_id):
        self.transmit = transmit_object(local_device_callsign, local_device_node_id)
        self.receive = receive_object(local_device_callsign, local_device_node_id)
        self.receive.start()

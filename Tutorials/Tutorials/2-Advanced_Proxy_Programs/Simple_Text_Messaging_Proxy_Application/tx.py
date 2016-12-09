import faraday_msg
import ConfigParser

# Load configuration from transmitter INI file
transmitter_config = ConfigParser.RawConfigParser()
transmitter_config.read('configuration.ini')

#Variables
local_device_callsign = transmitter_config.get("local", "callsign")  # Callsign of the local unit to connect to (COM port assignment)
local_device_node_id = transmitter_config.getint("local", "id")  # Callsign ID of the local unit to connect to (COM port assignment)



class transmit_object(object):
    def __init__(self, local_device_callsign, local_device_node_id,):
        # Create messaging application objects needed for transmissions
        self.faraday_tx_msg_sm = faraday_msg.MsgStateMachineTx()  # Transmit state machine object used to fragment data
        self.faraday_tx_msg_object = faraday_msg.MessageAppTx(local_device_callsign, local_device_node_id)  # Transmit object from the Faraday MSG application module

    def send(self, dest_callsign, dest_id, payload):
        # Create message fragments
        self.faraday_tx_msg_sm.createmsgpackets(local_device_callsign, local_device_node_id, payload)

        #Iterate through start, stop, and data fragment packets and transmit
        for i in range(0, len(self.faraday_tx_msg_sm.list_packets), 1):
            print "TX:", repr(self.faraday_tx_msg_sm.list_packets[i])
            self.faraday_tx_msg_object.transmitframe(self.faraday_tx_msg_sm.list_packets[i], dest_callsign, dest_id)



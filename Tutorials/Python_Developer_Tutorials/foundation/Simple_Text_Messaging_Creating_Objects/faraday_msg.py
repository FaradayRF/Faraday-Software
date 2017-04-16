# imports
import struct
import sys
import os

# Add Faraday library to the Python path.
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

# Imports - Faraday Specific
from faraday.proxyio import faradaybasicproxyio
from faraday.proxyio import faradaycommands


class MsgStateMachineTx(object):
    def __init__(self):
        """
        A state machine that handles the functionality needed to create and transmit a message
        """
        # Constants
        self.MAX_PAYLOAD_LENGTH = 40  # TBD
        self.MAX_MSG_DATA_LENGTH = 38  # TDB
        # States
        self.STATE_IDLE = 0
        self.STATE_INIT = 1
        self.STATE_FRAGMENT = 2
        self.STATE_TX = 3
        # Frame Types
        self.MSG_START = 255
        self.MSG_DATA = 254
        self.MSG_END = 253
        # Variables
        self.list_packets = []
        # Frame Definitions
        self.pkt_datagram_frame = struct.Struct('1B 40s')  # Fixed
        self.pkt_start = struct.Struct('9s 3B')  # Fixed
        self.pkt_data = struct.Struct('2B 38s')  # Variable  Data Length
        self.pkt_end = struct.Struct('1B')  # Fixed

    def fragmentcount(self, msg_len):
        """
        This function calculations the number of fragmentation "chucks" or packets will be needed to break the supplied
        message length into smaller fragmented pieces. If a message length smaller than a single packet is supplied
        then the fragmentation count will be 0. The fragementation byte count is determined by the
        self.MAX_MSG_DATA_LENGTH class variable.

        :param msg_len: The length of the packet to be fragmented

        :returns Number of fragmentation packets calculated to be needed to break the message length into the
        predetermined sized "chunks"
        """
        # Determine fragment count
        frag_cnt = msg_len / self.MAX_MSG_DATA_LENGTH
        if msg_len % self.MAX_MSG_DATA_LENGTH > 0:
            frag_cnt += 1
        return frag_cnt

    def fragmentmsg(self, msg):
        """
        This function fragments the supplied message into smaller packets or "chunks" that will fit into the
        pre-determined MTU (maximum transmissible unit) of the packet's path. Using an algorithm these fragments can
        be reassembled after reception.

        :param msg: The data to be fragmented

        :returns A list containing the fragemented "chunks" of data of the pre-determined size.
        """
        list_message_fragments = [msg[i:i + self.MAX_MSG_DATA_LENGTH] for i in
                                  range(0, len(msg), self.MAX_MSG_DATA_LENGTH)]
        #for item in list_message_fragments:
        #    print item, "Frag Length", len(item)
        #print repr(list_message_fragments)
        return list_message_fragments

    def createmsgpackets(self, src_call, src_id, msg):
        """
        This function is the high level fragmentation creation function that accepts a message/data and a source
        callsign/ID. The source callsign/ID is used in the START packet to easily tell the receive program who sent
        the message.

        :param src_call: Source device callsign
        :param src_id: Source device callsign ID number
        :param msg: Message/data to be transmitted to the receiving device (will be fragmented)

        """
        # Ensure callsign and ID are formatted correctly
        src_call = str(src_call).upper()
        src_id = int(src_id)

        # Create START Packet
        msg_start = self.createstartframe(src_call, src_id, len(msg))
        msg_start = self.pkt_datagram_frame.pack(self.MSG_START, msg_start)

        # Create END Packet
        msg_end = self.createendframe(len(msg))
        msg_end = self.pkt_datagram_frame.pack(self.MSG_END, msg_end)

        # Create DATA Packet(s)
        list_msg_fragments = self.fragmentmsg(msg)
        list_data_packets = []

        del list_data_packets[:]  # Remove all old indexes

        for i in range(0, len(list_msg_fragments), 1):
            data_packet = self.createdataframe(i, list_msg_fragments[i])
            #print "Pre-Pack:", repr(data_packet), len(data_packet)
            data_packet = self.pkt_datagram_frame.pack(self.MSG_DATA, data_packet)
            #print "Post-Pack:", repr(data_packet), len(data_packet)
            list_data_packets.append(data_packet)

        # Insert all packets into final packet list in order of transmission
        self.list_packets = []  # Reset any old packet fragments
        del self.list_packets[:]  # Remove all old indexes
        self.list_packets.append(msg_start)
        for i in range(0, len(list_data_packets), 1):
            self.list_packets.append(list_data_packets[i])
        self.list_packets.append(msg_end)

    def createstartframe(self, src_call, src_id, msg_len):
        """
        This function creates a START packet (frame) that resets the receivers state machine to prepare for a new message. In
        the START frame information about the message/data is stored.

        :param src_call: Source device callsign
        :param src_id: Source device callsign ID number
        :param msg_len: Length in bytes of the full Message/data to be transmitted to the receiving device

        :returns A START packet
        """
        # Calculate the number of fragmented packets
        frag_cnt = self.fragmentcount(msg_len)
        #print frag_cnt
        # Create packet
        packet = self.pkt_start.pack(src_call, len(src_call), src_id, frag_cnt)
        # Return packet created
        return packet

    def createdataframe(self, sequence, data):
        """
        This function creates a DATA packet (frame) that contains the main data/message to be reassembled at the
        receiver. This is fragmented packets of the main data/message being transmitted.

        :param sequence: The sequence number of the packet. This is used to re-order the original message fragments
        after reception.
        :param data: The data to be encapsulated in the data fragment packet.

        :returns A DATA packet
        """
        #print "create:", repr(data), len(data)
        packet = self.pkt_data.pack(sequence, len(data), data)
        #print "created:", repr(packet), len(packet)
        return packet

    def createendframe(self, msg_len):
        """
        This function creates an END packet (frame) that indicates to the receiver device that the end of the fragment
        packets has occurred and it is safe to reassemble the original data/message. The END packet can contain
        information about the the prior packets/data if needed.

        :param msg_len: TThe length of the full data/message in bytes that was transmitted.

        :returns An END packet
        """
        frag_cnt = self.fragmentcount(msg_len)
        packet = self.pkt_end.pack(frag_cnt)
        return packet


class MessageAppTx(object):
    def __init__(self, local_callsign, local_callsign_id):
        """
        The message application object contains all the functions, definitions, and state machines needed to implement
        a bare-bones text message application using the Faraday command application "experimental RF Packet
        Forward" functionality."
        """
        # Identification Variables
        self.local_device_callsign = str(local_callsign).upper()
        self.local_device_node_id = int(local_callsign_id)
        self.remote_callsign = ''  #str(destination_callsign).upper()
        self.remote_id = 0  #int(destination_id)

        # Initialize objects
        self.faraday_1 = faradaybasicproxyio.proxyio()
        self.faraday_cmd = faradaycommands.faraday_commands()

        # Initialize variables
        self.destination_callsign = ''
        self.destination_id = 0
        self.command = ''

    def updatedestinationstation(self, dest_callsign, dest_id):
        """
        This function updates the class object's destination callsign and ID that will change the respective device
        that the message/data will be transmitted to. This will allow the program to correctly address a Faraday device
        over the RF layer 2 link layer (and possibly above)

        Watch out for max callsign lengths!

        :param dest_callsign: The destination (remote) device callsign to address the transmissions to
        :param dest_id: The destination (remote) device callsign ID number to address the transmissions to

        """
        self.destination_callsign = str(dest_callsign).upper()  # Ensure callsign is always uppercase
        self.destination_id = int(dest_id)

    def transmitframe(self, payload, destination_callsign, destination_id):
        """
        A basic function used to transmit a raw payload to the intended destination unit as defined in the class
        variables. This is the high level function used to initiate a transmit of payload data/message.

        :param payload: The payload data/message to be transmitted.
        :param destination_callsign: The destination (remote) device callsign to address the transmissions to
        :param destination_id: The destination (remote) device callsign ID number to address the transmissions to

        """
        self.command = self.faraday_cmd.CommandLocalExperimentalRfPacketForward(destination_callsign,
                                                                                destination_id,
                                                                                payload)
        #print "Transmitting message:", repr(payload), "length:", len(payload)
        self.faraday_1.POST(self.local_device_callsign, self.local_device_node_id, self.faraday_1.CMD_UART_PORT,
                            self.command)


class MsgStateMachineRx(object):
    def __init__(self):
        """
        A state machine that handles the functionality needed to reassemble a message
        """
        # States
        self.STATE_IDLE = 0
        self.STATE_RX_INIT = 1
        self.STATE_RX_FRAGMENT = 2
        self.STATE_RX_END = 3
        # Frame Types
        self.MSG_START = 255
        self.MSG_DATA = 254
        self.MSG_END = 253
        # Variables
        self.currentstate = self.STATE_IDLE
        self.message = ''
        self.rx_station = ''

    def changestate(self, state):
        """
        A simple function used to change the class object state machine state.

        :param state: The new state to update the state machine to

        """
        self.currentstate = state

    def frameassembler(self, frame_type, data):
        """
        This function reassembles the received fragment packets into the original data/message using the class object's
        state machine.

        :param frame_type: The frame type being parsed and reassembled (START/DATA/END) packet types
        :param data: The data contained in the received fragment packet

        :returns If END packet then returns full reassembled packet
        :returns If NOT END packet then returns None

        """
        # Not a true state machine yet, but working to it!
        # Start
        if frame_type == self.MSG_START:
            self.changestate(self.STATE_RX_INIT)
            self.message = ''
            callsign_len = int(data[1])
            #fragments = data[3]
            self.rx_station = str(data[0][0:callsign_len]) + '-' + str(data[2])
            return None
        # Data
        elif frame_type == self.MSG_DATA:
            self.changestate(self.STATE_RX_FRAGMENT)
            #data_sequence = data[0]
            data_len = data[1]
            data_data = str(data[2])[0:data_len]
            self.message += data_data
            return None
        # Stop
        elif frame_type == self.MSG_END:
            self.changestate(self.STATE_RX_END)
            #fragments = data[0]
            message_assembled = {'source_callsign': self.rx_station, 'message': self.message}
            return message_assembled
        # Else Type (Error)
        else:
            print "Incorrect frame type:", frame_type, repr(data)


class MessageAppRx(object):
    def __init__(self):
        """
        The message application object contains all the functions, definitions, and state machines needed to implement
        a bare-bones text message application using the Faraday command application "experimental RF Packet Forward"
        functionality."
        """
        # Identification Variables
        self.local_device_callsign = 'kb1lqc'
        self.local_device_node_id = 1
        # Initialize objects
        self.faraday_Rx = faradaybasicproxyio.proxyio()
        self.faraday_Rx_SM = MsgStateMachineRx()
        # Initialize variables
        # Frame Definitions (Should be combined later with TX?)
        self.pkt_datagram_frame = struct.Struct('1B 41s')  # Fixed
        self.pkt_start = struct.Struct('9s 3B')  # Fixed
        self.pkt_data = struct.Struct('2B 39s')  # Variable  Data Length
        self.pkt_end = struct.Struct('1B')  # Fixed

    def getnextframe(self):
        """
        This function is used to check for a new received packet to be retrieved in the receive Proxy queue for the
        expected experimental RF packet forwarding messaging UART service port number. The retrieved packet will be
        parsed accordingly.
        """
        print repr(self.faraday_Rx.GETWait(self.local_device_callsign, self.local_device_node_id,
                                           self.faraday_Rx.CMD_UART_PORT, 1, False))

    def parsepacketfromdatagram(self, datagram):
        """
        This function parses recevied data packets (datagrams) and performs receiver state machine reassembly functions
        respectively.

        :param datagram: The received packet to be parsed

        :return If END packet then returns full reassembled packet
        :return If NOT END packet then returns None

        """
        unpacked_datagram = self.pkt_datagram_frame.unpack(datagram)
        packet_identifier = unpacked_datagram[0]
        packet = unpacked_datagram[1]
        try:
            # Start Packet
            if packet_identifier == 255:
                unpacked_packet = self.pkt_start.unpack(packet[0:12])
                # print unpacked_packet
                self.faraday_Rx_SM.frameassembler(255, unpacked_packet)
                return None
            # Data Packet
            if packet_identifier == 254:
                unpacked_packet = self.pkt_data.unpack(packet[0:41])
                # print unpacked_packet
                self.faraday_Rx_SM.frameassembler(254, unpacked_packet)
                return None
            # END Packet
            if packet_identifier == 253:
                unpacked_packet = self.pkt_end.unpack(packet[0])
                # print unpacked_packet
                message_assembled = self.faraday_Rx_SM.frameassembler(253, unpacked_packet)
                return message_assembled
        except Exception, err:
            print "Fail - Exception", Exception, err

    def rxmsgloop(self, local_callsign, local_callsign_id, uart_service_port_application_number, getwaittimeout):
        """
        This function is used as the main high level "receiver" loop to check for new message/data fragments received
        and parse them accordingly. If a new fully reassembled message/data has been completed the function will
        return the data/message. This function should be called regularly from the receiver program on a reoccuring
        interval.

        :param local_callsign: Callsign of the local device to retrieve received data packet from
        :param local_callsign_id: Callsign ID number of the local device to retrieve received data packet from
        :param uart_service_port_application_number: The UART network stack service port number to retrieve received
        data/messages from.
        :param getwaittimeout: The time in seconds to wait for new data before unblocking the function loop. This is
        the timeout time in the FaradayIO faradaybasicproxyio programs "GETWait()" function.


        :returns If message not received properly (but trigger) then returns None (unlikely)
        :returns If new data/message received and reassembled then returns the received data/message as a dictionary
        of the source callsign/ID and data.

        """
        data = None
        data = self.faraday_Rx.GETWait(str(local_callsign).upper(),
                                       int(local_callsign_id),
                                       uart_service_port_application_number,
                                       getwaittimeout)
        if (data is not None) and ('error' not in data):
            for item in data:
                datagram = self.faraday_Rx.DecodeRawPacket(item['data'])
                # All frames are 42 bytes long and need to be extracted from the much larger UART frame from Faraday
                datagram = datagram[0:42]
                message_status = self.parsepacketfromdatagram(datagram)
                if message_status is None:
                    return None  # Partial fragmented packet, still receiving
                else:
                    return message_status  # Full packet relieved!

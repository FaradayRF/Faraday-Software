# imports
import struct
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))  # Append path to common tutorial FaradayIO module
# noinspection PyPep8
from FaradayIO import faradaybasicproxyio
# noinspection PyPep8
from FaradayIO import faradaycommands


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
        # Determine fragment count
        frag_cnt = msg_len / self.MAX_MSG_DATA_LENGTH
        if msg_len % self.MAX_MSG_DATA_LENGTH > 0:
            frag_cnt += 1
        return frag_cnt

    def fragmentmsg(self, msg):
        list_message_fragments = [msg[i:i + self.MAX_MSG_DATA_LENGTH] for i in
                                  range(0, len(msg), self.MAX_MSG_DATA_LENGTH)]
        for item in list_message_fragments:
            print item, "Frag Length", len(item)
        print repr(list_message_fragments)
        return list_message_fragments

    def createmsgpackets(self, src_call, src_id, msg):
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
            print "Pre-Pack:", repr(data_packet), len(data_packet)
            data_packet = self.pkt_datagram_frame.pack(self.MSG_DATA, data_packet)
            print "Post-Pack:", repr(data_packet), len(data_packet)
            list_data_packets.append(data_packet)
        # Insert all packets into final packet list in order of transmission
        self.list_packets = []  # Reset any old packet fragments
        del self.list_packets[:]  # Remove all old indexes
        self.list_packets.append(msg_start)
        for i in range(0, len(list_data_packets), 1):
            self.list_packets.append(list_data_packets[i])
        self.list_packets.append(msg_end)

    def createstartframe(self, src_call, src_id, msg_len):
        # Calculate the number of fragmented packets
        frag_cnt = self.fragmentcount(msg_len)
        print frag_cnt
        # Create packet
        packet = self.pkt_start.pack(src_call, len(src_call), src_id, frag_cnt)
        # Return packet created
        return packet

    def createdataframe(self, sequence, data):
        print "create:", repr(data), len(data)
        packet = self.pkt_data.pack(sequence, len(data), data)
        print "created:", repr(packet), len(packet)
        return packet

    def createendframe(self, msg_len):
        frag_cnt = self.fragmentcount(msg_len)
        packet = self.pkt_end.pack(frag_cnt)
        return packet


class MessageAppTx(object):
    def __init__(self, local_callsign, local_callsign_id, destination_callsign, destination_id):
        """
        The message application object contains all the functions, definitions, and state machines needed to implement
        a bare-bones text message application using the Faraday command application "experimental RF Packet
        Forward" functionality."
        """
        # Identification Variables
        self.local_device_callsign = str(local_callsign).upper()
        self.local_device_node_id = int(local_callsign_id)
        self.remote_callsign = str(destination_callsign).upper()
        self.remote_id = int(destination_id)

        # Initialize objects
        self.faraday_1 = faradaybasicproxyio.proxyio()
        self.faraday_cmd = faradaycommands.faraday_commands()

        # Initialize variables
        self.destination_callsign = ''
        self.destination_id = 0
        self.command = ''

    def updatedestinationstation(self, dest_callsign, dest_id):
        """
        Update the destination station callsign and id to direct the message data packets to. Watch out for max
        callsign lengths!
        """
        self.destination_callsign = str(dest_callsign).upper()  # Ensure callsign is always uppercase
        self.destination_id = int(dest_id)

    def transmitframe(self, payload):
        """
        A basic function to transmit a raw payload to the intended destination unit.
        """
        self.command = self.faraday_cmd.CommandLocalExperimentalRfPacketForward(self.destination_callsign,
                                                                                self.destination_id,
                                                                                payload)
        print "Transmitting message:", repr(payload), "length:", len(payload)
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
        self.currentstate = state

    def frameassembler(self, frame_type, data):
        # Not a true state machine yet, but working to it!
        # Start
        if frame_type == self.MSG_START:
            self.changestate(self.STATE_RX_INIT)
            self.message = ''
            callsign_len = int(data[1])
            #fragments = data[3]
            self.rx_station = str(data[0][0:callsign_len]) + '-' + str(data[2])
        # Data
        elif frame_type == self.MSG_DATA:
            self.changestate(self.STATE_RX_FRAGMENT)
            #data_sequence = data[0]
            data_len = data[1]
            data_data = str(data[2])[0:data_len]
            self.message += data_data
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
        print repr(self.faraday_Rx.GETWait(self.local_device_callsign, self.local_device_node_id,
                                           self.faraday_Rx.CMD_UART_PORT, 1, False))

    def parsepacketfromdatagram(self, datagram):
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

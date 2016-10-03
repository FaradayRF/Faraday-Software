# imports
from FaradayIO import faradaybasicproxyio
from FaradayIO import faradaycommands

import struct

class Msg_State_Machine_Tx(object):
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
        self.pkt_datagram_frame = struct.Struct('1B 39s')  # Fixed
        self.pkt_start = struct.Struct('9s 3B')  # Fixed
        self.pkt_data = struct.Struct('2B 38s')  # Variable  Data Length
        self.pkt_end = struct.Struct('1B')  # Fixed

    def FragmentCount(self, msg_len):
        # Determine fragment count
        frag_cnt = msg_len / self.MAX_MSG_DATA_LENGTH
        if (msg_len % self.MAX_MSG_DATA_LENGTH > 0):
            frag_cnt += 1
        return frag_cnt

    def FragmentMsg(self, msg):
        list_Message_Fragments = [msg[i:i + self.MAX_MSG_DATA_LENGTH] for i in
                                  range(0, len(msg), self.MAX_MSG_DATA_LENGTH)]
        for item in list_Message_Fragments:
            print item, "Frag Length", len(item)
        print repr(list_Message_Fragments)
        return list_Message_Fragments

    def CreateMsgPackets(self, src_call, src_id, msg):
        # Create START Packet
        msg_start = self.CreateStartFrame(src_call, src_id, len(msg))
        msg_start = self.pkt_datagram_frame.pack(self.MSG_START, msg_start)
        # Create END Packet
        msg_end = self.CreateEndFrame(len(msg))
        msg_end = self.pkt_datagram_frame.pack(self.MSG_END, msg_end)
        # Create DATA Packet(s)
        list_msg_fragments = self.FragmentMsg(msg)
        list_data_packets = []
        del list_data_packets[:] # Remove all old indexes
        for i in range(0, len(list_msg_fragments), 1):
            data_packet = self.CreateDataFrame(i, list_msg_fragments[i])
            data_packet = self.pkt_datagram_frame.pack(self.MSG_DATA, data_packet)
            list_data_packets.append(data_packet)
        # Insert all packets into final packet list in order of transmission
        self.list_packets = [] # Reset any old packet fragments
        del self.list_packets[:] # Remove all old indexes
        self.list_packets.append(msg_start)
        for i in range(0, len(list_data_packets), 1):
            self.list_packets.append(list_data_packets[i])
        self.list_packets.append(msg_end)

    def CreateStartFrame(self, src_call, src_id, msg_len):
        # Calculate the number of fragmented packets
        frag_cnt = self.FragmentCount(msg_len)
        print frag_cnt
        # Create packet
        packet = self.pkt_start.pack(src_call, len(src_call), src_id, frag_cnt)
        # Return packet created
        return packet

    def CreateDataFrame(self, sequence, data):
        packet = self.pkt_data.pack(sequence, len(data), data)
        return packet

    def CreateEndFrame(self, msg_len):
        frag_cnt = self.FragmentCount(msg_len)
        packet = self.pkt_end.pack(frag_cnt)
        return packet


class message_app_Tx(object):
    def __init__(self):
        """
        The message application object contains all the functions, definitions, and state machines needed to implement a bare-bones text message application using the Faraday command application "experimental RF Packet Forward" functionality."
        """
        # Identification Variables
        self.local_device_callsign = 'kb1lqd'
        self.local_device_node_id = 7
        self.transmit_proxy_flask_port = 8099
        self.remote_callsign = 'KB1LQC'  # case independant
        self.remote_id = 1
        # Initialize objects
        self.faraday_1 = faradaybasicproxyio.proxyio(self.transmit_proxy_flask_port)
        self.faraday_cmd = faradaycommands.faraday_commands()
        # Initialize variables
        self.destination_callsign = ''
        self.destination_id = 0
        self.command = ''

    def UpdateDestinationStation(self, dest_callsign, dest_id):
        """
        Update the destination station callsign and id to direct the message data packets to. Watch out for max callsign lengths!
        """
        self.destination_callsign = dest_callsign
        self.destination_id = dest_id

    def TransmitFrame(self, payload):
        """
        A basic function to transmit a raw payload to the intended destination unit.
        """
        self.command = self.faraday_cmd.CommandLocalExperimentalRfPacketForward(self.destination_callsign,
                                                                                self.destination_id, payload)
        print "Transmitting message:", repr(payload)
        self.faraday_1.POST(self.local_device_callsign, self.local_device_node_id, self.faraday_1.CMD_UART_PORT,
                            self.command)


class Msg_State_Machine_Rx(object):
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

    def ChangeState(self, state):
        self.currentstate = state

    def FrameAssembler(self, frame_type, data):
        # Not a true state machine yet, but working to it!
        # Start
        if (frame_type == self.MSG_START):
            self.ChangeState(self.STATE_RX_INIT)
            self.message = ''
            callsign_len = int(data[1])
            fragments = data[3]
            self.rx_station = str(data[0][0:callsign_len]) + '-' + str(data[2])
        # Data
        elif (frame_type == self.MSG_DATA):
            self.ChangeState(self.STATE_RX_FRAGMENT)
            data_sequence = data[0]
            data_len = data[1]
            data_data = str(data[2])[0:data_len]
            self.message += data_data
        # Stop
        elif (frame_type == self.MSG_END):
            self.ChangeState(self.STATE_RX_END)
            fragments = data[0]
            print self.rx_station + ': ' + self.message
        # Else Type (Error)
        else:
            print "Incorrect frame type:", frame_type, repr(data)


class message_app_Rx(object):
    def __init__(self):
        """
        The message application object contains all the functions, definitions, and state machines needed to implement a bare-bones text message application using the Faraday command application "experimental RF Packet Forward" functionality."
        """
        # Identification Variables
        self.local_device_callsign = 'kb1lqd'
        self.local_device_node_id = 7
        self.transmit_proxy_flask_port = 8099
        self.receive_proxy_flask_port = 80
        # Initialize objects
        self.faraday_Tx = faradaybasicproxyio.proxyio(self.transmit_proxy_flask_port)
        self.faraday_Rx = faradaybasicproxyio.proxyio(self.receive_proxy_flask_port)
        self.faraday_Rx_SM = Msg_State_Machine_Rx()
        # Initialize variables
        # Frame Definitions (Should be combined later with TX?)
        self.pkt_datagram_frame = struct.Struct('1B 41s')  # Fixed
        self.pkt_start = struct.Struct('9s 3B')  # Fixed
        self.pkt_data = struct.Struct('2B 39s')  # Variable  Data Length
        self.pkt_end = struct.Struct('1B')  # Fixed

    def GetNextFrame(self):
        print repr(self.faraday_Rx.GETWait(self.local_device_callsign, self.local_device_node_id,
                                           self.faraday_Rx.CMD_UART_PORT, 1, False))

    def ParsePacketFromDatagram(self, datagram):
        unpacked_datagram = self.pkt_datagram_frame.unpack(datagram)
        packet_identifier = unpacked_datagram[0]
        packet = unpacked_datagram[1]
        try:
            # Start Packet
            if (packet_identifier == 255):
                unpacked_packet = self.pkt_start.unpack(packet[0:12])
                # print unpacked_packet
                self.faraday_Rx_SM.FrameAssembler(255, unpacked_packet)
            # Data Packet
            if (packet_identifier == 254):
                unpacked_packet = self.pkt_data.unpack(packet[0:41])
                # print unpacked_packet
                self.faraday_Rx_SM.FrameAssembler(254, unpacked_packet)
            # END Packet
            if (packet_identifier == 253):
                unpacked_packet = self.pkt_end.unpack(packet[0])
                # print unpacked_packet
                self.faraday_Rx_SM.FrameAssembler(253, unpacked_packet)
        except:
            print "Fail:", packet, len(packet)

    def RxMsgLoop(self):
        data = False
        data = self.faraday_Rx.GETWait('kb1lqd', 7, 3, 1, False)
        if (data != False):
            for item in data:
                datagram = self.faraday_Rx.DecodeJsonItemRaw(item['data'])
                datagram = datagram[
                           0:42]  # All frames are 42 bytes long and need to be extracted from the much larger UART frame from Faraday
                self.ParsePacketFromDatagram(datagram)

#imports
import struct
import textwrap
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))  #Append path to common tutorial FaradayIO module

from FaradayIO import faradaybasicproxyio
from FaradayIO import faradaycommands


class Msg_State_Machine_Tx(object):
    def __init__(self):
        """
        A state machine that handles the functionality needed to create and transmit a message
        """
        #Constants
        self.MAX_PAYLOAD_LENGTH = 20  #TBD
        self.MAX_MSG_DATA_LENGTH = 18  #TDB
        #States
        self.STATE_IDLE = 0
        self.STATE_INIT = 1
        self.STATE_FRAGMENT = 2
        self.STATE_TX = 3
        #Frame Types
        self.MSG_START = 255
        self.MSG_DATA = 254
        self.MSG_END = 253
        #Variables
        self.list_packets = []
        #Frame Definitions
        self.pkt_datagram_frame = struct.Struct('1B 19s')
        self.pkt_start = struct.Struct('9s 3B')
        self.pkt_data = struct.Struct('2B 18s')
        self.pkt_end = struct.Struct('1B')

    def FragmentCount(self, msg_len):
        #Determine fragment count
        frag_cnt = msg_len / self.MAX_MSG_DATA_LENGTH
        if msg_len % self.MAX_MSG_DATA_LENGTH > 0:
            frag_cnt += 1
        return frag_cnt

    def FragmentMsg(self, msg):
        list_Message_Fragments = textwrap.wrap(msg, self.MAX_MSG_DATA_LENGTH)
        return list_Message_Fragments

    def CreateMsgPackets(self, src_call, src_id, msg):
        #Create START Packet
        msg_start = self.CreateStartFrame(src_call, src_id, len(msg))
        #Create END Packet
        msg_end = self.CreateEndFrame(len(msg))
        #Create DATA Packet(s)
        list_msg_fragments = self.FragmentMsg(msg)
        list_data_packets = []
        for i in range(0, len(list_msg_fragments), 1):
            list_data_packets.append(self.CreateDataFrame(i, list_msg_fragments[i]))
        #Insert all packets into final packet list in order of transmission
        self.list_packets.append(msg_start)
        for i in range(0, len(list_data_packets), 1):
            self.list_packets.append(list_data_packets[i])
        self.list_packets.append(msg_end)

    def CreateStartFrame(self, src_call, src_id, msg_len):
        #Calculate the number of fragmented packets
        frag_cnt = self.FragmentCount(msg_len)
        print frag_cnt
        #Create packet
        packet = self.pkt_start.pack(src_call, len(src_call), src_id, frag_cnt)
        #Return packet created
        return packet

    def CreateDataFrame(self, sequence, data):
        packet = self.pkt_data.pack(sequence, len(data), data)
        return packet

    def CreateEndFrame(self, msg_len):
        frag_cnt = self.FragmentCount(msg_len)
        packet = self.pkt_end.pack(frag_cnt)
        return packet


class message_app(object):
    def __init__(self, local_callsign, local_callsign_id, destination_callsign, destination_id):
        """
        The message application object contains all the functions, definitions, and state machines needed to implement a bare-bones text message application using the Faraday command application "experimental RF Packet Forward" functionality."
        """
        #Identification Variables
        self.local_device_callsign = str(local_callsign).upper()
        self.local_device_node_id = int(local_callsign_id)
        self.remote_callsign = str(destination_callsign).upper()
        self.remote_id = int(destination_id)
        #Initialize objects
        self.faraday_1 = faradaybasicproxyio.proxyio(self.transmit_proxy_flask_port)
        self.faraday_cmd = faradaycommands.faraday_commands()
        #Initialize variables
        self.destination_callsign = ''
        self.destination_id = 0

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
        self.command = self.faraday_cmd.CommandLocalExperimentalRfPacketForward(self.destination_callsign, self.destination_id, payload)
        print "Transmitting message:", repr(payload)
        self.faraday_1.POST(self.local_device_callsign, self.local_device_node_id, self.faraday_1.CMD_UART_PORT, self.command)

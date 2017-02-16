#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Brent
#
# Created:     11/06/2016
# Copyright:   (c) Brent 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import base64
import requests
import struct
import time
from Command_Module import Command_Module

MSG_TRANSPORT_SERVICE_NUMBER = 3
MSG_DATA_LEN_MAX = 42
MSG_DATA_LEN_MAX_2 = 39
MSG_MULTI_DATA_LEN_MAX = 254*MSG_DATA_LEN_MAX
MSG_FRAG_LEN_MAX = 254

def SendMsg(packet):
    """
    Send command will transmit the provided packet to the provided command "number" over the module defined UART "Service Port." Send Command utilizes the Farday
    proxy interface that implements a TCP socket FLASK interface.
    """
    #Create test configuration packet
    packet_64 = base64.b64encode(packet)
    #print b64cmd
    status = requests.post('http://127.0.0.1/faraday/'+ str(MSG_TRANSPORT_SERVICE_NUMBER) +'?cmd=%s' % packet_64)
    #print "Sent", repr(packet)
    return status


def CreateUartMsgPacket(cmd, dest_call, dest_id, data):
    if(len(data)<=MSG_DATA_LEN_MAX):
        packet_format = struct.Struct('1B 9s 1B 1B 42s')
        packed_data = Command_Module.create_fixed_length_packet(data, 42)
        packet = packet_format.pack(cmd, dest_call.upper(), dest_id, len(packed_data), packed_data)
        return packet
    else:
        return False

def CreateRfPkt(sequence, packet):
    if(len(packet)<=MSG_DATA_LEN_MAX_2):
        packet_format = struct.Struct('1B 39s 2B')
        packet = packet_format.pack(sequence, packet, 0xAA, 0xBB)
        return packet
    else:
        return False

def CreateMsgPkt_SOH(src_callsign, src_id, fragments):
    if(fragments<MSG_FRAG_LEN_MAX):
        packet_format = struct.Struct('9s 3B')
        packet = packet_format.pack(src_callsign.upper(), len(src_callsign), src_id, fragments)
        return packet
    else:
        return False

def CreateMsgPkt_MSG(message):
    if(len(message)<=MSG_DATA_LEN_MAX_2):
        packet_format = struct.Struct('1B' + str(len(message)) + 's')
        packet = packet_format.pack(len(message), message)
        return packet
    else:
        return False

def CreateMsgPkt_EOT():
    packet_format = struct.Struct('1B')
    packet = packet_format.pack(0)
    return packet


def ParseMsgPkt_MSG(packet):
    packet_format_raw = struct.Struct('1B 38s')
    packet_parsed_raw = packet_format_raw.unpack(packet)
    #print "RAW", packet_parsed_raw
    packet_format = struct.Struct(str(packet_parsed_raw[0]) +'s'+str(38-int(packet_parsed_raw[0])) +'x')
    packet_parsed = packet_format.unpack(packet_parsed_raw[1])
    return packet_parsed

def ParseRfPkt(packet):
    packet_format = struct.Struct('1B 39s 2B')
    packer_parsed = packet_format.unpack(packet)
    return packer_parsed

def ParseMsgPkt_SOH(packet):
    packet_format = struct.Struct('9s 3B 27x')
    return packet_format.unpack(packet)

def CalcFragCnt(message, fragment_size):
    count = len(message)/fragment_size
    if(len(message)%fragment_size != 0):
        count += 1
    return count

def FragmentMsg(message, fragment_size):
    fraglist = [message[i:i+fragment_size] for i in range(0, len(message), fragment_size)]
    return fraglist

def CreateFrags(src_call, src_id, dest_call, dest_id ,message):
    fragcnt = CalcFragCnt( message, 20)
    SendMsg(CreateUartMsgPacket(0, dest_call, dest_id, CreateRfPkt(0, CreateMsgPkt_SOH(src_call,src_id, fragcnt))))
    message_list = FragmentMsg(message, 20)
    #print message_list
    for i in range(1, len(message_list)+1, 1):
        #time.sleep(0.005) #Delay! Get rid of it but it overruns for now?
        #print i
        SendMsg(CreateUartMsgPacket(0, dest_call, dest_id, CreateRfPkt(i, CreateMsgPkt_MSG(message_list[i-1]))))
    #time.sleep(0.005) #Delay! Get rid of it but it overruns for now?
    SendMsg(CreateUartMsgPacket(0, dest_call, dest_id, CreateRfPkt(255, CreateMsgPkt_MSG("End of message"))))



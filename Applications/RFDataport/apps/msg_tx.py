#!/usr/bin/env python

import requests
import ConfigParser
import os
import time
import base64
import struct
#import packet

config = ConfigParser.RawConfigParser()
filename = os.path.abspath("rfdataport.ini")
config.read(filename)

proxylocalcallsign = 'KB1LQD' #config.get('UNIT0', 'CALLSIGN')
proxylocalnodeid = 1 #int(config.get('UNIT0', 'NODEID'))
destinationcallsign = 'KB1LQD' #config.get('UNIT1', 'CALLSIGN')
destinationnodeid = 2 #int(config.get('UNIT1', 'NODEID'))

msglocalcallsign = '' #config.get('UNIT0', 'CALLSIGN')
msglocalnodeid = 0 #int(config.get('UNIT0', 'NODEID'))

INTERVAL_SEC = 0.001

packet_msg_struct = struct.Struct('6s 3B 31s')
PACKET_CALLSIGN_LEN = 6
PACKET_PAYLOAD_LEN = 31


def main():
    """
    Main function of the transmit example of Hermes messaging application using Flask. This function loops continuously
    getting user input text to transmit to the Flask server for wireless transmission to the intended remote device.
    """

    msglocalcallsign = raw_input("Enter TX ID CALLSIGN: ")
    msglocalnodeid = int(raw_input("Enter TX ID NODEID: "))

    while True:
        message = raw_input("Enter Message: ")

        frag_data_list = fragmentmsg(message, PACKET_PAYLOAD_LEN)
        data_tx_len = len(frag_data_list)
        sequence_cnt = 0

        frag_data_list_len = len(frag_data_list)
        print "LEN:", frag_data_list_len

        for item in frag_data_list:
            if frag_data_list_len == 1:
                data_tx = packet_msg_struct.pack(str(msglocalcallsign).upper(), msglocalnodeid, 254, len(item),
                                                 str(item))
            elif sequence_cnt == frag_data_list_len-1:
                data_tx = packet_msg_struct.pack(str(msglocalcallsign).upper(), msglocalnodeid, 255, len(item),
                                                 str(item))
            else:
                #Create datapacket
                data_tx = packet_msg_struct.pack(str(msglocalcallsign).upper(), msglocalnodeid, sequence_cnt, len(item), str(item))
            data_tx = base64.b64encode(data_tx)
            payload = {'localcallsign': proxylocalcallsign, 'localnodeid': proxylocalnodeid,
                       'destinationcallsign': destinationcallsign, 'destinationnodeid': destinationnodeid,
                       'data': data_tx}
            print "TRANSMIT", sequence_cnt,":", data_tx
            requests.post('http://127.0.0.1:8009/', params=payload)
            sequence_cnt += 1

#def pack_data():

def fragmentmsg(msg, fragmentsize):
    """
    This function fragments the supplied message into smaller packets or "chunks" that will fit into the
    pre-determined MTU (maximum transmissible unit) of the packet's path. Using an algorithm these fragments can
    be reassembled after reception.

    :param msg: The data to be fragmented

    :returns A list containing the fragmented "chunks" of data of the pre-determined size.
    """
    list_message_fragments = [msg[i:i + fragmentsize] for i in
                              range(0, len(msg), fragmentsize)]
    return list_message_fragments

if __name__ == '__main__':
    main()

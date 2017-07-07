#!/usr/bin/env python

import requests
import base64
import struct

INTERVAL_SEC = 0.001

packet_msg_struct = struct.Struct('6s 3B 31s')
PACKET_CALLSIGN_LEN = 6
PACKET_PAYLOAD_LEN = 31


def main():
    """
    Main function of the transmit example of Hermes messaging application using Flask. This function loops continuously
    getting user input text to transmit to the Flask server for wireless transmission to the intended remote device.
    """

    proxylocalcallsign = raw_input("Enter LOCAL (PROXY) ID CALLSIGN: ")
    proxylocalnodeid = int(raw_input("Enter LOCAL (PROXY) NODEID: "))
    destinationcallsign = raw_input("Enter DESTINATION CALLSIGN: ")
    destinationnodeid = int(raw_input("Enter DESTINATION NODEID: "))

    while True:
        message = raw_input("Enter Message: ")

        frag_data_list = fragmentmsg(message, PACKET_PAYLOAD_LEN)
        sequence_cnt = 0

        frag_data_list_len = len(frag_data_list)

        for item in frag_data_list:
            if frag_data_list_len == 1:
                data_tx = packet_msg_struct.pack(str(proxylocalcallsign).upper(), proxylocalnodeid, 254, len(item),
                                                 str(item))
            elif sequence_cnt == frag_data_list_len - 1:
                data_tx = packet_msg_struct.pack(str(proxylocalcallsign).upper(), proxylocalnodeid, 255, len(item),
                                                 str(item))
            else:
                # Create datapacket
                data_tx = packet_msg_struct.pack(str(proxylocalcallsign).upper(), proxylocalnodeid, sequence_cnt, len(item), str(item))
            data_tx = base64.b64encode(data_tx)
            payload = {'localcallsign': proxylocalcallsign, 'localnodeid': proxylocalnodeid,
                       'destinationcallsign': destinationcallsign, 'destinationnodeid': destinationnodeid,
                       'data': data_tx}
            print("Transmitting [{0}]: {1}".format(str(sequence_cnt), data_tx))  # Not sure if properly showing up in CMD window...
            requests.post('http://127.0.0.1:8009/', params=payload)
            sequence_cnt += 1


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

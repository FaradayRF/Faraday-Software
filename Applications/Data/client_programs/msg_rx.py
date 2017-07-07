#!/usr/bin/env python

import requests
import time
import base64
import struct

packet_msg_struct = struct.Struct('6s 3B 31s')
PACKET_CALLSIGN_LEN = 6
PACKET_PAYLOAD_LEN = 31


def main():
    """
    Main function of the receiver client test program for the Faraday DATA server.
    """
    rx_msg = ''
    rx_station = ''

    proxylocalcallsign = raw_input("Enter LOCAL (PROXY) ID CALLSIGN: ")
    proxylocalnodeid = int(raw_input("Enter LOCAL (PROXY) NODEID: "))

    while True:

        try:
            payload = {'localcallsign': proxylocalcallsign, 'localnodeid': proxylocalnodeid}
            rxdata = requests.get('http://127.0.0.1:8009/', params=payload)
            if rxdata.status_code == 204:
                pass  # Commenting out for now to avoid constant prints when no data on boot
                #print("Request Status Code: {0}".format(rxdata.status_code))
            else:
                if rxdata.status_code != 500:
                    for item in rxdata.json():
                        data_extract = base64.b64decode(item['data'])
                        data_parsed = parse_pkt(data_extract)

                        if data_parsed[2] == 0:  # Start of new message
                            rx_station = str(data_parsed[0]) + '-' + str(data_parsed[1])
                            rx_msg = str(data_parsed[4][0:data_parsed[3]])
                        elif data_parsed[2] == 254:  # Message length == 1, end of data.
                            rx_station = str(data_parsed[0]) + '-' + str(data_parsed[1])
                            rx_msg = str(data_parsed[4][0:data_parsed[3]])
                            print("RX Message ({0}): {1}".format(rx_station, rx_msg))
                        elif data_parsed[2] == 255:  # Final fragment, end of data.
                            rx_msg += str(data_parsed[4][0:data_parsed[3]])
                            print("RX Message ({0}): {1}".format(rx_station, rx_msg))
                        else:  # Append message fragment
                            rx_msg += str(data_parsed[4][0:data_parsed[3]])
                else:
                    print("Request Status Code: {0}".format(rxdata.status_code))

        except:
            pass  # Commenting out for now to avoid constant prints when no data on boot
            #print("Exception: {0}".format(e))
        time.sleep(0.1)


def parse_pkt(rx_packet):
    """
    This function parses the raw packet argument using the expected DATA packet fragment fields.

    :param rx_packet: Received packet to be parsed into fields

    :Return: The parsed packet as a list of fields.
    """
    parsed_data = packet_msg_struct.unpack(rx_packet)
    return parsed_data


if __name__ == '__main__':
    main()

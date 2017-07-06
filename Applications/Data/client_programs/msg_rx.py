#!/usr/bin/env python

import requests
import ConfigParser
import os
import time
import base64
import struct
import logging.config
import sys

packet_msg_struct = struct.Struct('6s 3B 31s')
PACKET_CALLSIGN_LEN = 6
PACKET_PAYLOAD_LEN = 31


# Start logging after importing modules
relpath1 = os.path.join('etc', 'faraday')
relpath2 = os.path.join('..', 'etc', 'faraday')
setuppath = os.path.join(sys.prefix, 'etc', 'faraday')
userpath = os.path.join(os.path.expanduser('~'), '.faraday')
path = ''

for location in os.curdir, relpath1, relpath2, setuppath, userpath:
    try:
        logging.config.fileConfig(os.path.join(location, "loggingConfig.ini"))
        path = location
        break
    except ConfigParser.NoSectionError:
        pass

logger = logging.getLogger('Data')

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
                logger.info("Request Status Code: {0}".format(rxdata.status_code))
            else:
                if rxdata.status_code != 500:
                    for item in rxdata.json():
                        data_extract = base64.b64decode(item['data'])
                        data_parsed = parse_pkt(data_extract)

                        if data_parsed[2] == 0:
                            rx_station = str(data_parsed[0]) + '-' + str(data_parsed[1])
                            rx_msg = str(data_parsed[4][0:data_parsed[3]])
                        elif data_parsed[2] == 254:
                            rx_station = str(data_parsed[0]) + '-' + str(data_parsed[1])
                            rx_msg = str(data_parsed[4][0:data_parsed[3]])
                            print("RX Message ({0}): {1}".format(rx_station, rx_msg))
                        elif data_parsed[2] == 255:
                            rx_msg += str(data_parsed[4][0:data_parsed[3]])
                            print("RX Message ({0}): {1}".format(rx_station, rx_msg))
                        else:
                            rx_msg += str(data_parsed[4][0:data_parsed[3]])
                else:
                    logger.info("Request Status Code: {0}".format(rxdata.status_code))


        except Exception as e:
            logger.info("Exception: {0}".format(e))
        time.sleep(0.1)

def parse_pkt(rx_packet):
    """
    This function parses the raw packet arguement using the expected DATA packet fragment fields.

    :param rx_packet: Received packet to be parsed into fields

    :Return: The parsed packet as a list of fields.
    """
    parsed_data = packet_msg_struct.unpack(rx_packet)
    return parsed_data

if __name__ == '__main__':
    main()

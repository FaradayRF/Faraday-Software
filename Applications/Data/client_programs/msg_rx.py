#!/usr/bin/env python

import requests
import ConfigParser
import os
import time
import json
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
    Main function of the transmit example of Hermes messaging application using Flask. This function loops continuously
    getting user input text to transmit to the Flask server for wireless transmission to the intended remote device.
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
                pass
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
                            print rx_station + ': ' + rx_msg
                        elif data_parsed[2] == 255:
                            rx_msg += str(data_parsed[4][0:data_parsed[3]])
                            print rx_station + ': ' + rx_msg
                        else:
                            rx_msg += str(data_parsed[4][0:data_parsed[3]])


        except:
            print "Fail"
            pass
        time.sleep(0.01)

def parse_pkt(rx_packet):
    parsed_data = packet_msg_struct.unpack(rx_packet)
    return parsed_data

if __name__ == '__main__':
    main()

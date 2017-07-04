#!/usr/bin/env python

import requests
import ConfigParser
import os
import time
import json
import base64
import struct
#import packet



config = ConfigParser.RawConfigParser()
#filename = os.path.abspath("../rfdataport.ini")
#config.read(filename)

localcallsign = 'KB1LQD' #config.get('UNIT0', 'CALLSIGN')
localnodeid = 2 #int(config.get('UNIT0', 'NODEID'))

packet_msg_struct = struct.Struct('6s 3B 31s')
PACKET_CALLSIGN_LEN = 6
PACKET_PAYLOAD_LEN = 31

def main():
    """
    Main function of the transmit example of Hermes messaging application using Flask. This function loops continuously
    getting user input text to transmit to the Flask server for wireless transmission to the intended remote device.
    """
    rx_msg = ''
    rx_station = ''
    while True:

        try:
            payload = {'localcallsign': localcallsign, 'localnodeid': localnodeid}
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
        time.sleep(0.1)

def parse_pkt(rx_packet):
    parsed_data = packet_msg_struct.unpack(rx_packet)
    return parsed_data

if __name__ == '__main__':
    main()
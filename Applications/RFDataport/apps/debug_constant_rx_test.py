#!/usr/bin/env python

import requests
import ConfigParser
import os
import time
import json
import base64
import struct
#import packet


# TEMP, USE packet.py later in correct directory
packet_struct = struct.Struct('2B 40s')
PACKET_LEN = 42
PAYLOAD_LEN = 40


config = ConfigParser.RawConfigParser()
#filename = os.path.abspath("../rfdataport.ini")
#config.read(filename)

localcallsign = 'KB1LQD' #config.get('UNIT0', 'CALLSIGN')
localnodeid = 2 #int(config.get('UNIT0', 'NODEID'))



def main():
    """
    Main function of the transmit example of Hermes messaging application using Flask. This function loops continuously
    getting user input text to transmit to the Flask server for wireless transmission to the intended remote device.
    """
    while True:

        try:
            payload = {'localcallsign': localcallsign, 'localnodeid': localnodeid}
            rxdata = requests.get('http://127.0.0.1:8009/', params=payload)
            if rxdata.status_code is 204:
                pass
            else:
                #rx_dataitems = json.loads(base64.b64decode(rxdata.json()))
                rxdata_decode_json = json.loads(rxdata.text)
                for item in rxdata_decode_json:
                    data_item = base64.b64decode(item['data'])

                    # Parse application packet
                    #data_item_parsed = packet_struct.unpack(data_item)

                    #Print only data transmitted, remove extra data (padding)
                    print data_item
                    #print data_item_parsed
        except:
            pass
        time.sleep(0.1)


if __name__ == '__main__':
    main()

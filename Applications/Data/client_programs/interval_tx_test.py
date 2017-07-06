#!/usr/bin/env python

import requests
import ConfigParser
import os
import time
import base64
import struct
import sys
#import packet

# TEMP, USE packet.py later in correct directory
packet_struct = struct.Struct('2B 40s')
PACKET_LEN = 42
PAYLOAD_LEN = 40

config = ConfigParser.RawConfigParser()
filename = os.path.abspath("rfdataport.ini")
config.read(filename)

localcallsign = 'KB1LQD' #config.get('UNIT0', 'CALLSIGN')
localnodeid = 1 #int(config.get('UNIT0', 'NODEID'))
destinationcallsign = 'KB1LQD' #config.get('UNIT1', 'CALLSIGN')
destinationnodeid = 2 #int(config.get('UNIT1', 'NODEID'))

INTERVAL_SEC = 0.05



def main():
    """
    Main function of the transmit example of Hermes messaging application using Flask. This function loops continuously
    getting user input text to transmit to the Flask server for wireless transmission to the intended remote device.
    """
    count = 0
    while True:
        #message = raw_input("Enter Message: ")
        if count < 256:
            pass
        else:
            count = 0

        #message = "COUNT = " + str(count) + " --- " + base64.b64encode(os.urandom(20))
        message = base64.b64encode(packet_struct.pack(PACKET_LEN,count,base64.b64encode(os.urandom(39))))

        payload = {'localcallsign': localcallsign, 'localnodeid': localnodeid,
                   'destinationcallsign': destinationcallsign, 'destinationnodeid': destinationnodeid,
                   'data': message}
        print "TRANSMIT", count, ":", message
        #requests.post('http://127.0.0.1:8009/', params=payload)
        sys.stdout.write(message)
        sys.stdout.write(b"\n")
        sys.stdout.flush()
        count+=1
        time.sleep(INTERVAL_SEC)


if __name__ == '__main__':
    main()

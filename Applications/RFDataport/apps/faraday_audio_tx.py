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

INTERVAL_SEC = 0.01

data_audio = None

def main():
	while True:
        #message = raw_input("Enter Message: ")
		data_audio = sys.stdin.readline()#sys.stdin.read(32)#sys.stdin.readline()
		#print len(data_audio), data_audio
		if data_audio is not None:
			message = base64.b64encode(packet_struct.pack(PACKET_LEN,255,data_audio))

			payload = {'localcallsign': localcallsign, 'localnodeid': localnodeid,
					   'destinationcallsign': destinationcallsign, 'destinationnodeid': destinationnodeid,
					   'data': message}
			print "TRANSMIT", ":", message
			requests.post('http://127.0.0.1:8009/', params=payload)
			time.sleep(INTERVAL_SEC)
			data_audio = None


if __name__ == '__main__':
    main()

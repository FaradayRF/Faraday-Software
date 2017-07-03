#!/usr/bin/env python

import requests
import ConfigParser
import os
import time
import json
import base64
import struct

config = ConfigParser.RawConfigParser()
filename = os.path.abspath("rfdataport.ini")
config.read(filename)

localcallsign = 'KB1LQD' #config.get('UNIT0', 'CALLSIGN')
localnodeid = 2 #int(config.get('UNIT0', 'NODEID'))

packet_struct = struct.Struct('1B 41s')
packet_len = 42

counttotal = 0
countsec = 0

timestarttotal = 0
timestartsec = 0
timecurrent = 0

startflag = False


def main():
    """
    Main function of the transmit example of Hermes messaging application using Flask. This function loops continuously
    getting user input text to transmit to the Flask server for wireless transmission to the intended remote device.
    """
    global counttotal, countsec, timecurrent, timestartsec, timestarttotal, startflag, packet_len
    while True:

        try:
            payload = {'localcallsign': localcallsign, 'localnodeid': localnodeid}
            rxdata = requests.get('http://127.0.0.1:8009/', params=payload)
            if rxdata.status_code is 204:
                pass
            else:

                if startflag is False:
                    startflag = True
                    timestarttotal = timestartsec = time.time()

                #rx_dataitems = json.loads(base64.b64decode(rxdata.json()))
                rxdata_decode_json = json.loads(rxdata.text)
                counttotal += len(rxdata_decode_json)
                for item in rxdata_decode_json:
                    data_item = base64.b64decode(item['data'])


                    # Parse application packet
                    data_item_parsed = packet_struct.unpack(str(data_item[0:packet_len]))

                    # Print only data transmitted, remove extra data (padding)
                    #print data_item_parsed[1][0:data_item_parsed[0]]
                timecurrent = time.time()
                timedeltasec = timecurrent-timestartsec

                if timedeltasec > 2:
                    timestartsec = time.time()
                    throughput = counttotal/(timecurrent - timestarttotal)
                    print "\n------------------------------------------"
                    print "Bytes/sec:", throughput*packet_len
                    print "bits/sec:", throughput*packet_len*8
                    print "------------------------------------------"

        except:
            pass
        time.sleep(0.05)


if __name__ == '__main__':
    main()

#Imports - General

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../Faraday_Proxy_Tools/")) #Append path to common tutorial FaradayIO module
#Imports - Faraday Specific
from FaradayIO import faradaybasicproxyio
from FaradayIO import faradaycommands



#Variables
local_device_callsign = 'kb1lqc'
local_device_node_id = 1

#Start the proxy server after configuring the configuration file correctly
#Setup a Faraday IO object
faraday_1 = faradaybasicproxyio.proxyio()
faraday_cmd = faradaycommands.faraday_commands()
#faraday_parser = telemetryparser.TelemetryParse()

#Define constants
PROXY_MESSAGE_EXPERIMENTAL_PORT = 3
PROXY_GET_TIMEOUT = 10 #Second(s)


#Setup variables for receiving
data = None

#While loop to wait for reception of data packet from experimental message application
while(1):
    #Wait until there is new data on the message application port OR timout
    for i in range(0,255,1):
        try:
            data = faraday_1.GET(local_device_callsign, local_device_node_id, i)
            if (data != None) and (not 'error' in data):
                print "PORT", i, ":", repr(faraday_1.DecodeRawPacket(data[0]['data']))
        except:
            print "Fail"

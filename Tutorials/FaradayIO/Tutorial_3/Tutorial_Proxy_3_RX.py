#Imports - General

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../")) #Append path to common tutorial FaradayIO module
#Imports - Faraday Specific
from FaradayIO import faradaybasicproxyio
from FaradayIO import faradaycommands



#Variables
local_device_callsign = 'kb1lqd'
local_device_node_id = 1

#Start the proxy server after configuring the configuration file correctly
#Setup a Faraday IO object
faraday_1 = faradaybasicproxyio.proxyio()
faraday_cmd = faradaycommands.faraday_commands()
#faraday_parser = telemetryparser.TelemetryParse()

# This example will show how to command Faraday using the basic command application.
# Make sure to turn UART TELEM BOOT Bitmask to 0 to turn OFF telemetry update automatically


##############
## TOGGLE Remote Device ++GPIO
##############

#Remote device information
remote_callsign = 'KB1LQC' #case independant
remote_id = 1

#Define constants
PROXY_MESSAGE_EXPERIMENTAL_PORT = 3
PROXY_GET_TIMEOUT = 1 #Second(s)

#Print debug information about ports. This is important because 2 Proxy programs CANNOT operate on the same TCP port.
print "Receiver operating TCP Localhost port:", faraday_1.FLASK_PORT

#Setup variables for receiving
data = None

#While loop to wait for reception of data packet from experimental message application
while(1):
    #Wait until there is new data on the message application port OR timout
    data = faraday_1.GETWait(local_device_callsign, local_device_node_id, PROXY_MESSAGE_EXPERIMENTAL_PORT, 2, False)

    #Check if data is False (False means that the Get() function timed out), if not then display new data
    if not 'error' in data:
        #print "Received Message RAW", repr(data[0]['data'])
        print "Received Message Decoded:", faraday_1.DecodeRawPacket(data[0]['data'])

        #Set data = False so that the function loop can properly wait until the next data without printing last received data over and over
        data = None
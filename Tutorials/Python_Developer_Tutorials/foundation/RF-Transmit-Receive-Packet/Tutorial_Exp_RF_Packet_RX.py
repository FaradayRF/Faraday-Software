#Imports - General

import os
import sys
import ConfigParser

sys.path.append(os.path.join(os.path.dirname(__file__), "../../../../Faraday_Proxy_Tools")) #Append path to common tutorial FaradayIO module
#Imports - Faraday Specific
from FaradayIO import faradaybasicproxyio
from FaradayIO import faradaycommands


#Open configuration INI
config = ConfigParser.RawConfigParser()
filename = os.path.abspath("configuration.ini")
config.read(filename)

#Definitions

#Variables
transmitter_device_callsign = config.get("DEVICES", "UNIT0CALL") # Should match the connected Faraday unit as assigned in Proxy configuration
transmitter_device_node_id = config.getint("DEVICES", "UNIT0ID") # Should match the connected Faraday unit as assigned in Proxy configuration
transmitter_device_callsign = str(transmitter_device_callsign).upper()
receiver_device_callsign = config.get("DEVICES", "UNIT1CALL") # Should match the programmed callsign of the remote Faraday device to be commanded (receive)
receiver_device_node_id = config.getint("DEVICES", "UNIT1ID") # Should match the programmed callsign of the remote Faraday device to be commanded (receive)
receiver_device_callsign = str(receiver_device_callsign).upper()

#Start the proxy server after configuring the configuration file correctly
#Setup a Faraday IO object
faraday_1 = faradaybasicproxyio.proxyio()
faraday_cmd = faradaycommands.faraday_commands()

#Define constants
PROXY_MESSAGE_EXPERIMENTAL_PORT = 3
PROXY_GET_TIMEOUT = 1 # Second(s)

#Print debug information about proxy port listening
print "Receiver operating TCP Localhost port:", faraday_1.FLASK_PORT
print "Receiver (Proxy):", receiver_device_callsign + '-' + str(receiver_device_node_id)
print "\n"
#Setup variables for receiving
data = None

#While loop to wait for reception of data packet from experimental message application
while(1):
    #Wait until there is new data on the message application port OR timout
    data = faraday_1.GETWait(receiver_device_callsign, receiver_device_node_id, PROXY_MESSAGE_EXPERIMENTAL_PORT, 2)

    #Check if data is False (False means that the Get() function timed out), if not then display new data
    if (data != None) and (not 'error' in data):
        payload_data = data[0]['data']
        print "Received Message Decoded:", faraday_1.DecodeRawPacket(payload_data)

        #Set data = False so that the function loop can properly wait until the next data without printing last received data over and over
        data = None
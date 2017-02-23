#Imports - General

import os
import sys
import time
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

print "\nConnecting to proxy on PROXY device:", transmitter_device_callsign + '-' + str(transmitter_device_node_id)
print "\nTransmitter (Proxy):", transmitter_device_callsign + '-' + str(transmitter_device_node_id)
print "Receiver (Device Configuration):", receiver_device_callsign + '-' + str(receiver_device_node_id)
print '\n'

#Use the predefined experimental message command (singled packet) function to send an RF message to a remote unit
message = "Testing RF Packet 1"  # NOTE: Max payload size commandmodule.FIXED_RF_PAYLOAD_LEN
command = faraday_cmd.CommandLocalExperimentalRfPacketForward(receiver_device_callsign, receiver_device_node_id, message)
print "Transmitting message:", message
faraday_1.POST(transmitter_device_callsign, transmitter_device_node_id, faraday_1.CMD_UART_PORT, command)

message = "Testing RF Packet 2"
command = faraday_cmd.CommandLocalExperimentalRfPacketForward(receiver_device_callsign, receiver_device_node_id, message)
print "Transmitting message:", message
faraday_1.POST(transmitter_device_callsign, transmitter_device_node_id, faraday_1.CMD_UART_PORT, command)

print "************************************"
print "\nQuit with ctrl+c"
while(True):
    #Loop until user presses ctrl+c so they can read response
    time.sleep(1)
    pass
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
local_device_callsign = config.get("DEVICES","UNIT0CALL") # Should match the connected Faraday unit as assigned in Proxy configuration
local_device_node_id = config.getint("DEVICES","UNIT0ID") # Should match the connected Faraday unit as assigned in Proxy configuration
local_device_callsign = str(local_device_callsign).upper()
remote_device_callsign = config.get("DEVICES","UNIT1CALL") # Should match the programmed callsign of the remote Faraday device to be commanded (receive)
remote_device_node_id = config.getint("DEVICES","UNIT1ID") # Should match the programmed callsign of the remote Faraday device to be commanded (receive)
remote_device_callsign = str(remote_device_callsign).upper()

#Start the proxy server after configuring the configuration file correctly
#Setup a Faraday IO object
faraday_1 = faradaybasicproxyio.proxyio()
faraday_cmd = faradaycommands.faraday_commands()

#Remote device information
remote_device_callsign = 'KB1LQD'
remote_device_node_id = 2

print "\nConnecting to proxy on PROXY device:", local_device_callsign + '-' + str(local_device_node_id)
print "Transmitting to device:", remote_device_callsign + '-' + str(remote_device_node_id)

#Use the predefined experimental message command (singled packet) function to send an RF message to a remote unit
message = "Testing RF Packet 1"
command = faraday_cmd.CommandLocalExperimentalRfPacketForward(remote_device_callsign, remote_device_node_id, message)
print "Transmitting message:", message
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)

message = "Testing RF Packet 2"
command = faraday_cmd.CommandLocalExperimentalRfPacketForward(remote_device_callsign, remote_device_node_id, message)
print "Transmitting message:", message
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)

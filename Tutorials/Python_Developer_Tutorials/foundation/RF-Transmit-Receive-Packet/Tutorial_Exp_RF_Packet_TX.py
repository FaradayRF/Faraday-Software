#!/usr/bin/env python

#Imports - General

import os
import sys

# Add Faraday library to the Python path.
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

# Imports - Faraday Specific
from faraday.proxyio import faradaybasicproxyio
from faraday.proxyio import faradaycommands


#Start the proxy server after configuring the configuration file correctly
#Setup a Faraday IO object
faraday_1 = faradaybasicproxyio.proxyio()
faraday_cmd = faradaycommands.faraday_commands()

#Local device information
local_device_callsign = 'REPLACEME'  # Should match the connected Faraday unit as assigned in Proxy configuration
local_device_node_id = 0  # Should match the connected Faraday unit as assigned in Proxy configuration

#Remote device information
remote_callsign = 'KB1LQD'
remote_id = 2

print "Connecting to proxy on PROXY device:", local_device_callsign + '-' + str(local_device_node_id)
print "Transmitting to device:", remote_callsign + '-' + str(remote_id)

#Use the predefined experimental message command (singled packet) function to send an RF message to a remote unit
message = "Testing RF Packet 1"
command = faraday_cmd.CommandLocalExperimentalRfPacketForward(remote_callsign, remote_id, message)
print "Transmitting message:", message
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)

message = "Testing RF Packet 2"
command = faraday_cmd.CommandLocalExperimentalRfPacketForward(remote_callsign, remote_id, message)
print "Transmitting message:", message
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)

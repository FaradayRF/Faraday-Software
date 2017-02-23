#Imports - General

import os
import sys
import time
import ConfigParser
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../../Faraday_Proxy_Tools")) #Append path to common tutorial FaradayIO module

#Imports - Faraday Specific
from FaradayIO import faradaybasicproxyio
from FaradayIO import faradaycommands
from FaradayIO import commandmodule

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

user_input = ''

while(user_input != "quit"):
    user_input = raw_input("\nText To Transmit (Max Length = " + str(commandmodule.FIXED_RF_PAYLOAD_LEN) +" Bytes)" + ": ")
    if len(user_input) < commandmodule.FIXED_RF_PAYLOAD_LEN:
        command = faraday_cmd.CommandLocalExperimentalRfPacketForward(receiver_device_callsign, receiver_device_node_id,
                                                                      str(user_input))
        print "Transmitting message:", user_input, '\n'
        faraday_1.POST(transmitter_device_callsign, transmitter_device_node_id, faraday_1.CMD_UART_PORT, command)
    else:
        print "Payload is too long!", len(user_input), "Bytes", '\n'

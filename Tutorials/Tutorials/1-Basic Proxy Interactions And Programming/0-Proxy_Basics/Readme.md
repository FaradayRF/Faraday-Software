
# Tutorial - Proxy Basics

This tutorial will introduce key concepts and interactions with the Faraday UART proxy that allows communication between a host computer and local Faraday devices. The supplied proxy program is the main method of interaction with Faraday's over a local computer host connection and provides this functionality over a RESTful API on localhost.

The architecture of the applications interacting with Faraday are contained in several layers

**Proxy Interface: **is always the low level interface to the actual device. Applications. Proxy provides an API for the physical Faraday device.

**Applications: ** Programs that interact with the Proxy Interface and provide functionalities using a Faraday device locally connected to the host computer. Applications utilize the Proxy RESTful interface while also providing (ideally) another RESTful interface for higher level programs to provide user interfaces.


**External Interface: ** Programs that interact with applications to provide a user interface or API to the applications functionality. These provide a modular interface to faraday functionallity and are highly desired but not always neccessary. 

![Faraday proxy and application block diagram](file:///C:/Users/Brent/Documents/Faraday_Github_Software/Faraday-Software/Tutorials/Tutorials/1-Basic Proxy Interactions And Programming/0-Proxy_Basics/Images/FaradayProxyBlocks.jpg "Faraday Proxy and Application Architecture")


```python
#Imports - General

import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../")) #Append path to common tutorial FaradayIO module

#Imports - Faraday Specific
from FaradayIO import faradaybasicproxyio
from FaradayIO import faradaycommands
from FaradayIO import telemetryparser

#Definitions
FARADAY_TELEMETRY_UART_PORT = 5
FARADAY_CMD_UART_PORT = 2

#Variables
local_device_callsign = 'kb1lqd'
local_device_node_id = 1

#Start the proxy server after configuring the configuration file correctly
#Setup a Faraday IO object
faraday_1 = faradaybasicproxyio.proxyio()
faraday_cmd = faradaycommands.faraday_commands()
faraday_parser = telemetryparser.TelemetryParse()

#Get all waiting packets on the Telemetry port (assuming faraday has been auto-transmitting telemetry packets). Get returns a list of all packets received on port (in JSON dictionary format).
print "Getting the latest telemetry from Faraday!"
rx_telem_data = faraday_1.GET( local_device_callsign, local_device_node_id, FARADAY_TELEMETRY_UART_PORT)

#Check if no received data waiting in Queue
if(rx_telem_data == None):
    #No packets recieved yet, command the unit to transmit a UART telemetry packet NOW
    faraday_1.POST(local_device_callsign, local_device_node_id, FARADAY_CMD_UART_PORT, faraday_cmd.CommandLocalUARTUpdateNow())
    #Wait up to 1 second for the unit to respond to the command. NOTE: GETWait will return ALL packets received if more than 1 packet (likley not in THIS case)
    rx_telem_data = faraday_1.GETWait(local_device_callsign, local_device_node_id, FARADAY_TELEMETRY_UART_PORT, 1, True) #Will block and wait for given time until a packet is recevied

try:
    print "\nThe Recevied data contains " + str(len(rx_telem_data)) + " packet(s) encoded in BASE64"

    #Decode the first packet in list from BASE 64 to a RAW bytesting
    print rx_telem_data
    rx_telem_pkt_decoded = faraday_1.DecodeRawPacket(rx_telem_data[0]['data'])
    print "\nThe first telemetry packet is:"
    print "\nAs Received BASE64:"
    print rx_telem_data[0]['data']
    print "\nDecoded:"
    print repr(rx_telem_data)

    #Unpack the telemetry datagram containing the standard "Telemetry Packet #3" packet
    rx_telemetry_datagram = faraday_parser.UnpackDatagram(rx_telem_pkt_decoded, debug = True) #Debug is ON
    #Extract just the data packet portion of the JSON dictionary
    rx_telemetry_packet = rx_telemetry_datagram[3]
    print "\nThe Decoded Data Within The Packet Is:\n"
    print rx_telemetry_datagram[3]

    #Extract the exact debug packet from longer datagram payload (Telemetry Packet #2)
    rx_telemetry_packet_extracted = faraday_parser.ExtractPaddedPacket(rx_telemetry_packet, faraday_parser.packet_3_len)

    #Parse the Telemetry #3 packet
    rx_telemetry_packet_parsed = faraday_parser.UnpackPacket_3(rx_telemetry_packet_extracted, True) #Debug ON
except:
    print "Failed to get data."
```

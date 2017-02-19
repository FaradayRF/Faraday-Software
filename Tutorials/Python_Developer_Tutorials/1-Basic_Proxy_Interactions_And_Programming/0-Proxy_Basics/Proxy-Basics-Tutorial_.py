# Basic introduction to proxy interaction with Faraday using Python.
# - Getting received data from telemetry
# - Parsing received data

#Imports - General

import os
import sys
import time
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../../Faraday_Proxy_Tools")) #Append path to common tutorial FaradayIO module

#Imports - Faraday Specific
from FaradayIO import faradaybasicproxyio
from FaradayIO import faradaycommands
from FaradayIO import telemetryparser

#Variables
local_device_callsign = 'kb1lqd'  # Should match the connected Faraday unit as assigned in Proxy configuration
local_device_node_id = 1  # Should match the connected Faraday unit as assigned in Proxy configuration

#Start the proxy server after configuring the configuration file correctly
#Setup a Faraday IO object
faraday_1 = faradaybasicproxyio.proxyio()
faraday_cmd = faradaycommands.faraday_commands()
faraday_parser = telemetryparser.TelemetryParse()

# Get only a single waiting packets on the Telemetry port (assuming faraday has been auto-transmitting telemetry
# packets). GET() returns a list of all packets received on port (in JSON dictionary format). Argument limit=1 will
# only get a single data packet from proxy even if there are more waiting. The default value is None and ALL packets
# would be returned.
print "Getting the latest telemetry from Faraday!"

#Wait up to 10 seconds for the unit to respond to the command.
rx_telem_data = faraday_1.GETWait(local_device_callsign, local_device_node_id, faraday_1.TELEMETRY_PORT, sec_timeout = 10, limit=1) #Will block and wait for given time until a packet is recevied

print "\nThe Recevied data contains " + str(len(rx_telem_data)) + " packet(s) encoded in BASE64"

#Decode the packet in list from BASE 64 to a RAW bytesting
rx_telem_pkt_decoded = faraday_1.DecodeRawPacket(rx_telem_data[0]['data']) #  JSON returned as list and use [0] to directly use the first (and only in this example due to "limit = 1") JSON list item
print "\nThe first telemetry packet is:"
print "\nAs Received BASE64:"
print rx_telem_data[0]['data']
print "\nDecoded:"
print repr(rx_telem_data)

#Unpack the telemetry datagram containing the standard "Telemetry Packet #3" packet
rx_telemetry_datagram = faraday_parser.UnpackDatagram(rx_telem_pkt_decoded, debug = True) #Debug is ON
#Extract just the data packet portion of the JSON dictionary
rx_telemetry_packet_payload = rx_telemetry_datagram['PayloadData']

print "\nThe telemetry packet payload data:\n"

#Extract the exact debug packet from longer datagram payload (Telemetry Packet #2)
rx_telemetry_packet_extracted = faraday_parser.ExtractPaddedPacket(rx_telemetry_packet_payload, faraday_parser.packet_3_len)

#Parse the Telemetry #3 packet
rx_telemetry_packet_parsed = faraday_parser.UnpackPacket_3(rx_telemetry_packet_extracted, True) #Debug ON


print "************************************"
print "\nQuit with ctrl+c"
while(True):
    #Loop until user presses ctrl+c so they can read response
    time.sleep(1)
    pass


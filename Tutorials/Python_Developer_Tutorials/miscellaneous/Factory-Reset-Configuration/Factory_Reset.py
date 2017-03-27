#Imports - General

import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../../Faraday_Proxy_Tools")) #Append path to common tutorial FaradayIO module

#Imports - Faraday Specific
from FaradayIO import faradaybasicproxyio
from FaradayIO import faradaycommands
from FaradayIO import telemetryparser

import time


#Variables
local_device_callsign = 'REPLACEME'  # Should match the connected Faraday unit as assigned in Proxy configuration
local_device_node_id = 0  # Should match the connected Faraday unit as assigned in Proxy configuration

#Start the proxy server after configuring the configuration file correctly
#Setup a Faraday IO object
faraday_1 = faradaybasicproxyio.proxyio()
faraday_cmd = faradaycommands.faraday_commands()
faraday_parser = telemetryparser.TelemetryParse()


############
## Telemetry
############

def get_telemetry():
    #Flush old data from UART service port
    faraday_1.FlushRxPort(local_device_callsign, local_device_node_id, faraday_1.TELEMETRY_PORT)

    #Command UART Telemetry Update NOW
    faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, faraday_cmd.CommandLocalUARTFaradayTelemetry())

    #Wait up to 1 second for the unit to respond to the command. NOTE: GETWait will return ALL packets received if more than 1 packet (likley not in THIS case)
    rx_telem_data = faraday_1.GETWait(local_device_callsign, local_device_node_id,faraday_1.TELEMETRY_PORT, 1) #Will block and wait for given time until a packet is recevied

    #Decode the first packet in list from BASE 64 to a RAW bytesting
    rx_telem_pkt_decoded = faraday_1.DecodeRawPacket(rx_telem_data[0]['data'])

    #Unpack the telemetry datagram containing the standard "Telemetry Packet #3" packet
    rx_telemetry_datagram = faraday_parser.UnpackDatagram(rx_telem_pkt_decoded) #Debug is OFF
    rx_telemetry_packet = rx_telemetry_datagram['PayloadData']

    #Extract the exact debug packet from longer datagram payload (Telemetry Packet #3)
    rx_telemetry_datagram_extracted = faraday_parser.ExtractPaddedPacket(rx_telemetry_packet, faraday_parser.packet_3_len)

    #Parse the Telemetry #3 packet
    rx_telemetry_packet_parsed = faraday_parser.UnpackPacket_3(rx_telemetry_datagram_extracted, debug = True) #Debug ON

    print "Parsed packet dictionary:", rx_telemetry_packet_parsed

def factory_reset_configuration():
    #Command  Unit Factory Reset
    faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, faraday_cmd.CommandLocalFactoryResetConfiguration())


# Get pre-reset general telemetry
get_telemetry()

# Factory reset device
factory_reset_configuration()

time.sleep(3)

# Get post-reset general telemetry
get_telemetry()

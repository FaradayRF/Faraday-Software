# Basic introduction to proxy interaction with Faraday using Python.
# - Getting received data from telemetry
# - Parsing received data

#Imports
from Basic_Proxy_IO import faradaybasicproxyio
from Basic_Proxy_IO import faradaycommands
from Basic_Proxy_IO import telemetryparser

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
if(rx_telem_data == False):
    #No packets recieved yet, command the unit to transmit a UART telemetry packet NOW
    faraday_1.POST(local_device_callsign, local_device_node_id, FARADAY_CMD_UART_PORT, faraday_cmd.CommandLocalUARTUpdateNow())

    #Wait up to 1 second for the unit to respond to the command. NOTE: GETWait will return ALL packets received if more than 1 packet (likley not in THIS case)
    rx_telem_data = faraday_1.GETWait(local_device_callsign, local_device_node_id, FARADAY_TELEMETRY_UART_PORT, 1, False) #Will block and wait for given time until a packet is recevied

print "\nThe Recevied data contains " + str(len(rx_telem_data)) + " packet(s) encoded in BASE64"
print rx_telem_data

#Decode the first packet in list from BASE 64 to a RAW bytesting
rx_telem_pkt_decoded = faraday_1.DecodeJsonItemRaw(rx_telem_data[0]['data'])
print "\nThe first telemetry packet is:"
print "\nAs Received BASE64:"
print rx_telem_data[0]['data']
print "\nDecoded:"
print repr(rx_telem_pkt_decoded)

#Unpack the telemetry datagram containing the standard "Telemetry Packet #3" packet
rx_telemetry_datagram = faraday_parser.UnpackDatagram(rx_telem_pkt_decoded, True) #Debug is ON
rx_telemetry_packet = rx_telemetry_datagram[3]

#Extract the exact debug packet from longer datagram payload (Telemetry Packet #2)
rx_telemetry_packet_extracted = faraday_parser.ExtractPaddedPacket(rx_telemetry_packet, faraday_parser.packet_3_len)

#Parse the Telemetry #3 packet
rx_telemetry_packet_parsed = faraday_parser.UnpackPacket_3(rx_telemetry_packet_extracted, True) #Debug ON

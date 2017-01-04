
# Tutorial - Proxy Interaction Basics

In this tutorial the three Telemetry packets available from Faraday are queried, parsed, and displayed. This makes use of the telemetry parsing tool module and more detailed information can be found in the telemetry application and packet definition documentation.

##Telemetry Packet Types

* **System Operation Information**
  * Current operation details (frequency, power levels, etc...)
* **Device Debug Information**
  * Non-volatile system failure/reset counters useful for debugging
* **Main Faraday Telemetry**
  * Faraday telemetry that include all peripheral data (i.e GPS, ADC's, etc...) 

#Running The Tutorial Example Script

## Start The Proxy Interface

Following the [Configuring Proxy](../../0-Welcome_To_Faraday/Configuring_Proxy/) tutorial configure, start, and ensure a successful connection to a locally (USB) connected Faraday digital radio.


## Tutorial Output Examples

below is a screen-shot of the partial output of the tutorial script when run in a python interpreter (PyCharm). The script 

![Example Tutorial Operation](Images/Output.png "Example Tutorial Operation")

# Code Overview

## Code - Parse Telemetry Packet Type #1 (System Operation)

The code below first uses `FlushRxPort()` to remove all prior data in the buffer and is imediately followed by `POST()` which the argument including ` faraday_cmd.CommandLocalSendTelemDeviceSystemSettings()` which commands the locally connected Faraday unit to send a Telemetry packet type #1 over UART to the proxy server. This simple example does not check for the packet type prior to parsing and  flushing all prior data to commanding packet type #1 being sent ensures that the next retrieved data from the proxy FIFO is packet type #1.

`faraday_parser.UnpackDatagram()` extracts the telemetry packet from the main encapsulation packet (datagram) and `rx_debug_data_datagram['PayloadData']` contains the telemetry packet type #1 packet to be parsed. The datagram payload is fixed length, `ExtractPaddedPacket(rx_settings_packet, faraday_parser.packet_1_len)` truncates just the packet needed using pre-defined packet lengths from the telemetry parser class module object. `UnpackPacket_1()` then parses the telemetry packet and `debug = True` causes the parser to print the fields directly to the screen and returns a dictionary of the parsed results.

`freq0_reverse_carrier_calculation()` uses the received system operating information to calculate the frequency of the CC430 radio in MHz.



```python
############
## System Settings
############

#Flush old data from UART service port
faraday_1.FlushRxPort(local_device_callsign, local_device_node_id, faraday_1.TELEMETRY_PORT)

#Command UART Telemetry Update NOW
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, faraday_cmd.CommandLocalSendTelemDeviceSystemSettings())

#Wait up to 1 second for the unit to respond to the command. NOTE: GETWait will return ALL packets received if more than 1 packet (likley not in THIS case)
rx_settings_data = faraday_1.GETWait(local_device_callsign, local_device_node_id,faraday_1.TELEMETRY_PORT, 1, False) #Will block and wait for given time until a packet is recevied

#Decode the first packet in list from BASE 64 to a RAW bytesting
rx_settings_pkt_decoded = faraday_1.DecodeRawPacket(rx_settings_data[0]['data'])

#Unpack the telemetry datagram containing the standard "Telemetry Packet #3" packet
rx_settings_datagram = faraday_parser.UnpackDatagram(rx_settings_pkt_decoded, debug = False) #Debug is ON
rx_settings_packet = rx_settings_datagram['PayloadData']

#Extract the exact debug packet from longer datagram payload (Telemetry Packet #2)
rx_settings_pkt_extracted = faraday_parser.ExtractPaddedPacket(rx_settings_packet, faraday_parser.packet_1_len)

#Parse the Telemetry #3 packet
rx_settings_parsed = faraday_parser.UnpackPacket_1(rx_settings_pkt_extracted, debug = True) #Debug ON

# Print current Faraday radio frequency
faraday_freq_mhz = cc430radioconfig.freq0_reverse_carrier_calculation(rx_settings_parsed['RF_Freq_2'], rx_settings_parsed['RF_Freq_1'], rx_settings_parsed['RF_Freq_0'])
print "Faraday's Current Frequency:", str(faraday_freq_mhz)[0:7], "MHz"
```


## Code - Parse Telemetry Packet Type #2 (Device Debug)

The actions needed to flush, command, unpack from the telemetry datagram, and parse telemetry packet type #2 are the same as previously exampled except that parsing routines for packet type #2 are specificaly used.  Notably `CommandLocalSendTelemDeviceDebugFlash()` and `UnpackPacket_2()` command the sending / parsing of telemetry packet type #2 respectively.

```python
############
## Debug
############

#Flush old data from UART service port
faraday_1.FlushRxPort(local_device_callsign, local_device_node_id, faraday_1.TELEMETRY_PORT)

#Command UART Telemetry Update NOW
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, faraday_cmd.CommandLocalSendTelemDeviceDebugFlash())

#Wait up to 1 second for the unit to respond to the command. NOTE: GETWait will return ALL packets received if more than 1 packet (likley not in THIS case)
rx_debug_data = faraday_1.GETWait(local_device_callsign, local_device_node_id,faraday_1.TELEMETRY_PORT, 1, False) #Will block and wait for given time until a packet is recevied

#Decode the first packet in list from BASE 64 to a RAW bytesting
rx_debug_data_pkt_decoded = faraday_1.DecodeRawPacket(rx_debug_data[0]['data'])

#Unpack the telemetry datagram containing the standard "Telemetry Packet #3" packet
rx_debug_data_datagram = faraday_parser.UnpackDatagram(rx_debug_data_pkt_decoded, False) #Debug is ON
rx_debug_data_packet = rx_debug_data_datagram['PayloadData']

#Extract the exact debug packet from longer datagram payload (Telemetry Packet #2)
rx_debug_data_pkt_extracted = faraday_parser.ExtractPaddedPacket(rx_debug_data_pkt_decoded, faraday_parser.packet_2_len)

#Parse the Telemetry #3 packet
rx_debug_data_parsed = faraday_parser.UnpackPacket_2(rx_debug_data_pkt_extracted, debug = True) #Debug ON
```


## Code - Parse Telemetry Packet Type #3 (Main Faraday Telemetry)

The actions needed to flush, command, unpack from the telemetry datagram, and parse telemetry packet type #3 are the same as previously exampled except that parsing routines for packet type #2 are specificaly used.  Notably `CommandLocalUARTFaradayTelemetry()` and `UnpackPacket_3()` command the sending / parsing of telemetry packet type #3 respectively.

`rx_telemetry_packet_parsed` is printed after reception and parsing to example the raw parsed dictionary item returned from the parsing function(s).

```python
############
## Telemetry
############

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

```
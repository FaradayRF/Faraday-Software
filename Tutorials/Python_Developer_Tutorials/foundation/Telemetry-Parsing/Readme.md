
# Tutorial - Proxy Interaction Basics

This tutorial introduces telemetry packets available from Faraday's telemetry application. Although beaconing mode(s) allow automatic transmission of telemetry this tutorial commands the local device to send the respective packet.The telemetry packets are queried, parsed, and displayed. This makes use of the telemetry parsing tool module.

##Telemetry Packet Types

* **System Operation Information**
  * Current operation details (frequency, power levels, etc...)
* **Device Debug Information**
  * Non-volatile system failure/reset counters useful for debugging
* **Main Faraday Telemetry**
  * Faraday telemetry that include all peripheral data (i.e GPS, ADC's, etc...) 


### Prerequisites
* Properly configured and connected proxy
  * Single Faraday

#Running The Tutorial Example Script

## Configuration

* Open `configuration-template.ini` with a text editor
* Update `CALLSIGN` Replace ```REPLACEME``` to match the callsign of the Faraday unit **as assigned** in proxy
* Update `NODEID` to match the callsign node ID of the Faraday unit **as assigned** in proxy
* Save the file as `configuration.ini`

## Tutorial Output Examples

Shown below is the output of the tutorial script when run in a python interpreter (PyCharm). 

``` Python
--- Telemetry Packet #1 ---
Index[0]: RF Freq 2 35
Index[1]: RF Freq 1 44
Index[2]: RF Freq 0 78
Index[3]: RF Power Bitmask 20
Faraday's Current Frequency: 914.499 MHz


18
--- Telemetry Packet #2 ---
Index[0]: Boot Count 93
Index[1]: Reset Count 0
Index[2]: Brownout reset counter 0
Index[3]: Reset / Non-maskable Interrupt counter 0
Index[4]: PMM Supervisor Low counter 0
Index[5]: PMM Supervisor High counter 0
Index[6]: PMM Supervisor Low - OVP counter 0
Index[7]: PMM Supervisor High - OVP counter 0
Index[8]: Watchdog timeout counter 0
Index[9]: Flash key violation counter 0
Index[10]: FLL Unlock counter 0
Index[11]: Peripheral / Config counter 0
Index[12]: Access violation counter 0
Index[13]: Firmware Revision 232278577 232278577


--- Telemetry Packet #3 ---
Source Callsign KB1LQD
Source Callsign Length 6
Source Callsign ID 1
Destination Callsign KB1LQD
Destination Callsign Length 6
Destination Callsign ID 1
RTC Second 16
RTC Minute 16
RTC Hour 8
RTC Day 20
RTC Day Of Week 1
RTC Month 2
Year 57607
GPS Lattitude 1234.5678
GPS Lattitude Direction N
GPS Longitude 12345.5678
GPS Longitude Direction W
GPS Altitude 6.100000
GPS Altitude Units M
GPS Speed 1.150
GPS Fix 1
GPS HDOP 1.72
GPIO State Telemetry 192
IO State Telemetry 7
RF State Telemetry 0
ADC 0 2395
ADC 1 2350
ADC 2 2261
ADC 3 2247
ADC 4 2185
ADC 5 2186
VCC 0
CC430 Temperature 23
ADC 8 2854
HAB Automatic Cutdown Timer State Machine State 0
HAB Cutdown Event State Machine State 0
HAB Automatic Cutdown Timer Trigger Time 7200
HAB Automatic Cutdown Timer Current Time 0
EPOCH 1487578577.25
Parsed packet dictionary: {'RFSTATE': 0, 'GPIOSTATE': 192, 'VCC': 0, 'RTCMIN': 16, 'SOURCECALLSIGN': 'KB1LQD', 'GPSLONGITUDE': '11826.1698', 'SOURCEID': 1, 'RTCYEAR': 57607, 'ADC1': 2350, 'BOARDTEMP': 23, 'DESTINATIONID': 1, 'EPOCH': 1487578577.25, 'RTCSEC': 16, 'GPSLATITUDE': '3400.0243', 'IOSTATE': 7, 'GPSSPEED': '1.150', 'RTCDAY': 20, 'RTCMONTH': 2, 'GPSFIX': '1', 'RTCHOUR': 8, 'HABTIMER': 0, 'GPSHDOP': '1.72', 'ADC3': 2247, 'HABTRIGGERTIME': 7200, 'DESTINATIONCALLSIGNLEN': 6, 'GPSLONGITUDEDIR': 'W', 'DESTINATIONCALLSIGN': 'KB1LQD', 'ADC4': 2185, 'ADC5': 2186, 'SOURCECALLSIGNLEN': '6', 'GPSALTITUDE': '6.100000', 'ADC0': 2395, 'GPSLATITUDEDIR': 'N', 'ADC2': 2261, 'HABTIMERSTATE': 0, 'RTCDOW': 1, 'HABCUTDOWNSTATE': 0, 'ADC8': 2854, 'GPSALTITUDEUNITS': 'M'}
************************************

Quit with ctrl+c
```

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
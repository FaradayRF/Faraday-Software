Basic Input/Output With Faraday IO
==================================

This tutorial will teach how to perform basic input and output functionality using the FaradayIO toolset. Retrieving data from the telemetry application preinstalled onto faraday is goal of this tutorial. Full example code is available in the GIT repository.

Prerequisites
-------------

Ensure that these steps and configurations have been performed prior to using the tutorial.

* **Faraday Proxy Configuration INI File**
 * In section [telemetry] set *autoretrieve' = False
* **Faraday Proxy**
 * Successfully start the proxy service
 
 
Tutorial
========

Toolset Module Imports And Initializations
------------------------------------------

The first lines of the example perform basic import and setup of the supplied Faraday toolsets. These tools allow easy input/output, predefined command packets and creation functions, and a packet parsing tool.

.. code-block:: python

	#Imports
	from Basic_Proxy_IO import faradaybasicproxyio
	from Basic_Proxy_IO import faradaycommands
	from Basic_Proxy_IO import telemetryparser
	
	#Definitions
	FARADAY_TELEMETRY_UART_PORT = 5
	FARADAY_CMD_UART_PORT = 2
	
Several toolset modules were imported and they provide functionality such as:

* **faradaybasicproxyio:** Basic Faraday Proxy GET and POST module for input and output operations
* **faradaycommands:** Command packet creation toolset and pre-defined common commands
* **telemetryparser:** Faraday "Telemetry" parsing tool

The definitions are "port" numbers that define the Faraday Transport Layer (Layer 4) port number that ties to the intended application. There is also a predefined list in the class object of faradaybasicproxyio.

Local Device And Tool Object Initializations
--------------------------------------------

.. code-block:: python

	#Variables
	local_device_callsign = 'kb1lqd'
	local_device_node_id = 1

	#Start the proxy server after configuring the configuration file correctly
	#Setup a Faraday IO object
	faraday_1 = faradaybasicproxyio.proxyio()
	faraday_cmd = faradaycommands.faraday_commands()
	faraday_parser = telemetryparser.TelemetryParse()

The code above defines the intended local device parameters (callsign and ID) to identify the intended local device to direct data to and from over the proxy. This allows for multiple local devices to be connected to over a single proxy server and makes learning/testing RF functionality that involved TX and RX easier. Two proxy programs can be run instead and this is handled in a later tutorial until proxy is upgraded.

.. note: At current time of writing Faraday Proxy does not use the local callsign and ID to match a local device to. It is ignored. Only a single unit can connect to a proxy.

Several class objects are then created that are later used to perform the modules intended purposes such as decoding recevied data.

Retrieve Data With The GET() Function
-------------------------------------

.. code-block:: python

	#Get all waiting packets on the Telemetry port (assuming faraday has been auto-transmitting telemetry packets). Get returns a list of all packets received on port (in JSON dictionary format).
	print "Getting the latest telemetry from Faraday!"
	rx_telem_data = faraday_1.GET( local_device_callsign, local_device_node_id, FARADAY_TELEMETRY_UART_PORT)

The most basic method on getting data from a Faraday Transport Layer "port" is to use the GET() function. The function returns all data packets received and waiting in a queue, if none are waiting the function returns False. The defined local callsign and ID of the device to be interacted with locally are passed along with the intended Faraday Transport port to retrieve data from.

Retrieve Data With The GETWait() Function If Needed
---------------------------------------------------

.. code-block:: python

	#Check if no received data waiting in Queue
	if(rx_telem_data == False):
		#No packets recieved yet, command the unit to transmit a UART telemetry packet NOW
		faraday_1.POST(local_device_callsign, local_device_node_id, FARADAY_CMD_UART_PORT, faraday_cmd.CommandLocalUARTUpdateNow())

		#Wait up to 1 second for the unit to respond to the command. NOTE: GETWait will return ALL packets received if more than 1 packet (likley not in THIS case)
		rx_telem_data = faraday_1.GETWait(local_device_callsign, local_device_node_id, FARADAY_TELEMETRY_UART_PORT, 1, False) #Will block and wait for given time until a packet is recevied

	print "\nThe Recevied data contains " + str(len(rx_telem_data)) + " packet(s) encoded in BASE64"
	print rx_telem_data

Depending on Faraday telemtry application settings on the CC430 itself there may be no packets waiting to be retrieved from Proxy. The code above detects this condition and uses a predefined command to tell the local Faraday unit to send its Telemetry (Telemetry Packet #3) over UART now. You'll notice a new function being used: GETWait(), this function abstracts the GET() function and if no data is waiting to be retrieve the program blocks and loops for the specified duration and returns either the retrieve data or False. This is useful because Faraday obeys the laws of physics and cannot respond at the speed of light and therefor periodically checking for new data allows the program to un-block with data as soon as possible. Using debug modes of GETWait also allow optimizations to the protocol to be measured.

Data retrieve is returned in JSON format and BASE64 encoded. The code block below shows a return of 4 data packets from a single GET() or GETWait() call.

.. code-block:: python

	[{u'data': u'AwBhS0IxTFFEBXsDBgdLQjFMUUQFewMGBxUrFhIACeAHMzM1Mi40MjExTjExODIyLjYwNDFXMzQuNjIwMDBNMC4yNzAyMC45MAAXYAjcCKgICQetB/IIHQAAAB4LBQAAHCAAAAAAAABGBgdLQjFMUUQAAAAGBxQqFhTu',
	  u'port': 5},
	 {u'data': u'AwBhS0IxTFFEAADFBgdLQjFMUUSyAAAGByorFhIACeAHMzM1Mi40MjEyTjExODIyLjYwNDBXMzQuNjIwMDBNMC4xNDAyMC45MAAXYAjaCKYIBweoB+0IGwAAAB4LBgAAHCAAAAAAAAAAAEYGB0tCMUxRRGLEAACXIxbe',
	  u'port': 5},
	 {u'data': u'AwBhS0IxTFFEBXsDBgdLQjFMUUQAAMUGBwMsFhIACeAHMzM1Mi40MjA3TjExODIyLjYwMzJXMzQuNjIwMDBNMC4yMzAyMC45MAAXYAjdCKYICQemB+oIHAAAAB4K/wAAHCAAAAAAAAAAAAAARgYHS0IxTFFEYsQAABbN',
	  u'port': 5},
	 {u'data': u'AwBhS0IxTFFEAACgBgdLQjFMUUSyAAAGBxgsFhIACeAHMzM1Mi40MjA2TjExODIyLjYwMzJXMzQuNjIwMDBNMC4yMzAyMC45MAAXYAjeCKcICAekB+YIHAAAAB8LCAAAHCAAANgGB0tCMUxRRP8AAAYHFiwWEgCXIxeN',
	  u'port': 5}]

	  
**JSON Data Dictionary Keys**
* **data**: BASE64 encoded data packet
* **port**: The Faraday Transport Layer "Port" number the data was retrieved from
  
  
Telemetry Datagram And Packet Decoding
--------------------------------------
.. code-block:: python

	#Decode the first packet in list from BASE 64 to a RAW bytesting
	rx_telem_pkt_decoded = faraday_1.DecodeJsonItemRaw(rx_telem_data[0]['data'])
	print "\nThe first telemetry packet is:"
	print "\nAs Received BASE64:"
	print rx_telem_data[0]['data']
	print "\nDecoded:"
	print repr(rx_telem_pkt_decoded)
	
Data received will be in JSON format and the data will be encoded in BASE64. BASE64 is only used on the Proxy to make binary data web-safe and is NOT used over Faraday itself. The code block above shows the first packet (index = 0) data being extracted from the JSON dictionary:

.. code-block:: python

	rx_telem_data[0]['data']
	
The BASE64 encoded data is then decoded using the FaradayIO module tool provided.

.. code-block:: python

	faraday_1.DecodeJsonItemRaw(rx_telem_data[0]['data'])
	

The code below will finish up the tutorial by parsing the telemtry packet.

.. code-block:: python

	#Unpack the telemetry datagram containing the standard "Telemetry Packet #3" packet
	rx_telemetry_datagram = faraday_parser.UnpackDatagram(rx_telem_pkt_decoded, True) #Debug is ON
	rx_telemetry_packet = rx_telemetry_datagram[3]

	#Extract the exact debug packet from longer datagram payload (Telemetry Packet #2)
	rx_telemetry_packet_extracted = faraday_parser.ExtractPaddedPacket(rx_telemetry_packet, faraday_parser.packet_3_len)

	#Parse the Telemetry #3 packet
	rx_telemetry_packet_parsed = faraday_parser.UnpackPacket_3(rx_telemetry_packet_extracted, True) #Debug ON


Telemetry packets are supplied by the "Telemetry" application and following the OSI model for network stacks it too has its own packet definition! Every Telemetery packet is encapsulated within a datagram that indicates key parameters such as length, packet type, and a checksum for error detection and correction. It should be noted that for simplicity of the first network stack on Faraday applications handle error detection and correction themselves.

The 3rd index of the parsed datagram list contains the datagram payload which happens to be the actual telemetry packet we intend to decode. Telemetry packets are simple fixed length datagrams and packets not using the entire size must be extracted (i.e. cut out). The last operation using the Faraday Telemetry Parsing toolset to parse the entire telemetry packet (Telemetry Packet #3) into a list. Using a "debug" argument of True forces the parsing tools to print a human readable output of the parsed data.

.. code-block:: python

	--- Telemetry Datagram ---
	Telemetry Packet Type: 3
	Telemetry RF Source: 0
	Telemetry Payload Length: 97
	Telemetry Packet 16 Bit Checksum: 5718
	Telemetry Packet Payload Data: 'KB1LQD\x05{\x03\x06\x07KB1LQD\x05{\x03\x06\x07\x12\x0b\x06\x13\x01\t\xe0\x073352.4203N11822.6005W34.30000M0.22021.24\x00\x07`\x06\xf8\x05e\x04\xcc\x04\x86\x04\x87\x04s\x00\x00\x00\x1c\x0b\x03\x00\x00\x1c \x00\x00\x00\x00\x00\x00\xd8\x06\x07KB1LQD\xff\x00\x00\x06\x07\x1e\n\x06'


	--- Telemetry Packet #3 ---
	Index[0]: Source Callsign KB1LQD{
	Index[1]: Source Callsign Length 6
	Index[2]: Source Callsign ID 7
	Index[3]: Destination Callsign KB1LQD{
	Index[4]: Destination Callsign Length 6
	Index[5]: Destination Callsign ID 7
	Index[6]: RTC Second 18
	Index[7]: RTC Minute 11
	Index[8]: RTC Hour 6
	Index[9]: RTC Day 19
	Index[10]: RTC Day Of Week 1
	Index[11]: RTC Month 9
	Index[12]: Year 57351
	Index[13]: GPS Lattitude 3352.4203
	Index[14]: GPS Lattitude Direction N
	Index[15]: GPS Longitude 11822.6005
	Index[16]: GPS Longitude Direction W
	Index[17]: GPS Altitude 34.30000
	Index[18]: GPS Altitude Units M
	Index[19]: GPS Speed 0.220
	Index[20]: GPS Fix 2
	Index[21]: GPS HDOP 1.24
	Index[22]: GPIO State Telemetry 0
	Index[23]: RF State Telemetry 7
	Index[24]: ADC 0 96
	Index[25]: ADC 1 1784
	Index[26]: ADC 2 1381
	Index[27]: ADC 3 1228
	Index[28]: ADC 4 1158
	Index[29]: ADC 5 1159
	Index[30]: ADC 6 1139
	Index[31]: CC430 Temperature 0
	Index[32]: ADC 8 28
	Index[33]: N/A Byte 2819
	Index[34]: HAB Automatic Cutdown Timer State Machine State 0
	Index[35]: HAB Cutdown Event State Machine State 0
	Index[36]: HAB Automatic Cutdown Timer Trigger Time 7200
	Index[37]: HAB Automatic Cutdown Timer Current Time 0

 
Tutorial Example Code
=====================

The entire main code of the example is shown below.

.. code-block:: python

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




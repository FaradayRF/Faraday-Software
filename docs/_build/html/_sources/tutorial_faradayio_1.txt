Tutorial 1 - Local Command and Control
======================================

This tutorial will walk you through basic local device command and control as well as remote device command and control over RF. It is important to note that this tutorial's command and control is provided by an "application" operating on the Faraday CC430 and we are issuing packets that invoke actions to occure.


Tutorial 1a - Basic Local Device IO Commands
============================================

Perfoming basic input and output commanding involves very few operations, this is made simpler by common actions such as toggling and LED have had pre-defined command functions created for them. Lets begin with importing and configuring FaradayIO module that connects to the proxy server.

https://github.com/FaradayRF/Faraday-Software/blob/master/Tutorials/FaradayIO/Tutorial_1/Tutorial_Proxy_1a.py

.. code-block:: python

	#imports
	from FaradayIO import faradaybasicproxyio
	from FaradayIO import faradaycommands
	from FaradayIO import telemetryparser
	from FaradayIO import gpioallocations

	import time

	#Definitions


	#Variables
	local_device_callsign = 'kb1lqd'
	local_device_node_id = 1

	#Start the proxy server after configuring the configuration file correctly
	#Setup a Faraday IO object
	faraday_1 = faradaybasicproxyio.proxyio() #default proxy port
	faraday_cmd = faradaycommands.faraday_commands()


toggling LED 1 and LED 2 on and off using both predefined command creation functions and implementing the base GPIO bitmask command function. Using the bitmask command function allows multiple GPIO's to be toggled in a single command. 

The command application *contains its own OSI layer packet protocol* and this is defined in the supplied documentation. Each command is encapsulated in a "datagram" and the corresponding packet type indicated in the datagram will tell Faraday how to decode the payload supplied. This allows functions to both perform a simple action and pass data along with the command in various configurations.

.. code-block:: python

	#Turn LED 1 ON LOCAL
	command = faraday_cmd.CommandLocalGPIOLED1On()
	faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)
	time.sleep(1)

	#Turn LED 1 OFF LOCAL
	command = faraday_cmd.CommandLocalGPIOLED1Off()
	faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)

	#Turn LED 2 ON LOCAL
	command = faraday_cmd.CommandLocalGPIOLED2On()
	faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)
	time.sleep(1)

	#Turn LED 2 OFF LOCAL
	command = faraday_cmd.CommandLocalGPIO(0, 0, 0, gpioallocations.LED_2, 0, 0) #This examples how the non predefined LED GPIO commanding is created. Multiple GPIO's can be toggled at once using ||'s
	faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)
	time.sleep(1) #Delay so it is obvious that both LED's turn on at the same time in the next command

	#Turn Both LED 1 and LED 2 ON simultaneously
	command = faraday_cmd.CommandLocalGPIO((gpioallocations.LED_1|gpioallocations.LED_2), 0, 0, 0, 0, 0)
	faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)
	time.sleep(1)

	#Turn Both LED 1 and LED 2 OFF simultaneously
	command = faraday_cmd.CommandLocalGPIO(0, 0, 0, (gpioallocations.LED_1|gpioallocations.LED_2), 0, 0)
	faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)

Sending a command to turn GPIO's on and off is pretty straightforward. What if we wanted to simply send data to Faraday and ECHO that data back?

Using the defined "ECHO" command all payload bytes are re-transmitted over UART (and subsequently the proxy server) back to the originating proxy.

The first step is to create the data message to be sent, in this example it is text but it could be raw binary data if desired.

.. code-block:: python

	#Use the general command library to send a text message to the Faraday UART "ECHO" command. Will only ECHO a SINGLE packet. This will send the payload of the message back (up to 62 bytes, this can be updated in firmware to 124!)
	originalmsg = "This will ECHO back on UART" #Cannot be longer than max UART payload size!
	command = faradaycommands.commandmodule.create_command_datagram(faraday_cmd.CMD_ECHO, originalmsg)
	faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)


The command application uses its own "Faraday Transport Layer Port Number" and operates in a different set of FIFO queues than the telemetry application used in the last tutorial. Allowing applications a basic isolation like this is a powerful tool that seperates all programs into their own packet "streams" without worry of conflicting with other programs packets.

Once the command is transmitted the ECHO'd packet will be ready to recieve from the proxy server shortly. As Faraday is optimized the delay between command and reception (or actions in general) will be improved. Using the "GetWait()" function is an ideal method to block until the data is received (only if the queue is empty).

.. code-block:: python

	#Retrive waiting data packet in UART Transport service number for the COMMAND application (Use GETWait() to block until ready or return False).
	rx_echo_raw = faraday_1.GETWait(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, 1, False) #Wait for up to 1 second

	#Now parse data again
	b64_data = rx_echo_raw[0]['data']
	echo_decoded = faraday_1.DecodeJsonItemRaw(b64_data)

	#Display information
	print "Original Message: ", originalmsg
	print "RAW Received BASE64 ECHO'd Message:", b64_data
	print "Decoded received ECHO'd Message:", echo_decoded #Note that ECHO sends back a fixed packed regardless. Should update to send back exact length.

Running this example in PyScripter produces the output:

.. code-block:: python

	*** Remote Interpreter Reinitialized  ***
	>>> 
	Original Message:  This will ECHO back on UART
	RAW Received BASE64 ECHO'd Message: VGhpcyB3aWxsIEVDSE8gYmFjayBvbiBVQVJUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/////////////////////////////////////////////////////////////////////////////////
	Decoded received ECHO'd Message: This will ECHO back on UART
	>>> 

Tutorial 1b - Commanding And Parsing All Telemetry Packets
==========================================================

**Tutorial Example Script:** https://github.com/FaradayRF/Faraday-Software/blob/master/Tutorials/FaradayIO/Tutorial_1/Tutorial_Proxy_1b.py

The purpose of this tutorial is to command a local Faraday unit to transmit all 3 current types of telemetry packets and how to use the supplied parsing tools to decode them. 

.. note:: Make sure that Faraday Proxy is successfully running prior to running the example script!

- Command transmisson of different telemetry packets
	- Packet Type #1: System Settings (i.e. Frequency, RF power...)
	- Packet Type #2: Device Debug Information (Boot counter, reset counters, error flags, etc...)
	- Packet Type #3: Standard Faraday Telemetry (ADC, GPIO, GPS, etc...)
- Using FaradayIO parsing tools to decode received telemetry packets from the proxy server
	- Introduce the "Flush" function in FaradayIO
	- Extracting smaller packets from larger datagram payloads
- Overview of the telemetry packet formats and data available

Example Notes
-------------

**Telemtry Packet #3 - Standard Telemetry**

This telemetry packet is the main telemetry that most people will want from a Faraday as it contains the ADC, GPIO, GPS, and other information.

Below is an example of output data when the the debug argument is equal to True thus printing parsing information for educational purposes. This function otherwise returns a list of parsed elements using the standard python Struct module.

.. code-block:: python

	>>> 
	--- Telemetry Packet #3 ---
	Index[0]: Source Callsign KB1LQD“*
	Index[1]: Source Callsign Length 6
	Index[2]: Source Callsign ID 7
	Index[3]: Destination Callsign KB1LQD
	Index[4]: Destination Callsign Length 6
	Index[5]: Destination Callsign ID 7
	Index[6]: RTC Second 14
	Index[7]: RTC Minute 30
	Index[8]: RTC Hour 17
	Index[9]: RTC Day 23
	Index[10]: RTC Day Of Week 5
	Index[11]: RTC Month 9
	Index[12]: Year 57351
	Index[13]: GPS Lattitude 3352.4159
	Index[14]: GPS Lattitude Direction N
	Index[15]: GPS Longitude 11822.6014
	Index[16]: GPS Longitude Direction W
	Index[17]: GPS Altitude 40.26000
	Index[18]: GPS Altitude Units M
	Index[19]: GPS Speed 0.190
	Index[20]: GPS Fix 2
	Index[21]: GPS HDOP 0.94
	Index[22]: GPIO State Telemetry 0
	Index[23]: RF State Telemetry 7
	Index[24]: ADC 0 96
	Index[25]: ADC 1 2237
	Index[26]: ADC 2 2041
	Index[27]: ADC 3 2023
	Index[28]: ADC 4 1928
	Index[29]: ADC 5 1934
	Index[30]: ADC 6 1878
	Index[31]: CC430 Temperature 0
	Index[32]: ADC 8 29
	Index[33]: N/A Byte 2816
	Index[34]: HAB Automatic Cutdown Timer State Machine State 0
	Index[35]: HAB Cutdown Event State Machine State 0
	Index[36]: HAB Automatic Cutdown Timer Trigger Time 7200
	Index[37]: HAB Automatic Cutdown Timer Current Time 0
	('KB1LQD\x93*\x00', 6, 7, 'KB1LQD\x00\x02\x00', 6, 7, 14, 30, 17, 23, 5, 9, 57351, '3352.4159', 'N', '11822.6014', 'W', '40.26000', 'M', '0.190', '2', '0.94', 0, 7, 96, 2237, 2041, 2023, 1928, 1934, 1878, 0, 29, 2816, 0, 0, 7200, 0)
	 14



Below are excerpts and explainations of key points to understand from this 



Tutorial 1 - Local Command and Control
======================================

This tutorial will walk you through basic local device command and control as well as remote device command and control over RF. It is important to note that this tutorial's command and control is provided by an "application" operating on the Faraday CC430 and we are issuing packets that invoke actions to occure.


Tutorial 1a - Basic Local Device IO Commands
============================================

Perfoming basic input and output commanding involves very few operations, this is made simpler by common actions such as toggling and LED have had pre-defined command functions created for them. Lets begin with importing and configuring FaradayIO module that connects to the proxy server.

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


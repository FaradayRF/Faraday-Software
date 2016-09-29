Tutorial 1 - Local Command and Control
======================================

This tutorial will walk you through basic local device command and control as well as remote device command and control over RF. It is important to note that this tutorial's command and control is provided by an "application" operating on the Faraday CC430 and we are issuing packets that invoke actions to occure.

 **Key Points**
 - Basic command application usage
  - Toggle LED GPIOs using both "FaradayIO" predefined commands and the generic GPIO function
  - Send and "ECHO" command and recevied, decode, and display the resulting echo'd message
  

Tutorial Example/Source Code: https://github.com/FaradayRF/Faraday-Software/tree/master/Tutorials/FaradayIO/Tutorial_1
  
Tutorial 1a - Basic Local Device IO Commands
============================================

This simple example tutorial shows the use of the command application's GPIO control functions. The code is well commented and should be self-document.


Notable Key Points
--------------------

Turning ON a GPIO (such as an LED) using the pre-defined functions is very simple as shown below. Note that the "local_device_callsign" and "local_device_node_id" are identifiers to command a specific unit attached to a single computer with multiple Faraday units connected. This will be more useful in later tutorials.

.. code-block:: python

	#Turn LED 1 ON LOCAL
	command = faraday_cmd.CommandLocalGPIOLED1On()
	faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)

The pre-defined functions simply invoke the base GPIO toggling function below. The key point to learn is that a value of LOW (0) performs *no action* and a value of HIGH (1) *performs either a TOGGLE HIGH or TOGGLE LOW* depending on the function arguments. You cannot attempt to toggle HIGH and LOW in a single command. A GPIO header file is provided (gpioallocations.py) that maps the pins on  the CC430 to Faraday functions.	

.. code-block:: python

	#Turn Both LED 1 and LED 2 OFF simultaneously
	command = faraday_cmd.CommandLocalGPIO(0, 0, 0, (gpioallocations.LED_1|gpioallocations.LED_2), 0, 0)
	faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)


After transmitting a command "ECHO" packet with a supplied payload (that will be echo'd) Faraday takes a non-zero amount of time to respond. this is typically slower than the very powerful computer running the Python code and the GetWait() function blocks the script until a data message is received (assumed to be the message inteded).

.. code-block:: python

	#Retrive waiting data packet in UART Transport service number for the COMMAND application (Use GETWait() to block until ready or return False).
	rx_echo_raw = faraday_1.GETWait(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, 1, False) #Wait for up to 1 second


Running this example toggles the LED's on Faraday and produces the following output:

.. code-block:: python

	*** Remote Interpreter Reinitialized  ***
	>>> 
	Original Message:  This will ECHO back on UART
	RAW Received BASE64 ECHO'd Message: VGhpcyB3aWxsIEVDSE8gYmFjayBvbiBVQVJUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/////////////////////////////////////////////////////////////////////////////////
	Decoded received ECHO'd Message: This will ECHO back on UART
	>>> 

Tutorial 1b - Commanding And Parsing All Telemetry Packets
==========================================================

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



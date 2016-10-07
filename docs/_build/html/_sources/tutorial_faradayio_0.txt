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

Tutorial/Example Source Code: https://github.com/FaradayRF/Faraday-Software/tree/master/Tutorials/FaradayIO/Tutorial_0


The example code provided retrieves telemetry data from the locally connected (USB) Faraday Device, decodes the "Proxy Server" JSON BASE64 data, and parses the Faraday Telemetry (Packet Type #3) into a readable format.

Notable Key Points
------------------

When the example code is correctly the output data will be similar to the output below.

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

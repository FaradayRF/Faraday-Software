
# Tutorial - Device Configuration

This tutorial will example how to use the Device Configuration program to both read and write non-volatile Faraday unit configuration using the proxy interface. This configuration data is stored in the CC430 Flash memory and is used to store the units callsign, ID, and other information/default settings.

Reconfiguring the non-volatile memory on Faraday requires using the "Device Configuration" proxy application. The configuration can both be read from the device and reprogrammed. The device application program uses the `faraday_config.ini` file to reprogram a Faraday device, sending a RESTful POST command to the program initiates the reading, parsing, and command creation from the `faraday_config.ini` file.

> NOTE: Device Configuration using the application tool in this tutorial is currently limited to programming a single device at a time.


#Running The Tutorial Example Script

## Start The Proxy Interface

Following the [Configuring Proxy](../../0-Welcome_To_Faraday/Configuring_Proxy/) tutorial configure, start, and ensure a successful connection to a locally (USB) connected Faraday digital radio.


## Execute Tutorial Script


#Code Overview

## Code - Read Current Configuration




#See Also

* [Python Request Module](http://docs.python-requests.org/en/master/)


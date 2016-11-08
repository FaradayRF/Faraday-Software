# Device Configuration Application

The device configuration application is a tool used to read and modify a local Faraday device's configuration settings. This application is parallel to the firmware "Device Configuration" application and performs configuration updates to fields such as:

* Device callsign/ID number
* Default boot settings (GPS, telemetry, etc...)
* Etc

## General Operation

This application interacts directly with the Faraday "Proxy" server and utilizes the command application to send and receive device configuration data. In most cases the device configuration should be READ first prior to editing, this allows the editing of only the fields to be updated and leaving the remaining fields as-is.

All interaction using the RESTful API expect in the RESTful call a unit callsign and ID that is assigned to the COM port regardless of actual callsign and ID of the unit. 

### GET

Issuing a GET to the '/' of the device configuration program will query the unit addressed for its complete Flash memory device configuration contents. For example to query the COM port assigned to kb1lqd-1 on the device configuration program running on port 8002:

`localhost:8002?callsign=kb1lqd&nodeid=1`

This will return a JSON formatted dictionary of the devices configuration. Note that in the future to-do the INI file will be updated to current unit device configuration as noted but this is not currently implemented.

### POST

Issuing a POST to the '/' of the device configuration program will cause the device configuration located in the "faraday_config.INI" to be loaded into the Flash memory of the local device assigned to the passed callsign/id COM port. For example to update the local device "kb1lqd-1" with the contents of the INI file with device configuration on port 8002:

`localhost:8002?callsign=kb1lqd&nodeid=1`

The program will read the INI file, convert it into a valid device configuration update packet, and transmit over the UART the packet and update the unit.

## To-Do

* Add functionality to the GET command that writes the received unit configuration into the INI file so that a unit can easily be modified without a possible large manual editing of the INI file.

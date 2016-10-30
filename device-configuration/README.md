# Device Configuration Application

The device configuration application is a tool used to read and modify a local Faraday device's configuration settings. This application is parallel to the firmware "Device Configuration" application and performs configuration updates to fields such as:

* Device callsign/ID number
* Default boot settings (GPS, telemetry, etc...)
* Etc

## General Operation

This application interacts directly with the Faraday "Proxy" server and utilizes the command application to send and receive device configuration data. In most cases the device configuration should be READ first prior to editing, this allows the editing of only the fields to be updated and leaving the remaining fields as-is.

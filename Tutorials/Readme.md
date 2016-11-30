
# Tutorials

The tutorials series below is meant to introduce a user/developer to:

* Basic setup, configuration, and use of Faraday
* Learn the fundamentals of how to interface to the Faraday Proxy server
* Building more advanced Faraday host computer programs

This series does not yet contain tutorials covering programming the CC430 itself as most people will likely use and program at the host computer python level.

##Welcome To Faraday

* **Introduction To Faraday**
  * What is Faraday and what can you do with it out of the box?
* **[Configuring Proxy](/Tutorials/Tutorials/0-Welcome_To_Faraday/Configuring_Proxy/)**
  * The proxy interface program is the main program needed to interact with Faraday on a Host computer. Learn how to set-up the program to properly connect to Faraday digital radio(s).
* **Saying Hello!**
  * How to connect a Faraday digital radio to a host computer and use built in applications.
* **Where Are You?**
  * A major goal for Faraday is creating interoperable networks, data is data. Using the APRS program telemetry received from the locally connected Faraday is ported over teh  APRS-IS system.
* **Simple Messaging**
  * Using a simple wireless text messaging program between two Faraday digital radios. This program is extremly simple and provides unacknowledged data transfer
* **Simple File Transfer**
  * This is a small update to the "Simple Messaging" program that sends binary data (files, images, etc...) over RF between two Faraday digital radios. The communications is unacknowledged not robust.

##Developers - Faraday Proxy Programming

* **[Hello World - Proxy 101](/Tutorials/Tutorials/1-Basic_Proxy_Interactions_And_Programming/0-Proxy_Basics/)**
  * Interacting with proxy as a programmer and the basics of the GET/POST API.
* **[Commanding - Local](/Tutorials/Tutorials/1-Basic_Proxy_Interactions_And_Programming/1-Commanding-Local/)**
  * How to send commands to a locally connected Faraday digital radio.
* **[Telemetry Parsing](/Tutorials/Tutorials/1-Basic_Proxy_Interactions_And_Programming/2-Telemetry-Parsing)**
  * Using the parsing module to parse all packet types of telemetry data from a Faraday digital radio.
* **[Device Configuration](Tutorials/Tutorials/1-Basic_Proxy_Interactions_And_Programming/3-Device-Configuration)**
  * Using the device configuration application to re-configure non-volatile configuration of a locally connected Faraday device.
* **[Commanding - Remote (RF)](/Tutorials/Tutorials/1-Basic_Proxy_Interactions_And_Programming/4-Commanding-Remote-RF)**
  * How to send commands to a remote Faraday device over RF.
* **Experimental RF Packet Forwarding**
  * An introduction to using the simple RF packet forward command that sends a local UART payload over RF to a specified remote Faraday device. This is the basis for more advanced programs such as messaging and data/file transfers.
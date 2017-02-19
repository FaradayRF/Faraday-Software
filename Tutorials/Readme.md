
# Faraday Python Developer Tutorials

This tutorial series is focused on introducing Faraday as a digital radio platform to program using Python. The reader will begin by learning fundamental transmissions of commands to both local and remote (using RF) devices. The tutorial series will conclude by building apon each skill and toolset learned to develope a basic radio data  transmission program capable of transmitting data, text, etc... of abritrary size from one Faraday to another wirelessly.

**Key Concepts**

* Digital Communications Fundamentals
  * Frame/packet, error detection, fragmentation, encapsulation, ARQ (automatic retry-request)
* Programming with Faraday toolsets/modules
* Building more advanced Faraday host computer programs

These tutorials rely on the currently implemented commands/functionality of Faraday and thus provide a great platform for experimentation. Higher data throughput and functionality can be achieved using other toolsets or in conjuction with more speciallized firmware programming that will be covered at a later date.

##Introduction To Faraday Proxy Programming

* **[Commanding - Local](/Tutorials/Tutorials/1-Basic_Proxy_Interactions_And_Programming/1-Commanding-Local/)**
  * How to send commands to a locally connected Faraday digital radio.
* **[Telemetry Parsing](/Tutorials/Tutorials/1-Basic_Proxy_Interactions_And_Programming/2-Telemetry-Parsing)**
  * Using the parsing module to parse all packet types of telemetry data from a Faraday digital radio.
    * Telemetry - Device settings
    * Telemetry - Debug
    * Telemetry - Faraday Telemetry
* **[Commanding - Remote (RF)](/Tutorials/Tutorials/1-Basic_Proxy_Interactions_And_Programming/4-Commanding-Remote-RF)**
  * How to send commands to a remote Faraday device over RF.
* **[Experimental RF Packet Forwarding](/Tutorials/Tutorials/1-Basic_Proxy_Interactions_And_Programming/5-RF-Transmit-Receive-Packet)**
  * An introduction to using the simple RF packet forward command that sends a local UART payload over RF to a specified remote Faraday device. This is the basis for more advanced programs such as messaging and data/file transfers.

## Building Fundamental Applications

* **[Simple Text Messaging](/Tutorials/Tutorials/2-Advanced_Proxy_Programs/Simple_Text_Messaging/)**
  * Utilizing the experimental RF packet forwarding command to build a simple text messaging application.
* **[Simple Text Messaging - Creating Functional Objects](/Tutorials/Tutorials/2-Advanced_Proxy_Programs/Simple_Text_Messaging_Creating_Objects/)**
  * This example tutorial implements the "Simple Text Messaging" application into a generic transmiter/receiver python object. This is a major step towards implemented a RESTful FLASK based application interface. 

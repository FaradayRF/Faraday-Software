
# Faraday Python Developer Tutorials

This tutorial series is focused on introducing Faraday as a digital radio platform. The tutorial is focused on:

* Learning fundamental commands used to command/communicate with a locally connected Faraday
* Learning commands used to transfer data to a remote Faraday radio using wireless transmissions

Each tutorial series builds upon the prior to create a simple wireless transmission program capable of transmitting both text and arbitrary data from one Faraday to another.

**Key Concepts**

* Digital Communications Fundamentals
  * Frame/packet, error detection, fragmentation, encapsulation, ARQ (automatic retry-request)
* Programming with Faraday toolsets/modules
* Building more advanced Faraday host computer programs

> These tutorials rely on the currently implemented commands/functionality of Faraday and thus provide a great platform for experimentation. Higher data throughput and functionality can be achieved using other toolsets or in conjunction with more specialized firmware programming that will be covered at a later date.

##Introduction To Faraday Proxy Programming

* **[Commanding - Local](foundation/Commanding-Local/)
  * How to send commands to a locally connected Faraday digital radio.
* **[Telemetry Parsing](foundation/Telemetry-Parsing) (OUTDATED - UPDATE IN PROGRESS)**
  * Using the parsing module to parse all packet types of telemetry data from a Faraday digital radio.
    * Telemetry - Device settings
    * Telemetry - Debug
    * Telemetry - Faraday Telemetry
* **[Commanding - Remote (RF)](foundation/Commanding-Remote-RF) (OUTDATED - UPDATE IN PROGRESS)**
  * How to send commands to a remote Faraday device over RF.
* **[Experimental RF Packet Forwarding](foundation/RF-Transmit-Receive-Packet) (OUTDATED - UPDATE IN PROGRESS)**
  * An introduction to using the simple RF packet forward command that sends a local UART payload over RF to a specified remote Faraday device. This is the basis for more advanced programs such as messaging and data/file transfers.

## Building Fundamental Applications

* **[Simple Text Messaging](foundation/Simple_Text_Messaging/) (OUTDATED - UPDATE IN PROGRESS)**
  * Utilizing the experimental RF packet forwarding command to build a simple text messaging application.
* **[Simple Text Messaging - Creating Functional Objects](foundation/Simple_Text_Messaging_Creating_Objects/) (OUTDATED - UPDATE IN PROGRESS)**
  * This example tutorial implements the "Simple Text Messaging" application into a generic transmitter/receiver python object. This is a major step towards implementing a RESTful Flask based application interface.


.. Faraday Software documentation master file, created by
   sphinx-quickstart on Tue Sep 13 22:05:09 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

================
Faraday Software
================

The Faraday radio software is a collection of toolsets, applications, and useful code to fully implement a Faraday radio with a computer connection. For a high-level overview of Faraday code check out our code_ page! ** Early users of Faraday are expected to be developers, helping define how Faraday is implemented and the methods in which it helps solve amateur radio tasks**.

.. _code: https://faradayrf.com/code/

The core applications are the heart of Faraday which help the user and developer interface with the radio. All applications attempt to remain RESTful, adhearing to tried and true web application practices. This fundamentally shifts radio experimentation towards an application based endeavor, disassocaiting low-level RF protocol issues from actual use of the radio.

Quickstart Information
----------------------
.. toctree::
	:maxdepth: 1
	
	installation
	getting-started

=================
Core Applications
=================

.. image:: images/FaradayBlocks.png

Proxy
-----
.. toctree::
	:maxdepth: 1
	
	Proxy Application <proxy>
    
The Proxy application is the gateway to Faraday via USB UART communications. With Faraday plugged into a USB port on a computer, Proxy interfaces the radio with the user over a RESTful localhost interface. A basic description of proxy operation as well as the API documentation is located at the above link.

Telemetry
---------
.. toctree::
	:maxdepth: 1
	
	Telemetry Application <telemetry>

The Telemetry application interfaces the Proxy and provides a RESTful interface to decoded telemetry from Faraday as well as the ability to save telemetry to a local storage facility such as SQLite.

Messaging
---------
.. toctree::
	:maxdepth: 1
	
	Messaging Application <messaging>

The Messaging application interfaces the Proxy and provides the user an ability to RESTfully send/receive text-based messages of arbitrary length.

Data
----
.. toctree::
	:maxdepth: 1
	
	Data Application <data>

The Data application interfaces the Proxy and provides a RESTful interface to send/receive data of arbitrary length. This could be text files, images, binary, or any other form of data.

APRS-IS
-------
.. toctree::
	:maxdepth: 1
	
	APRS-IS Application <aprs-is>

The APRS-IS application interfaces the telemetry, messaging, and data application with the APRS-IS system via a web socket. It provides basic interfacing to the APRS system to allow Faraday radios to appear on the APRS interfaces such as aprs.fi_

.. _aprs.fi: http://www.aprs.fi

User Interface
--------------
.. toctree::
	:maxdepth: 1
	
	UI Application <userinterface>

The User Interface (UI) application interfaces the telemetry, messaging, and data applications ith a web-based control and viewing application. The UI is essentially a dashboard with bidirectional interfacing to Faraday allowing one to see data from the Faraday radios, control local and remote radios, and configure local radios settings.

Toolset Module Documentation
----------------------------
.. toctree::
	:caption: FaradayIO
	:maxdepth: 1
	
	toolsets-faradayio
	tutorials_faradayio



	
License
-------
Faraday is licensed under the **GNUv3 with an additional exception for network interfaces**. Read the `license <https://github.com/FaradayRF/Faraday-Software/blob/master/LICENSE.md>`_ to learn more.
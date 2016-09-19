.. Faraday Software documentation master file, created by
   sphinx-quickstart on Tue Sep 13 22:05:09 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Faraday Software
================
The Faraday Software is the code which will redefine what digital radios used in 
amateur radio are. The architecture of the code is modular and mimics web programming.
Digital communications using a Faraday node or similar is simple, intuitive, and easy
to learn.

**Early users of the Faraday node are expected to be developers willing to help define the look and feel of interacting with Faraday as well as identify and fix confusing aspects of using the radio. Eventually this will not be the case. For now, welcome!**

Overview
--------
Faraday software is the software project which interacts with the Faraday modem or
a compliant device which interfaces the USB UART in the same manner. Data is sent and
retrieved over the UART connection with a "proxy" providing a RESTful interface.
Subsequent programs interact and provide their own interfaces from which to build up
a system with.

.. toctree::
	:caption: Quickstart
	:maxdepth: 1
	
	installation
	getting-started

.. toctree::
	:caption: Toolsets
	:maxdepth: 2
	
	faradayio
License
-------
Faraday is licensed under the **GNUv3 with an additional exception for network interfaces**. Read the `license <https://github.com/FaradayRF/Faraday-Software/blob/master/LICENSE.md>`_ to learn more.
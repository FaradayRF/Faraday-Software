# APRS
The Automatic Packet Reporting System, [APRS](http://www.aprs.org/) has been around is some shape or form since 1982. It is a tried and true situation awareness application of ham radio. The [APRS-IS](http://www.aprs-is.net/) network is the common link between APRS gateways using the internet. Since Faraday modems connected to a computer use internet sockets to communicate with applications it is trivial to send data over the internet.

The APRS application is a core Faraday application provided by FaradayRF so that radio amateurs may leverage this heritage network with Faraday. Eventually we will provide an interconnected network for Faraday data which will render the APRS specification based APRS-IS not as useful. However, we're fans of what APRS has done to the hobby and are excited to be able to integrate with it.

## What Does the APRS Application Do?
This application provides a socket link to APRS-IS servers and sends data from Faraday to show up on the APRS-IS system. This way, you may use services such as the excellent [aprs.fi](https://www.aprs.fi) to view geospatial information. The current limitations include:

 * Data is only sent to APRS-IS and is not received from it
 * Only specific APRS Specification packet types relevant to Faraday have been implemented
 * Packets sent to APRS-IS are intended to not rebroadcast over RF (yet). However, this is not guaranteed and could end up on RF anyways.
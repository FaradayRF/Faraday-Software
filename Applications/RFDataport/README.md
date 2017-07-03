# RFDataport Documentation

## Starting The RFDataport Server

* Copy rfdataport.sample.ini to rfdataport.ini and update as needed
* Run rfdataport_server.py

Send any data (base64 encoded) to the server port and it will automatically be fragmented and sent with as many packets as needed. There is no need for packetizing the data in any way. The packets described below are for internal server TX and RX used abstracted by the FLASK interface.

## Server Packets

### Transmits Packets
As noted in the packet excel document the transmitted packets contain:
* Packet Type
  * Indication of data or command packets for RFDataport operation
* Sequence
  * Counting sequence numbering of packets
* Data Payload
  * Remaining bytes are payload data. This is fixed length so data not long enough will be padded.

### Receive Packets

#### Data Packet

Data packets will be received from the FLASK server as the fragmented data packets only.
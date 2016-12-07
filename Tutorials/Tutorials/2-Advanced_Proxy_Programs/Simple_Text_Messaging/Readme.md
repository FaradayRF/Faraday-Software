
# Tutorial - Simple Text Messaging Application Using Experimental RF Command

As shown in the previous tutorial it is possible to send short packets between two Faraday's using only python code and use of the "Experimental RF Packet Forward" functionality. Transmitting messages longer than a single packet is not possible without introducing the concent of packet fragmentation and encapsulation. ***This tutorial program will allow the transmission and reception of abritrarally long messages between two Faraday devices using RF transmissions.***

The key concept to understand for this tutorial is packet fragmentation. Packet fragmentation breaks a large packet into smaller "chunks" for transmission, the receiver reassembles these chunks of data piece by piece until the original packet has been recreated. 

![Packet Fragmentation And Reassembly](Images/Packet-Fragmentation.png "Packet Fragmentation And Reassembly")

Packet encapsulation is the act of placing one packet (or portions of a packet) into another packet as data payload. In order to reassemble correctly several key issues need to be addressed:

* Ordering of fragmented packets needs to be maintained
* Receiver must know when to start and stop reassembling a fragmented packet

There are also several key items that will NOT be addressed:

* Error detection and correction will not be addressed for simplicity
* All commands must be addressed to the intended Faraday; Experiemental RF packet forward command cannout be "broadcasted" to all devices.
  * A more complicated dedicated messaging program will achieve this

#Running The Tutorial Example Script

## Start The Proxy Interface

Following the [Configuring Proxy](../../0-Welcome_To_Faraday/Configuring_Proxy/) tutorial configure, start, and ensure a successful connection to **BOTH** locally (USB) connected Faraday digital radios.

## Modify Configuration Files

Basic configuration for the local and remote Faraday devices need to be updated in the `receiver_configuration.ini` and `transmiter_configuration.ini` files. The `[local]` and `[remote]` INI file sections are respective to the configuration file.

### Transmiter INI Configuration


* **[local]**
  * Referenced to the local proxy device callsign and ID as set in the proxy configuration INI file.

* **[remote]**
  * Referenced to the actual callsign and ID assigned to the remote unit's device configuration Flash memory. *This callsign and ID are used to address the RF packets to the correct device.*

For example to transmit from a proxy device `KB1LQD-1` to a remote unit of `KB1LQD-2`:

![Example Transmiter Configuration](Images/TX_Config.png "Example Transmiter Configuration")

### Receiver INI Configuration

* **[local]**
  * Referenced to the local proxy device callsign and ID as set in the proxy configuration INI file.

In this example `KB1LQD-2` is the receiving device and both the proxy allocation and the device programming are "`KB1LQD-2`. 

![Example Receiver Configuration](Images/RX_Config.png "Example Receiver Configuration")

## Run The Receiver Program `rx.py`

Execute the `rx.py` program. This will start a terminal prompt that is waiting for messages to receive from the receiving Faraday through the proxy interface.

![RX Started](Images/rx_started.png "RX Started")

## Run The (Basic) Transmitter Program `tx.py`

Execute the `tx.py` program to transmit a long (larger than a single 41 byte Experimental RF packet forward packet)fixed length string to the receiver.

The message saved (feel free to edit you're own message in!) is `This is a test of a very long message that will be fragmented and reassembled!`. 

After transmission observe the receiver terminal, the message should have been received!

![Fixed Length Message Received](Images/rx_receive_fixed_length.png "Fixed Length Message Received")

Note that original message has been recieved 100% correct. Although this message was split between 2 data packets and a START/END packet the message was reasembled. There is no error correction in this simple program, if corruption or loss occurs the message contents will not be 100% correct.

## Run The User Input Transmitter Program `tx_user_input.py`

This transmitter program accepts user text input and after hitting the ENTER key to initiate a transmission.

![Received User Input Transmission](Images/rx_receive_user_message.png "Received User Input Transmission")

#Theory Of Operation

## Program Structure

The transmit and receive messaging funcitons are provided by two class objects `MsgStateMachineTx()` and `MessageAppRx()` respectively in the `faradaymsg.py` script. These objects contain the fragmentation, sequencing, and other functions that create the simple messaging program. 

## Fragmentation Packets

Fragmentation of the packets must be accompanied by a method for the receiver to know when a new message has started, stopped, and the order of the received fragments. Three packet types have been created and are encapsulated inside a simple fixed length "Frame" (header) that indicates which packet type was received.

![Packet Types](Images/Fragmentation-Packets-States.png "Packet Types")

* **START Packet:** Indicates the beginning of a new message to receive and contains information such as source station ID and expected length/fragmentation packets to receive.

* **DATA Packet:** This packet contains one fragmented packet as a payload and is used each time as the a single fragmentation is transmitted until completed. It contains a simple header that indicates the sequence ordering for reassembly.

* **END Packet:** Indicates the message transmission has completed and contains a final message size in bytes. The message size in bytes is a very simple error detection method although not very reliable (it will detect lost packets).


## Receiver - Assembling Fragmented Data

* **IDLE:** Program waits here until a new message to receive is detected (START packet)

* **INIT:** Message buffer is cleared and fragmentation counters reset 

* **FRAGMENT:** The state operated during reception of all sequential fragmentation packets and reassembly

* **END:** Indicates the last packet has been received and to complete reassembly of message and return to idle

![Receiver Fragmentation State Machine](Images/Receiver_States.png "Receiver Fragmentation State Machine")


## Transmitter - Fragmenting Data

The transmitter class operations are very straight forward in their operational flow to create the needed frames/packets.

![Fragmenting Data](Images/Transmit_Create_Functional_Diagram.png "Fragmenting Data")

## Transmitter - Transmitting Fragmented Data

The transmitter program then transmits the packets in the specific order to match the receiver state machine operational flow.

![Fragmentation Packet Transmit Ordering](Images/Transmit_Order.png "Fragmentation Packet Transmit Ordering")




#Apendix

## Frame and Packet Definitions

(Make better!)

![Packets](Images/Packets.png "Packets")




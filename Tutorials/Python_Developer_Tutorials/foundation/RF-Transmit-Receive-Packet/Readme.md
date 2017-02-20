
# Tutorial - Experimental RF Command

This tutorial introduces wireless data transmission between two Faraday units. The example program(s) uses the "Experimental RF Packet Forward" Faraday command application command. This command sends a single data packet (payload) as supplied from the local device (transmitter) to a remote device (receiver) using a wireless command transmission. This is "experimental" because it is not optimized and purely for learning/debugging but it introduces key concepts that are used in more advanced Faraday data transmission programs. ***This enables simple proxy (Python) packet protocol experimentation without the need for CC430 programming!***

> This code makes up for its extreme inefficiency with its simplicity. A throughput of ~2kBps was measured using this tutorial program operating at a datarate of 38.4kbaud sending 1kB of data. Inefficient but still pretty fast for amateur radio!

Although there is limited optimization and flexibility available this provides the educational basis for:

* Single data packet transmissions
* Text message programs
  * [Packet fragmentation](http://www.tech-faq.com/packet-fragmentation.html), [packet sequencing](https://www.wireshark.org/docs/wsdg_html_chunked/ChDissectReassemble.html),flow control [general protocol state machines (PDF)](http://courses.cs.vt.edu/~cs5516/spring03/slides/reliable_tx_1.pdf)
* File transfer
  * [ARQ protocols](https://en.wikipedia.org/wiki/Automatic_repeat_request)

There are two transmitter scripts provided that are received by a single receiver script.
 
* Transmit a saved variable 
* Transmit user input data

### Prerequisites
* Properly configured and connected proxy
  * x2 Faraday connected to local computer
 
> Note: Keep the units seperated a few feet apart and ensure the RF power settings are below ~20 to avoid desensing the CC430 front end receiver!

> Note: Until proxy auto-configuration functionality is added it is possible that proxy's assigned callsign is different than the units actual configuration callsign. Please keep these matching unless you know what you're doing.

An example proxy.ini with two units connected is shown below.

```Python
[FLASK]
HOST=127.0.0.1
PORT=8000

[PROXY]
UNITS=2

[UNIT0]
CALLSIGN = KB1LQD
NODEID = 1
COM = COM106
BAUDRATE = 115200
TIMEOUT = 5

[UNIT1]
CALLSIGN = KB1LQD
NODEID = 2
COM = COM112
BAUDRATE = 115200
TIMEOUT = 5
```

#Running The Tutorial Example Script

## Configuration

* Open `configuration-template.ini` with a text editor
* Transmitter
  * Update `CALLSIGN` Replace ```REPLACEME``` to match the callsign of the Faraday unit **as assigned** in proxy
  * Update `NODEID` to match the callsign node ID of the Faraday unit **as assigned** in proxy
* Receiver
  * Update `CALLSIGN` Replace ```REPLACEME``` to match the callsign of the remote Faraday unit as configured in the devices FLASH memory configuration
  * Update `NODEID` to match the callsign of the remote Faraday unit as configured in the devices FLASH memory configuration
* Save the file as `configuration.ini`

> NOTE: Ideally the proxy assigned callsign/ID matches the unit device configuration but this is not controlled or required and care should be taken.

```python
[DEVICES]
UNITS=2

; Transmitter - This should match the connected Faraday unit as assigned in Proxy configuration
UNIT0CALL=REPLACEME
UNIT0ID= REPLACEME

; Receiver - This should match the programmed callsign of the remote Faraday device to be commanded (receive)
UNIT1CALL=REPLACEME
UNIT1ID= REPLACEME
```

## Edit Local/Remote Device Information

###Transmit Python Script(s)

There are two transmitter scripts provided that are used to send UART data to the intended transmitter Faraday which in turn forwards that data over a wireless transmission.

* `Tutorial_Exp_RF_Packet_TX.py` - Transmits a series of hardcoded messages
* `Tutorial_Exp_RF_Packet_TX-User-Input.py` - Transmits user input text


### Receiver Python Script

The `Tutorial_Exp_RF_Packet_RX.py` script is used to create the "receiver" for the received data packet(s) from the experimental packet forward command application "port". It continuously queries proxy for new packets on this port and if so it retrieves, parses, and displays them.

## Start The Receiver

Run the `Tutorial_Exp_RF_Packet_RX.py` script and when properly conneted to the proxy Faraday device a terminal prompt like below should appear:

![Receiver Started Prompt](Images/Receiver_Started.png "Receiver Started Prompt")


## Execute Tutorial Script `Tutorial_Exp_RF_Packet_TX.py`

Simply running this script will transmit two predefined data messages (ASCII) one after the other to the receiver and be displayed!

**Transmitter Prompt**

![Receiver Prompt Success 1](Images/TX_1_Output.png "Transmitter Prompt Success 1")

**Receiver Prompt**

![Receiver Prompt Success 1](Images/Output_Example_Success_1.png "Receiver Prompt Success 1")

> If you do not see received packets see the troubleshooting section below


## Execute Tutorial Script `Tutorial_Exp_RF_Packet_TX-User-Input.py`

The "User Input" transmitter program will open a prompt (left) when run thats asks for you to enter text to be transmitted to and displays on the receiver (right)  terminal.

Type in any message (keep in legal for Part 97!) to the transmitter prompt the is less than 42 characters (bytes) long and press enter to transmit. You should see the receiver print the message!

> Faraday's simple wireless network stack embededs the device's callsign in every (layer 2) packet as ASCII. There is no need to manually "identify".

![Output Success User Input](Images/Output_Example_Success_2.png "Output Success User Input")

Congratulations, you just transmitted your first simple text message using Faraday!

> If you do not see received packets see the troubleshooting section below

#Code Overview - Receiver



## Code - Receiver Loop

The receiver code is extremely basic and simple loops while checking for a new data from UART service port #2. The `faraday_1.GETWait()` is run on each loop iteration and when data has been received it decodes the proxy BASE64 and prints the raw data payload to the terminal prompt. Setting `data = None` is important so that the function only prints NEW data as received, `faraday_1.GETWait()` returns `None` when no data has been retrieved from proxy.

```python
#Print debug information about proxy port listening
print "Receiver operating TCP Localhost port:", faraday_1.FLASK_PORT
print "Receiver (Proxy):", receiver_device_callsign + '-' + str(receiver_device_node_id)
print "\n"
#Setup variables for receiving
data = None

#While loop to wait for reception of data packet from experimental message application
while(1):
    #Wait until there is new data on the message application port OR timout
    data = faraday_1.GETWait(receiver_device_callsign, receiver_device_node_id, PROXY_MESSAGE_EXPERIMENTAL_PORT, 2)

    #Check if data is False (False means that the Get() function timed out), if not then display new data
    if (data != None) and (not 'error' in data):
        payload_data = data[0]['data']
        print "Received Message Decoded:", faraday_1.DecodeRawPacket(payload_data)

        #Set data = False so that the function loop can properly wait until the next data without printing last received data over and over
        data = None
```

## Code - Transmitter (`Tutorial_Exp_RF_Packet_TX.py`)

The transmitter code that sends a predefined string variable to the receiver is straight-forward programatically. The predefined experimental RF packet forward command is accessed using `faraday_cmd.CommandLocalExperimentalRfPacketForward()` from the `faradaycommands.py` module. The message is simple placed into this function as a data payload to the intended remote receiving Faraday device.

Two messages are send sequentially, `"Testing RF Packet 1"` and `"Testing RF Packet 2"` with not timing constraints (flow control) between them. Faraday is fast enough to buffer both incoming packets and transmit them. 

```python
print "\nConnecting to proxy on PROXY device:", transmitter_device_callsign + '-' + str(transmitter_device_node_id)
print "\nTransmitter (Proxy):", transmitter_device_callsign + '-' + str(transmitter_device_node_id)
print "Receiver (Device Configuration):", receiver_device_callsign + '-' + str(receiver_device_node_id)
print '\n'

#Use the predefined experimental message command (singled packet) function to send an RF message to a remote unit
message = "Testing RF Packet 1"  # NOTE: Max payload size commandmodule.FIXED_RF_PAYLOAD_LEN
command = faraday_cmd.CommandLocalExperimentalRfPacketForward(receiver_device_callsign, receiver_device_node_id, message)
print "Transmitting message:", message
faraday_1.POST(transmitter_device_callsign, transmitter_device_node_id, faraday_1.CMD_UART_PORT, command)

message = "Testing RF Packet 2"
command = faraday_cmd.CommandLocalExperimentalRfPacketForward(receiver_device_callsign, receiver_device_node_id, message)
print "Transmitting message:", message
faraday_1.POST(transmitter_device_callsign, transmitter_device_node_id, faraday_1.CMD_UART_PORT, command)
```

## Code - Transmitter (`Tutorial_Exp_RF_Packet_TX-User-Input.py`)

Reviewing the transmitter code above this code is pretty straight forward.

``` Python
user_input = ''

while(user_input != "quit"):
    user_input = raw_input("\nText To Transmit (Max Length = " + str(commandmodule.FIXED_RF_PAYLOAD_LEN) +" Bytes)" + ": ")
    if len(user_input) < commandmodule.FIXED_RF_PAYLOAD_LEN:
        command = faraday_cmd.CommandLocalExperimentalRfPacketForward(receiver_device_callsign, receiver_device_node_id,
                                                                      str(user_input))
        print "Transmitting message:", user_input, '\n'
        faraday_1.POST(transmitter_device_callsign, transmitter_device_node_id, faraday_1.CMD_UART_PORT, command)
    else:
        print "Payload is too long!", len(user_input), "Bytes", '\n'
```

## Program Limitations

### Maximum Transmissible Unit (MTU)
You're probably wondering why the maximum data length is 42 bytes? The simplistic experiemental experiemental packet forwarding command used is a standard "command application" packet that performes a specific action. This is limited to a max size of 64 bytes by the command application packet protocol. Adding overhead for the command application header information leaves a total payload of 42 bytes. There is no logic in this example program to fragment larger amounts of data into 42 byte pieces and reassemble after reception.

The following tutorials will create a simple fragmentation protocol that will allow for data larger than the MTY to be transfered.

### Channel Reliability
This example program nor does the experimental RF packet forwarding command provide a "reliable" communication channel. If a wireless transmission is corrupted or lost the information will be lost and the reciever will not know that it is missing. There are two common ways to mitigate this:

* Automatic Retry-Request (ARQ)
  * Error detection and transmissions retry
* Forward Error Correction
  * Reduntant data coded into data that allows for correction of minor errors/corruption in data without retrying transmission

Future tutorials will explore the developement of a simple ARQ protocol.

### Optimization
This tutorial example series uses a simple single packet command function to transfer data and is slow by design. Great enhancements to total throughput (among others) can be achieved by:

* Custom CC430 firmware that provides multi-packet buffering
* ARQ layer within CC430 firmware
* Additon of a "sliding-window" ARQ protocol

# Troubleshooting

The addition of wireless communications invites more chances for setup and reliability issues. Below are a few quick items to check if you are not able to runing the tutorial script is not commanding the remote unit correctly.

**Remote Callsign/ID**

Check that the correct callsign and ID number of the remote device is correct (as programmed) or the MAC layer protocol will not allow the remote unit to accept the command. All commands accepted by a unit over RF must match be properlly addressed.

**RF Power - Desensing**

Faraday is actually quite sensitive and having a high power signal transmit between two close units can cause the receiving device to not hear the transmission. This is called radio de-sensing. The solution is to turn the power down, typically for a foot or two I've found a setting under 20 works well.

**Payload Data Too Long**

This simple implementation is limited to a maximum of 42 Bytes of payload data. Exceeding this will cause the transmission to fail.

**General Noise/Corruption**

This simplistic protocol has no error detection or correction. If a packet was not receiver simply retry several times.

#Excersizes
* Experiements with python's `repr()` to display raw bytes of data instead of the ASCII converted view
  * This will make the fixed-length payload padding bytes visible!
* Write a simple frame that allows a variable length message (in one MTU) that allows you to easily extract ONLY the intended payload and remove other bytes of padding data.

#See Also



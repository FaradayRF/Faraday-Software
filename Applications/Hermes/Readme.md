
#OUTDATED - NEEDS UPDATING - DO NOT USE

# Tutorial - Simple Text Messaging Class Object

The previous tutorial created a simple messaging application that utilized the Faraday  proxy interface and directly implemented a user interface. Proper application modularity should separate the user interface from core application, ideally using a RESTful interface. 

This tutorial reconfigured the prior "Simple Messaging Application" transmit and receive classes into multi-threaded class objects. The example program `message_application_example.py` utilizes the functionality of `faraday_msg.py` in threaded class objects contained in `msg_object.py`. Queues are established (FIFO's) that allow buffering of transmit and receive messages if multiple are received prior to polling the receiver for new messages. The example program can therefor operate both transmit and receive in a single script independently.

This allows for modular interfacing to the classes where a future tutorial can implement a RESTful API.

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

## Run `message_application_example.py`

Run the application, you'll see a screen ask for the message you'd like to transmit.

![Program Prompt](Images/Initial_Program.PNG "Program Prompt")

Type the message you'd like to transmit. This message will transmit from `Unit 1` and be received on `Unit 2`. Hit the enter key to transmit, you should see the red LED blink on `Unit 1` indicating transmissions are occuring followed shortly by the prompt displaying the received message. The propmt will ask for the next message to send.

![Received Message](Images/Received_Message.PNG "Received Message")

Congratulations! We've taken a mighty step to creating a powerful transmit/recieve object that allows simple direct messaging between Faraday digital radios. 

## Ideas

Ideas for the reader to experiment with the example program.

* Modify the example code to example sending more than one message prior to receiving. This will build up messages in the queue.
* Write an automated response message to transmit back after reception.
* Break the `message_application_example.py` application into two programs each dedicated to a specific device. Enable transmit/receive between two units generically.

#Code Overview

## Code - Class Objects

Creating transmit and receive class objects allows functionality to be copied to multiple instances from a single python script. Creating a third object combining the transmit/recieve objects together in a single class allows for one object variable to perform both functions seamlessly. 

Although we haven't created a FLASK API interface yet we have created abritrary function blocks that can be glued to a Flask interface.

### Transmiter Object

The transmit object simply provides an interface where a supplied destination callsign, ID number, and payload (message) are transmitted to the inteded device using Faraday's CC430 RF modem. The `send()` function calls `faraday_tx_msg_sm.createmsgpackets()` to fragment the message into smaller packets and inserting the START and END protocol packets. `faraday_tx_msg_object.transmitframe()` simply transmits the packets.

```python
class TransmitObject(object):

    def __init__(self, local_device_callsign, local_device_node_id):
        self.local_device_callsign = local_device_callsign
        self.local_device_node_id = local_device_node_id
        # Create messaging application objects needed for transmissions
        self.faraday_tx_msg_sm = faraday_msg.MsgStateMachineTx()
        self.faraday_tx_msg_object = faraday_msg.MessageAppTx(self.local_device_callsign,
                                                              self.local_device_node_id)
        # Create receiver application object
        self.faraday_rx_msg_object = faraday_msg.MessageAppRx()
        self.rx_uart_service_port_application_number = 3
        self.GETWAIT_TIMEOUT = 2

    def send(self, dest_callsign, dest_id, payload):
        # Create message fragments
        self.faraday_tx_msg_sm.createmsgpackets(self.local_device_callsign, self.local_device_node_id, payload)

        # Iterate through start, stop, and data fragment packets and transmit
        for i in range(0, len(self.faraday_tx_msg_sm.list_packets), 1):
            # print "TX:", repr(self.faraday_tx_msg_sm.list_packets[i])
            self.faraday_tx_msg_object.transmitframe(self.faraday_tx_msg_sm.list_packets[i], dest_callsign, dest_id)
```

### Receiver Object

The reciever object must run in the background constantly looking for new data (packet fragments) received in the proxy interface buffers and perform reassembly as needed. When a full message has been reconstructed it is placed into a FIFO (Queue) for retrieval.

The [Python threading module](https://pymotw.com/2/threading/) was used to run the objects `run()` function indefinietely as a seperate process.

```python
class ReceiveObject(threading.Thread):
    def __init__(self, local_device_callsign, local_device_node_id):
        self.local_device_callsign = local_device_callsign
        self.local_device_node_id = local_device_node_id
        # Set constants
        self.rx_uart_service_port_application_number = 3
        self.GETWAIT_TIMEOUT = 0.5

        # Create receiver application object
        self.faraday_rx_msg_object = faraday_msg.MessageAppRx()
        threading.Thread.__init__(self)
        self.fifo = Queue.Queue(0)
        return

    def run(self):
        # Loop continuously through the faraday experimental RF command message application RX routine
        while 1:
            rx_message_dict = self.faraday_rx_msg_object.rxmsgloop(self.local_device_callsign,
                                                                   self.local_device_node_id,
                                                                   self.rx_uart_service_port_application_number,
                                                                   self.GETWAIT_TIMEOUT)
            if rx_message_dict is not None:
                self.fifo.put(rx_message_dict)
                rx_message_dict = None
            else:
                pass  # No messages received
```


### Main Messaging Object

The object below combinds both transmit and receive objects into a single object for cleaner interactions. It is important to run the `receive.start()` to initiate the threaded process of the receiver. **This object is the main object to assign when using the simple messages application.**

```python
class MessageObject(object):
    def __init__(self, local_device_callsign, local_device_node_id):
        self.transmit = TransmitObject(local_device_callsign, local_device_node_id)
        self.receive = ReceiveObject(local_device_callsign, local_device_node_id)
        self.receive.start()
```
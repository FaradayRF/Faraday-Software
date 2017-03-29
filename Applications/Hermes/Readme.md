# Hermes - Message Application

Hermes is a simple messaging application developed for Faraday. Hermes, the messenger of the gods in mythology, is a fitting name for our first application to transition into messaging between radios.

Based on Flask like many other Faraday applications, Hermes provides transmit and receive messaging functionality for Faraday radios within range of each other. Sending a message to the Flask port with an HTTP request will cause Hermes to interface with the local Faraday radio via Proxy to send the message over RF. The reverse is also true for receive.

The `hermesflaskexample_rx.py` and `hermesflaskexample_tx.py` scripts are examples of simple user interface programs utilizing the Flask messaging server and provide functionality to transmit text between two units.

### Prerequisites
* Properly configured and connected proxy
  * x2 Faraday connected to local computer
 
> Note: Keep the units separated a few feet apart and ensure the RF power settings are below ~20 to avoid de-sensing the CC430 front end receiver!

> Note: Until proxy auto-configuration functionality is added it is possible that proxy's assigned callsign is different than the units actual configuration callsign. Please keep these matching unless you know what you're doing.

#Running The Example Scripts

## Configuration

In these example programs either unit can be used as transmitter or receiver.

* Open `hermes.sample.ini` with a text editor
* UNIT0
  * Update `CALLSIGN` Replace ```REPLACEME``` to match the callsign of the Faraday unit **as assigned** in proxy
  * Update `NODEID` to match the callsign node ID of the Faraday unit **as assigned** in proxy
* UNIT1
  * Update `CALLSIGN` Replace ```REPLACEME``` to match the callsign of the remote Faraday unit as configured in the devices FLASH memory configuration
  * Update `NODEID` to match the callsign of the remote Faraday unit as configured in the devices FLASH memory configuration
* Save the file as `hermes.ini`


```python
[FLASK]
HOST=127.0.0.1
PORT=8005

[PROXY]
UNITS=2

[UNIT0]
CALLSIGN=REPLACEME
NODEID=REPLACEME

[UNIT1]
CALLSIGN=REPLACEME
NODEID=REPLACEME

```

## Run

* Run the proxy server with both units properly connected
* Run the `hermesflaskserver.py` Flask server
* Run the `hermesflaskexample_rx.py` receiver application example
* Run the `hermesflaskexample_tx.py` transmitter application example
* Enter text intended for transmission and press enter
  * The text should appear in the receiver prompt after proper reception
  * If text was not properly received ensure configuration is correct and try again



Flask Server | Transmitter Example | Receiver Example

![All Hermes programs started](Images/Start.png)

Successful transmission of data.

![Successful transmission of data](Images/TX-RX-Data.png)

### Transmitter/Receiver Specification

The transmitter and receiver units are specific in the example RX and TX scripts. The configuration file `hermes.ini` is parsed for `UNIT0` and `UNIT1` and the example scripts choose the functionality of either. Each unit has TX/RX functionality using Hermes.

The transmitter script by default assigns `UNIT0` as the "local" unit used for transmission and `UNIT1` as the destination (receiving) unit as shown below.


``` Python
localcallsign = config.get('UNIT1', 'CALLSIGN')
localnodeid = int(config.get('UNIT1', 'NODEID'))
destinationcallsign = config.get('UNIT0', 'CALLSIGN')
destinationnodeid = int(config.get('UNIT0', 'NODEID'))
```
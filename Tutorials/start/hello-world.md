# Hello World

With hardware connected, hardware configured, and Proxy running you are ready to write your first Python script to command hardware using the API! We're going to communicate through Proxy over the USB cable with the CC430 and turn the LED's ON and OFF. It's our very own "[hello-world](https://en.wikipedia.org/wiki/%22Hello,_World!%22_program)". Let's go!

> NOTE: All commands are checked for corruption by the CC430 prior to accepting them but they are not currently acknowledged or guaranteed to be received.

## Prerequisites
* Faraday radio connected via USB to the computer
* Faraday radio configured correctly
* Proxy configured and running
* Download [hello-world.py](https://rawgit.com/FaradayRF/Faraday-Software/master/Tutorials/start/hello-world.py) to you computer, open in a text editor

# Code Overview
## Importing Faraday Modules
The FaradayIO module contains several subpackages which make using Faraday much more straight forward. These are the `faradaybasicproxyio` and `faradaycommands` classes which implement communications over proxy with an abstracted API using several of their attributes.

## Faradaybasicproxyio
This subpackage contains the class proxyio which abstracts the RESTful interface provided by Proxy. Two of the most important functions provided are `GET()` and `POST()` which perform GET and POST HTTP methods with properly formatted BASE64 payloads Proxy expects.

## Faradaycommands
This subpackage abstracts commands one might wish to send to Faraday. It contains functions which build up generic commands such as `CommandLocal()` or task-specific commands such as `CommandLocalGPIOLED1On()` which turns on LED1.

## LED Code
The following code example will enter an infinite loop to turn LED1 ON (green) and OFF with a period of one second. We've placed `hello-world.py` in the start tutorials folder and all you need to do is modify it with your Faraday radio callsign-nodeid where `callsign = 'REPLACEME'` and `node_id = 0` are located. Alternatively you can _right-click_ and "Save Link As" on the link above in the Prerequisites section. Below is `hello-world.py` modified for use by KB1LQD-1.

```
#!/usr/bin/env python

import os
import sys
import time

# Imports - Faraday Specific
from faraday.proxyio import faradaybasicproxyio
from faraday.proxyio import faradaycommands

#Setup a Faraday IO object
faraday_1 = faradaybasicproxyio.proxyio()  #default proxy port
faraday_cmd = faradaycommands.faraday_commands()

callsign = 'KB1LQD'
node_id = 1

while True:
    #Turn LED 1 ON (GREEN)
    print "Turning LED 1 ON"
    command = faraday_cmd.CommandLocalGPIOLED1On()
    faraday_1.POST(callsign, node_id, faraday_1.CMD_UART_PORT, command)
    time.sleep(0.5)

    #Turn LED 1 OFF
    print "Turning LED 1 OFF"
    command = faraday_cmd.CommandLocalGPIOLED1Off()
    faraday_1.POST(callsign, node_id, faraday_1.CMD_UART_PORT, command)
    time.sleep(0.5)
```


### Windows
* Double-click on hello-world.py and run with python
* Navigate to `C:\faradayrf\faraday-software\Tutorials\start` and run `python hello-world.py`

Ensure that Proxy is running in the background!

### Linux (Debian-based)
* Navigate in terminal to `/git/faraday-software/Python_Developer_Tutorials/start` and run `sudo python hello-world.py`
* sudo is needed to ensure you can write to `/dev/ttyUSB0`

Ensure that Proxy is running in the background!

## Time To Play With RF
This concludes the quickstart section on how to interact with a Faraday connected locally over USB. Our next quickstart section focuses on RF telemetry. Head on over and [learn how to configure Faraday to transmit RF](configuring-rf-faraday.md). We gaurantee it will be fun!

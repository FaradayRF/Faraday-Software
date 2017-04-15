# Hello World

With hardware connected as well as Proxy configured and running you are ready to write your first Python script to command hardware using the API! We're going to communicate through Proxy over the USB cable with the CC430 and turn the LED's ON and OFF. Let's go!

> NOTE: All commands are checked for corruption by the CC430 prior to accepting them but they are not currently acknowledged or guaranteed to be received.

###Prerequisites
 * Faraday radio connected via USB to the computer
 * Proxy configured and running
 
# Code Overview
## Importing Faraday Modules
The FaradayIO module contains several subpackages which make using Faraday much more straight forward. These are the ```faradaybasicproxyio``` and ```faradaycommands``` classes which implement communications over proxy with an abstracted API using several of their attributes.

###Faradaybasicproxyio
This subpackage contains the class proxyio which abstracts the RESTful interface provided by Proxy. Two of the most important functions provided are ```GET()``` and ```POST()``` which perform GET and POST HTTP methods with properly formatted BASE64 payloads Proxy expects.

### Faradaycommands
This subpackage abstracts commands one might wish to send to Faraday. IT contains functions which build up generic commands such as ```CommandLocal()``` or task-specific commands such as ```CommandLocalGPIOLED1On()``` which turns on LED1.

##LED Code
The following code example will enter an infinite loop to turn LED1 ON (green) and OFF in a total of one second. `hello-world.py` should be modified with your callsign and node ID where `REPLACEME` has been added. Below is `hello-world.py` modified for use by KB1LQD-1.
```
#!/usr/bin/env python

import os
import sys
import time

# Add Faraday library to the Python path.
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

# Imports - Faraday Specific
from faraday.proxyio import faradaybasicproxyio
from faraday.proxyio import faradaycommands

#Setup a Faraday IO object
faraday_1 = faradaybasicproxyio.proxyio() #default proxy port
faraday_cmd = faradaycommands.faraday_commands()

while(1):
    #Turn LED 1 ON (GREEN)
    print "Turning LED 1 ON"
    command = faraday_cmd.CommandLocalGPIOLED1On()
    faraday_1.POST('KB1LQD', 1, faraday_1.CMD_UART_PORT, command)
    time.sleep(0.5)

    #Turn LED 1 OFF
    print "Turning LED 1 OFF"
    command = faraday_cmd.CommandLocalGPIOLED1Off()
    faraday_1.POST('KB1LQD', 1, faraday_1.CMD_UART_PORT, command)
    time.sleep(0.5)
```

To run the code example we've placed `hello-world.py` in the start folder
### Windows
 * Double-click on hello-world.py and run with python
 * Navigate to `C:\faradayrf\faraday-software\Tutorials\start' and run `python hello-world.py`
 
Ensure that Proxy is running in the background!
 
### Linux (Debian-based)
 * Navigate in terminal to `/git/faraday-software/Python_Developer_Tutorials/start` and run `sudo python hello-world.py`
  * sudo is needed to ensure you can write to `/dev/ttyUSB0`
  
Ensure that Proxy is running in the background!

## Time To Play With RF
This concludes the quickstart section on how to interact with a Faraday connected locally over USB. Our next quickstart section focuses on RF telemetry. Head on over and [learn how to configure Faraday to transmit RF](configuring-rf-faraday.md). We gaurantee it will be fun!

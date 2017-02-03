# Hello World

With hardware connected as well as Proxy configured and running you are ready to write your first Python script to command hardware using the API! We're going to communicate through Proxy over the USB cable with the CC430 and turn the LED's ON and OFF. Let's go!

> NOTE: All commands are checked for corruption by the CC430 prior to accepting them but they are not currently acknowledged or guaranteed to be received.

###Prerequisits
 * Faraday radio connected via USB to the computer
 * Proxy configured and running

##LED Code
The following code example will enter an infinite loop to turn LED1 ON (green) and OFF in a total of one second.
```
import os
import sys
import time
sys.path.append(os.path.join(os.path.dirname(__file__), "../../Faraday_Proxy_Tools")) #Append path to common tutorial FaradayIO module

from FaradayIO import faradaybasicproxyio
from FaradayIO import faradaycommands

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

To run the code example we've placed hello-world.py in the start folder
### Windows
 * Double-click on hello-world.py and run with python
 * Navigate to `C:\faradayrf\faraday-software\Tutorials\start' and run `python hello-world.py`
 
Ensure that Proxy is running in the background!
 
### Linux (Debian-based)
 * Navigate in terminal to `/git/faraday-software/Tutorials/start` and run `sudo python hello-world.py`
  * sudo is needed to ensure you can write to `/dev/ttyUSB0`
  
Ensure that Proxy is running in the background!

# Code Overview
## Importing Faraday Modules
The FaradayIO module contains several subpackages which make using Faraday much more straight forward. These are the ```faradaybasicproxyio``` and ```faradaycommands``` classes which implement communications over proxy with an abstracted API using several of their attributes.

###Faradaybasicproxyio
This subpackage contains the class proxyio which abstracts the RESTful interface provided by Proxy. Two of the most important functions provided are ```GET()``` and ```POST()``` which perform GET and POST HTTP methods with properly formatted BASE64 payloads Proxy expects.

### Faradaycommands
This subpackage abstracts commands one might wish to send to Faraday. IT contains functions which build up generic commands such as ```CommandLocal()``` or task-specific commands such as ```CommandLocalGPIOLED1On()``` which turns on LED1.

# Congratulations
Your Faraday radio is now setup with a callsign and node ID it will use to identify itself even after reboot. We've also installed all necessary programs and configured them to communicate with the radio over USB serial. This concludes the quickstart guide. We highly encourage you to check out our standard core programs such as [Telemetry](../../telemetry) or [APRS](../../aprs). You should also learn more about our API. We're providing the building blocks to experiment, lets go!

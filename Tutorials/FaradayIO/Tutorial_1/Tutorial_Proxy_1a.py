# This example will show how to command Faraday using the basic command application.
# Make sure to turn UART TELEM BOOT Bitmask to 0 to turn OFF telemetry update automatically so that you know telemetry commands are working

#Imports - General

import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../")) #Append path to common tutorial FaradayIO module

#Imports - Faraday Specific
from FaradayIO import faradaybasicproxyio
from FaradayIO import faradaycommands
from FaradayIO import telemetryparser
from FaradayIO import gpioallocations

import time

#Definitions


#Variables
local_device_callsign = 'kb1lqd'
local_device_node_id = 1

#Start the proxy server after configuring the configuration file correctly
#Setup a Faraday IO object
faraday_1 = faradaybasicproxyio.proxyio() #default proxy port
faraday_cmd = faradaycommands.FaradayCommands()


##############
## TOGGLE GPIO
##############
#Turn LED 1 ON LOCAL
command = faraday_cmd.CommandLocalGPIOLED1On()
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)
time.sleep(1)

#Turn LED 1 OFF LOCAL
command = faraday_cmd.CommandLocalGPIOLED1Off()
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)

#Turn LED 2 ON LOCAL
command = faraday_cmd.CommandLocalGPIOLED2On()
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)
time.sleep(1)

#Turn LED 2 OFF LOCAL
command = faraday_cmd.CommandLocalGPIO(0, 0, 0, gpioallocations.LED_2, 0, 0) #This examples how the non predefined LED GPIO commanding is created. Multiple GPIO's can be toggled at once using ||'s
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)
time.sleep(1) #Delay so it is obvious that both LED's turn on at the same time in the next command

#Turn Both LED 1 and LED 2 ON simultaneously
command = faraday_cmd.CommandLocalGPIO((gpioallocations.LED_1|gpioallocations.LED_2), 0, 0, 0, 0, 0)
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)
time.sleep(1)

#Turn Both LED 1 and LED 2 OFF simultaneously
command = faraday_cmd.CommandLocalGPIO(0, 0, 0, (gpioallocations.LED_1|gpioallocations.LED_2), 0, 0)
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)

###############
## ECHO MESSAGE
###############
#Use the general command library to send a text message to the Faraday UART "ECHO" command. Will only ECHO a SINGLE packet. This will send the payload of the message back (up to 62 bytes, this can be updated in firmware to 124!)
originalmsg = "This will ECHO back on UART" #Cannot be longer than max UART payload size!
command = faradaycommands.commandmodule.create_command_datagram(faraday_cmd.CMD_ECHO, originalmsg)
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)

#Retrive waiting data packet in UART Transport service number for the COMMAND application (Use GETWait() to block until ready or return False).
rx_echo_raw = faraday_1.GETWait(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, 1, False) #Wait for up to 1 second

#Now parse data again
b64_data = rx_echo_raw[0]['data']
echo_decoded = faraday_1.DecodeJsonItemRaw(b64_data)

#Display information
print "Original Message: ", originalmsg
print "RAW Received BASE64 ECHO'd Message:", b64_data
print "Decoded received ECHO'd Message:", echo_decoded #Note that ECHO sends back a fixed packed regardless. Should update to send back exact length.



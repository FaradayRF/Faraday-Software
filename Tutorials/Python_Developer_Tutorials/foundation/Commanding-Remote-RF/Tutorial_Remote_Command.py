#Imports - General

import os
import sys
import ConfigParser
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../../Faraday_Proxy_Tools")) #Append path to common tutorial FaradayIO module

#Imports - Faraday Specific
from FaradayIO import faradaybasicproxyio
from FaradayIO import faradaycommands
from FaradayIO import gpioallocations
import time


#Setup a Faraday IO object
faraday_1 = faradaybasicproxyio.proxyio()
faraday_cmd = faradaycommands.faraday_commands()

#Open configuration INI
config = ConfigParser.RawConfigParser()
filename = os.path.abspath("configuration.ini")
config.read(filename)

#Definitions

#Variables
local_device_callsign = config.get("DEVICES","UNIT0CALL") # Should match the connected Faraday unit as assigned in Proxy configuration
local_device_node_id = config.getint("DEVICES","UNIT0ID") # Should match the connected Faraday unit as assigned in Proxy configuration
local_device_callsign = str(local_device_callsign).upper()
remote_device_callsign = config.get("DEVICES","UNIT1CALL") # Should match the programmed callsign of the remote Faraday device to be commanded (receive)
remote_device_node_id = config.getint("DEVICES","UNIT1ID") # Should match the programmed callsign of the remote Faraday device to be commanded (receive)
remote_device_callsign = str(remote_device_callsign).upper()

################################
## TOGGLE Remote Device ++GPIO
################################

#Turn remote device LED 1 ON
print "Transmitting(" + local_device_callsign + "-" + str(local_device_node_id) + ") To Remote Faraday (" + remote_device_callsign + "-" + str(remote_device_node_id) + "): GREEN LED ON"
command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIOLED1On(remote_device_callsign, remote_device_node_id))
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)
time.sleep(1)

#Turn remote device LED 1 OFF
print "Transmitting(" + local_device_callsign + "-" + str(local_device_node_id) + ") To Remote Faraday (" + remote_device_callsign + "-" + str(remote_device_node_id) + "): GREEN LED OFF"
command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIOLED1Off(remote_device_callsign, remote_device_node_id))
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)
time.sleep(0.5)

#Turn both LED 1, LED2, and DIGITAL_IO_0 ON, This requires a slightly more low level function and bitmask. Prior function were high level abstractions of this command
print "Transmitting(" + local_device_callsign + "-" + str(local_device_node_id) + ") To Remote Faraday (" + remote_device_callsign + "-" + str(remote_device_node_id) + "): RED LED ON | GREEN LED ON | DIGITAL_IO_0 ON"
command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remote_device_callsign, remote_device_node_id, gpioallocations.LED_1 | gpioallocations.LED_2 | gpioallocations.DIGITAL_IO_0, 0, 0, 0, 0, 0))
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)
time.sleep(1)

#Turn both LED 1 and DIGITAL_IO_0 OFF
print "Transmitting(" + local_device_callsign + "-" + str(local_device_node_id) + ") To Remote Faraday (" + remote_device_callsign + "-" + str(remote_device_node_id) + "): RED LED OFF | GREEN LED OFF | DIGITAL_IO_0 OFF"
command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remote_device_callsign, remote_device_node_id, 0, 0, 0, gpioallocations.LED_1 | gpioallocations.LED_2 | gpioallocations.DIGITAL_IO_0, 0, 0))
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)
time.sleep(0.5)

print "************************************"
print "\nQuit with ctrl+c"
while(True):
    #Loop until user presses ctrl+c so they can read response
    time.sleep(1)
    pass
#Imports - General

import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../../Faraday_Proxy_Tools")) #Append path to common tutorial FaradayIO module

#Imports - Faraday Specific
from FaradayIO import faradaybasicproxyio
from FaradayIO import faradaycommands
from FaradayIO import gpioallocations
import time


#Setup a Faraday IO object
faraday_1 = faradaybasicproxyio.proxyio()
faraday_cmd = faradaycommands.faraday_commands()

#Local device information (Must match proxy assigned information)
local_device_callsign = 'KB1LQD'  # Should match the connected Faraday unit as assigned in Proxy configuration
local_device_node_id = 1  # Should match the connected Faraday unit as assigned in Proxy configuration

#Remote device information (Must match unit programming)
remote_callsign = 'KB1LQD'  #case independent
remote_id = 2

################################
## TOGGLE Remote Device ++GPIO
################################

#Turn remote device LED 1 ON
command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIOLED1On(remote_callsign, remote_id))
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)
time.sleep(1)

#Turn remote device LED 1 OFF
command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIOLED1Off(remote_callsign, remote_id))
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)
time.sleep(0.5)

#Turn both LED 1, LED2, and DIGITAL_IO_0 ON, This requires a slightly more low level function and bitmask. Prior function were high level abstractions of this command
command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remote_callsign, remote_id, gpioallocations.LED_1 | gpioallocations.LED_2 | gpioallocations.DIGITAL_IO_0, 0, 0, 0, 0, 0))
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)
time.sleep(1)

#Turn both LED 1 and DIGITAL_IO_0 OFF
command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remote_callsign, remote_id, 0, 0, 0, gpioallocations.LED_1 | gpioallocations.LED_2 | gpioallocations.DIGITAL_IO_0, 0, 0))
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)
time.sleep(0.5)

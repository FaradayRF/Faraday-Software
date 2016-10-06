#imports
from FaradayIO import faradaybasicproxyio
from FaradayIO import faradaycommands
from FaradayIO import gpioallocations
import time


#Variables
local_device_callsign = 'kb1lqd'
local_device_node_id = 7

#Setup a Faraday IO object
faraday_1 = faradaybasicproxyio.proxyio()
faraday_cmd = faradaycommands.FaradayCommands()

# This example will show how to command Faraday using the basic command application.
# Make sure to turn UART TELEM BOOT Bitmask to 0 to turn OFF telemetry update automatically

################################
## TOGGLE Remote Device ++GPIO
################################

#Remote device information
remote_callsign = 'kb1lqc' #case independant
remote_id = 1

#Turn remote device LED 1 ON
command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIOLED1On(remote_callsign, remote_id))
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)
time.sleep(1)

#Turn remote device LED 1 OFF
command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIOLED1Off(remote_callsign, remote_id))
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)
time.sleep(0.5)

#Turn remote device LED 2 ON
command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIOLED2On(remote_callsign, remote_id))
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)
time.sleep(1)

#Turn remote device LED 2 OFF
command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIOLED2Off(remote_callsign, remote_id))
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)
time.sleep(0.5)

#Turn both LED 1 and LED 2 ON, This requires a slightly more low level function and bitmask. Prior function were high level abstractions of this command
command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remote_callsign, remote_id, gpioallocations.LED_1 | gpioallocations.LED_2, 0, 0, 0, 0, 0))
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)
time.sleep(1)

#Turn both LED 1 and LED 2 OFF
command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remote_callsign, remote_id, 0, 0, 0, gpioallocations.LED_1 | gpioallocations.LED_2, 0, 0))
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)
time.sleep(0.5)


# Tutorial - Remote RF Command

This tutorial will example how to interact with other Faraday digital radios wirelessly using RF commanding. This tutorial requires the use of two Faraday units connected to proxy, although they will both be connect to the same computer (for convienience) the communication is performed using the CC430 radio. This can be verified by commanding a Faraday unit while being battery powered!

#Running The Tutorial Example Script

## Start The Proxy Interface

Following the [Configuring Proxy](../../0-Welcome_To_Faraday/Configuring_Proxy/) tutorial configure, start, and ensure a successful connection to **BOTH** locally (USB) connected Faraday digital radios.

## Edit Local/Remote Device Information

The tutorial script variables listed below hold the local and remote Faraday device callsign/ID numbers. The local device communicates through the proxy interface and regardless of actual assigned callsign/ID the variables must match that assigned by the *"proxy.ini"* file. The remote device callsign/ID variable is used to address the RF packet and must match that of the remote unit device configuration to be communicated with.

> NOTE: Ideally the proxy assigned callsign/ID matches the unit device configuration but this is not controlled or required and care should be taken.

```python
#Local device information (Must match proxy assigned information)
local_device_callsign = 'kb1lqd'  #case independent
local_device_node_id = 1

#Remote device information (Must match unit programming)
remote_callsign = 'kb1lqd'  #case independent
remote_id = 2
```


## Execute Tutorial Script

While running the tutorial script you should see the green led (LED #1) light up on the remote unit and the red LED flashing on the local unit. Default Faraday operation enables the red LED whenever RF transmissions are occuring.

The tutorial script terminal output during a succesful operation displays raw command packets as transmitted for reference.

![Successful Operation Terminal](Images/Output_Example_Success.png "Successful Operation Terminal")

# RF Commanding Design Summary

The command functionality on Faraday is operating in an application running on Faraday itself and parses a command application packet protocol to determine actions needed. This is common between both local and RF commands however sending and RF command simply encapsulates a local command (for the remote unit) within a local "transmit RF command" command (packet). This results in the remote device receiving a "local" command from a remote device, it knows no difference.

The `DIGITAL_IO_0` pin is a PGIO header pin that can be measured for voltage toggling but no visible effect occures.

#Code Overview

## Code - Toggle LED & Digital GPIO pin 

The tutorial code below is very similar to the previous "local commanding" tutorial however you'll notice that all command destined to be executed on a remote device are commanded using the function argument `9` (command number) with the actual command to be execute as payload. Command `9` simply transmits a command packet to the remote device and upon reception the remote device knows to execute the payload as a local command.

```python
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

#Turn both LED 1 and DIGITAL_IO_0 ON, This requires a slightly more low level function and bitmask. Prior function were high level abstractions of this command
command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remote_callsign, remote_id, gpioallocations.LED_1 | gpioallocations.DIGITAL_IO_0, 0, 0, 0, 0, 0))
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)
time.sleep(1)

#Turn both LED 1 and DIGITAL_IO_0 OFF
command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remote_callsign, remote_id, 0, 0, 0, gpioallocations.LED_1 | gpioallocations.DIGITAL_IO_0, 0, 0))
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)
time.sleep(0.5)
```



#See Also



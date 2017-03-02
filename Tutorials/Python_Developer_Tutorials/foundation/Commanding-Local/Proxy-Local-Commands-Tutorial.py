# This example will show how to command Faraday using the basic command application.
# LED's being commanded may be receiving other commands and not work as intended (i.e. RED due to RF TX indication)

# Imports - General

import os
import sys
import time
import ConfigParser

sys.path.append(os.path.join(os.path.dirname(__file__),
                             "../../../../Faraday_Proxy_Tools"))  # Append path to common tutorial FaradayIO module

# Imports - Faraday Specific
from FaradayIO import faradaybasicproxyio
from FaradayIO import faradaycommands
from FaradayIO import gpioallocations

# Open configuration INI
config = ConfigParser.RawConfigParser()
filename = os.path.abspath("command_local.ini")
config.read(filename)

# Definitions

# Variables
local_device_callsign = config.get("DEVICES",
                                   "UNIT0CALL").upper()  # Should match the connected Faraday unit as assigned in Proxy configuration
local_device_node_id = config.getint("DEVICES",
                                  "UNIT0ID")  # Should match the connected Faraday unit as assigned in Proxy configuration

# Start the proxy server after configuring the configuration file correctly
# Setup a Faraday IO object
faraday_1 = faradaybasicproxyio.proxyio()  # default proxy port
faraday_cmd = faradaycommands.faraday_commands()

##############
## TOGGLE GPIO
##############
# Turn LED 1 ON LOCAL
print "Turning ON the Green LED (LED #1)"
command = faraday_cmd.CommandLocalGPIOLED1On()
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)
time.sleep(1)

# Turn LED 1 OFF LOCAL
print "Turning OFF the Green LED (LED #1)"
command = faraday_cmd.CommandLocalGPIOLED1Off()
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)

# Turn LED 2 ON LOCAL
print "Turning ON the Red LED (LED #2)"
command = faraday_cmd.CommandLocalGPIOLED2On()
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)
time.sleep(1)

# Turn LED 2 OFF LOCAL
print "Turning Off the Red LED (LED #2)"
command = faraday_cmd.CommandLocalGPIO(0, 0, 0, gpioallocations.LED_2, 0, 0)  # This examples how the non predefined LED GPIO commanding is created.
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)
time.sleep(1)  # Delay so it is obvious that both LED's turn on at the same time in the next command

# Turn Both LED 1 and LED 2 ON simultaneously
print "Turning ON both the Green and Red LED (LED #1 | LED #2)"
command = faraday_cmd.CommandLocalGPIO((gpioallocations.LED_1 | gpioallocations.LED_2), 0, 0, 0, 0, 0)
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)
time.sleep(1)

# Turn Both LED 1 and LED 2 OFF simultaneously
print "Turning Off both the Green and Red LED (LED #1 + LED #2)"
command = faraday_cmd.CommandLocalGPIO(0, 0, 0, (gpioallocations.LED_1 | gpioallocations.LED_2), 0, 0)
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)


###############
## ECHO MESSAGE
###############
print "\n** Beginning ECHO command test** \n"
originalmsg = "This will ECHO back on UART"  # Cannot be longer than max UART Transport layer payload size!

# Display information
print "**Sending**\n"
print "Original Message: ", originalmsg

#  Create command packet
command = faradaycommands.commandmodule.create_command_datagram(faraday_cmd.CMD_ECHO, originalmsg)
#  Send command
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)
#  Retrive waiting data packet in UART Transport service number for the COMMAND application (Use GETWait() to block until ready or timeout
rx_echo_raw = faraday_1.GETWait(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT,
                                sec_timeout=3)  # Wait for up to 3 seconds for data to arrive

try:
    # Decode BASE 64 encoded data from Proxy - Only using the [0] index packet (first) if multiple are retrieved
    b64_data = rx_echo_raw[0]['data']
    echo_decoded = faraday_1.DecodeRawPacket(b64_data)

    # Display information
    print "\n**Receiving**\n"
    print "Decoded received ECHO'd Message:", echo_decoded  # Note that ECHO sends back a fixed packed regardless. Should update to send back exact length.
    print "\nRAW Received BASE64 ECHO'd Message:", b64_data
    print "\nDecoded BASE64 RAW Bytes:", repr(echo_decoded)

except KeyError as e:
    print "\nFailed ECHO due to Key error:", e
    print "This is a KNOWN BUG (https://github.com/FaradayRF/Faraday-Software/issues/50)"
    print "Retry script execution without restarting proxy"

print "\n************************************"
print "\nQuit with ctrl+c"
while (True):
    # Loop until user presses ctrl+c so they can read response
    time.sleep(1)
    pass

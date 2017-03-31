# This example will show how to command Faraday using the basic command application.
# LED's being commanded may be recieving other commands and not work as intended (i.e. RED due to RF TX indication)

#Imports - General

import os, sys, time
sys.path.append(os.path.join(os.path.dirname(__file__), "../Faraday_Proxy_Tools")) #Append path to common tutorial FaradayIO module

#Imports - Faraday Specific
from FaradayIO import faradaybasicproxyio
from FaradayIO import faradaycommands

#Definitions


#Variables
local_device_callsign = 'KB1LQD'
local_device_node_id = 1

remote_device_callsign = 'KB1LQD'
remote_device_node_id = 0

#Start the proxy server after configuring the configuration file correctly
#Setup a Faraday IO object
faraday_1 = faradaybasicproxyio.proxyio() #default proxy port
faraday_cmd = faradaycommands.faraday_commands()



# #Update RF power
# command = faraday_cmd.CommandLocalUpdatePATable(130)
# faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)
#
# # Command Local RF Telemetry TX
# command = faraday_cmd.CommandLocalRFUpdateNow()
# faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)

#time.sleep(0.5)
#Update RF power
#command = faraday_cmd.CommandLocalUpdatePATable(100)
#faraday_1.POST(remote_device_callsign, remote_device_node_id, faraday_1.CMD_UART_PORT, command)

# Command Local RF Telemetry TX
#command = faraday_cmd.CommandLocalRFUpdateNow()
#print repr(command)
#faraday_1.POST(remote_device_callsign, remote_device_node_id, faraday_1.CMD_UART_PORT, command)

# Command remote RF telemetry
for i in range(0,5):
    command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteRFUpdateNow(remote_device_callsign, remote_device_node_id))
    #print repr(command)
    faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, command)
    time.sleep(0.5)

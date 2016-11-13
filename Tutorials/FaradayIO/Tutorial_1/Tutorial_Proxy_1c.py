#Warning - Must run the "deviceconfiguration" proxy application

#Imports - General

import os
import sys
import requests
import time

sys.path.append(os.path.join(os.path.dirname(__file__), "../")) #Append path to common tutorial FaradayIO module
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../")) #Append path to common tutorial FaradayIO module

#Imports - Faraday Specific
from FaradayIO import faradaybasicproxyio
from FaradayIO import faradaycommands
from FaradayIO import telemetryparser

#Variables
local_device_callsign = 'kb1lqd'
local_device_node_id = 1

#Start the proxy server after configuring the configuration file correctly
#Setup a Faraday IO object
faraday_1 = faradaybasicproxyio.proxyio()
faraday_cmd = faradaycommands.faraday_commands()
faraday_parser = telemetryparser.TelemetryParse()

#########################################################################################
###Get current configuration information post configuration update.
#########################################################################################

#Display current device configuration prior to configuration flash update (Send UART telemetry update now command)
#Send the command to read the entire Flash Memory Info D allocations
faraday_1.POST(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, faraday_cmd.CommandLocalSendReadDeviceConfig())
#Wait up to 1 second for the unit to respond to the command. NOTE: GETWait will return ALL packets received if more than 1 packet (likley not in THIS case)
rx_flashd_data = faraday_1.GETWait(local_device_callsign, local_device_node_id, faraday_1.CMD_UART_PORT, 1, False) #Will block and wait for given time until a packet is recevied

#Decode the first packet in list from BASE 64 to a RAW bytesting
rx_flashd_decoded = faraday_1.DecodeRawPacket(rx_flashd_data[0]['data'])
rx_flashd_decoded_extracted = faraday_parser.ExtractPaddedPacket(rx_flashd_decoded, faraday_parser.flash_config_info_d_struct_len)

print "\n--- Current Device Flash Device Callsign Information ---\n"
current_update_config = faraday_parser.UnpackConfigFlashD(rx_flashd_decoded_extracted, True)

#########################################################################################
###Update configuration using INI file as defined by Faraday device object and functions
#########################################################################################

try:
    requests.post('http://127.0.0.1:8002', params={'callsign':"kb1lqd", 'nodeid':1})
except requests.exceptions.RequestException as e:  # This is the correct syntax
    print e





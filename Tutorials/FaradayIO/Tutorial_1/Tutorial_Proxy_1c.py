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


try:
    r = requests.get("http://127.0.0.1:8002", params={'callsign': str(local_device_callsign), 'nodeid': int(local_device_node_id)})
except requests.exceptions.RequestException as e:  # This is the correct syntax
    print e

#Print JSON dictionary device data from unit
print r
raw_unit_json = r.json()
print "************************************"
print "Unit Callsign-ID:\n", str(raw_unit_json['local_callsign']) + '-' + str(raw_unit_json['local_callsign_id'])
print "RAW Unit JSON Data:", raw_unit_json

print "************************************"
#########################################################################################
###Update configuration using INI file as defined by Faraday device object and functions
#########################################################################################

time.sleep(1) # Sleep to allow unit to process, polling and slow

try:
    r = requests.post('http://127.0.0.1:8002', params={'callsign': str(local_device_callsign), 'nodeid': int(local_device_node_id)})
except requests.exceptions.RequestException as e:  # This is the correct syntax
    print e

time.sleep(5) # Sleep to allow unit to process, polling and slow, not sure why THIS slow...

#Flush old data from UART service port
faraday_1.FlushRxPort(local_device_callsign, local_device_node_id, faraday_1.TELEMETRY_PORT)

try:
    r = requests.get("http://127.0.0.1:8002", params={'callsign': str(local_device_callsign), 'nodeid': int(local_device_node_id)})
except requests.exceptions.RequestException as e:  # This is the correct syntax
    print e

#Print JSON dictionary device data from unit
raw_unit_json = r.json()
print "************************************"
print "Unit Callsign-ID:\n", str(raw_unit_json['local_callsign']) + '-' + str(raw_unit_json['local_callsign_id'])
print "RAW Unit JSON Data:", raw_unit_json

print "************************************"




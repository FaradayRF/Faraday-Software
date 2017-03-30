#Warning - Must run the "deviceconfiguration" proxy application

#Imports - General

import os
import sys
import requests
import base64
import cPickle
import time

sys.path.append(os.path.join(os.path.dirname(__file__), "../../../../Faraday_Proxy_Tools")) #Append path to common tutorial FaradayIO module

#Imports - Faraday Specific
from FaradayIO import faradaybasicproxyio
from FaradayIO import faradaycommands
from FaradayIO import telemetryparser

#Variables
local_device_callsign = 'REPLACEME'  # Should match the connected Faraday unit as assigned in Proxy configuration
local_device_node_id = 0  # Should match the connected Faraday unit as assigned in Proxy configuration


#Start the proxy server after configuring the configuration file correctly
#Setup a Faraday IO object
faraday_1 = faradaybasicproxyio.proxyio()
faraday_cmd = faradaycommands.faraday_commands()
faraday_parser = telemetryparser.TelemetryParse()

#########################################################################################
###Get current configuration information prior to configuration update.
#########################################################################################

#Display current device configuration prior to configuration flash update (Send UART telemetry update now command)
#Send the command to read the entire Flash Memory Info D allocations

try:
    r = requests.get("http://127.0.0.1:8002", params={'callsign': str(local_device_callsign), 'nodeid': int(local_device_node_id)})
except requests.exceptions.RequestException as e:  # This is the correct syntax
    print e

#Print JSON dictionary device data from unit
raw_unit_json = r.json()

# Decode and depickle (serialize) device configuration parsed dictionary data
b64_unit_json = base64.b64decode(raw_unit_json['data'])
unit_configuration_dict = cPickle.loads(b64_unit_json)


print "\n************************************"
print "PRIOR TO CONFIGURATION UPDATE"
print "Unit Callsign-ID:\n", str(unit_configuration_dict['local_callsign'])[0:unit_configuration_dict['local_callsign_length']] + '-' + str(unit_configuration_dict['local_callsign_id'])
print "RAW Unit JSON Data:", unit_configuration_dict
print "************************************"


#########################################################################################
###Update configuration using INI file as defined by Faraday device object and functions
#########################################################################################

time.sleep(3) # Sleep to allow unit to process, polling and slow

try:
    r = requests.post('http://127.0.0.1:8002', params={'callsign': str(local_device_callsign), 'nodeid': int(local_device_node_id)})
except requests.exceptions.RequestException as e:  # This is the correct syntax
    print e

time.sleep(6) # Sleep to allow unit to process, polling and slow, not sure why THIS slow...

try:
    r = requests.get("http://127.0.0.1:8002", params={'callsign': str(local_device_callsign), 'nodeid': int(local_device_node_id)})
except requests.exceptions.RequestException as e:  # This is the correct syntax
    print e

#Print JSON dictionary device data from unit
raw_unit_json = r.json()

# Decode and depickle (serialize) device configuration parsed dictionary data
b64_unit_json = base64.b64decode(raw_unit_json['data'])
unit_configuration_dict = cPickle.loads(b64_unit_json)

print "\n************************************"
print "POST CONFIGURATION UPDATE"
print "Unit Callsign-ID:\n", str(unit_configuration_dict['local_callsign'])[0:unit_configuration_dict['local_callsign_length']] + '-' + str(unit_configuration_dict['local_callsign_id'])
print "RAW Unit JSON Data:", unit_configuration_dict

print "************************************"




#Warning - Must run the "deviceconfiguration" proxy application

#Imports - General

import os
import sys
import requests
import base64
import cPickle
import time
import ConfigParser

sys.path.append(os.path.join(os.path.dirname(__file__), "../../Faraday_Proxy_Tools")) #Append path to common tutorial FaradayIO module

#Imports - Faraday Specific
from FaradayIO import faradaybasicproxyio
from FaradayIO import faradaycommands
from FaradayIO import telemetryparser

#Open configuration INI
config = ConfigParser.RawConfigParser()
filename = os.path.abspath("deviceconfiguration.ini")
config.read(filename)

#Variables
local_device_callsign = config.get("DEVICES","UNIT0CALL")
local_device_node_id = config.get("DEVICES","UNIT0ID")
local_device_callsign = str(local_device_callsign).upper()

hostname = config.get("FLASK","HOST")
port = config.get("FLASK","PORT")

#Start the proxy server after configuring the configuration file correctly
#Setup a Faraday IO object
faraday_1 = faradaybasicproxyio.proxyio()
faraday_cmd = faradaycommands.faraday_commands()
faraday_parser = telemetryparser.TelemetryParse()

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
for item in unit_configuration_dict:
    print item, ' - ', unit_configuration_dict[item]
print "************************************"

delay = raw_input("Hit Enter To Close.")





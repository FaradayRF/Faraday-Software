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

#########################################################################################
###Update configuration using INI file as defined by Faraday device object and functions
#########################################################################################

try:
    print "Sending configuration to {0}-{1}".format(local_device_callsign,local_device_node_id)
    r = requests.post('http://{0}:{1}'.format(hostname,port), params={'callsign': str(local_device_callsign), 'nodeid': int(local_device_node_id)})
    print "Completed configuration to {0}-{1}".format(local_device_callsign,local_device_node_id)

except requests.exceptions.RequestException as e:  # This is the correct syntax
    print e





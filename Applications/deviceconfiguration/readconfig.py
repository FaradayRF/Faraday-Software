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
    r = requests.get("http://127.0.0.1:8002", params={'callsign': str(local_device_callsign), 'nodeid': int(local_device_node_id)})
except requests.exceptions.RequestException as e:
    # Some error occurred
    print r.text

# Obtain JSON response with data from Faraday
raw_unit_json = r.json()

# Decode and depickle (serialize) device configuration parsed dictionary data
b64_unit_json = base64.b64decode(raw_unit_json['data'])
unit_configuration_dict = cPickle.loads(b64_unit_json)

#Print configuration values
print "\n************************************"

print "POST CONFIGURATION UPDATE"
print "\nBASIC"
rx_callsign = str(unit_configuration_dict['local_callsign'])[0:unit_configuration_dict['local_callsign_length']]
print "Unit Callsign:", rx_callsign, repr(rx_callsign)
rx_nodeid = str(unit_configuration_dict['local_callsign_id'])
print "ID:", rx_nodeid, repr(rx_nodeid)
print "CONFIGBOOTBITMASK:", format(unit_configuration_dict['configuration_bitmask'], '#010b')
print "GPIO_P3:", format(unit_configuration_dict['default_gpio_port_3_bitmask'], '#010b')
print "GPIO_P4:", format(unit_configuration_dict['default_gpio_port_4_bitmask'], '#010b')
print "GPIO_P5:", format(unit_configuration_dict['default_gpio_port_5_bitmask'], '#010b')
print "\nRF"
print "BOOT_FREQUENCY_MHZ 0:", str(unit_configuration_dict['default_boot_freq_0'])
print "BOOT_FREQUENCY_MHZ 1:", str(unit_configuration_dict['default_boot_freq_1'])
print "BOOT_FREQUENCY_MHZ 2:", str(unit_configuration_dict['default_boot_freq_2'])
print "BOOT_RF_POWER:", str(unit_configuration_dict['default_rf_power'])
print "\nGPS"
print "DEFAULT_LATITUDE:", str(unit_configuration_dict['default_gps_latitude'])
print "DEFAULT_LATITUDE_DIR:", str(unit_configuration_dict['default_gps_latitude_dir'])
print "DEFAULT_LONGITUDE:", str(unit_configuration_dict['default_longitude'])
print "DEFAULT_LONGITUDE_DIR:", str(unit_configuration_dict['default_longitude_dir'])
print "DEFAULT_ALTITUDE:", str(unit_configuration_dict['default_altitude'])
print "DEFAULT_ALTITUDE_UNITS:", str(unit_configuration_dict['default_altitude_units'])
print "GPS_BOOT_BIT & GPS_PRESENT_BIT:", format(unit_configuration_dict['gps_boot_bitmask'], '#010b')
print "\nTELEMETRY"
print "UART_TELEMETRY_BOOT_BIT & RF_TELEMETRY_BOOT_BIT:", format(unit_configuration_dict['telemetry_boot_bitmask'], '#010b')
print "TELEMETRY_DEFAULT_UART_INTERVAL:", str(unit_configuration_dict['default_telemetry_uart_beacon_interval'])
print "TELEMETRY_DEFAULT_RF_INTERVAL:", str(unit_configuration_dict['default_telemetry_rf_beacon_interval'])

print "************************************"
print "\nQuit with ctrl+c"
while(True):
    #Loop until user presses ctrl+c so they can read response
    time.sleep(1)
    pass
    




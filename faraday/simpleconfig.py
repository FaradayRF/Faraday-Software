#!/usr/bin/env python

#Warning - Must run the "deviceconfiguration" proxy application

#Imports - General

import os
import sys
import requests
import base64
import time
import ConfigParser
import json
import logging.config


#Imports - Faraday Specific
from faraday.proxyio import faradaybasicproxyio
from faraday.proxyio import faradaycommands
from faraday.proxyio import telemetryparser

# Start logging after importing modules
relpath1 = os.path.join('etc', 'faraday')
relpath2 = os.path.join('..', 'etc', 'faraday')
setuppath = os.path.join(sys.prefix, 'etc', 'faraday')
userpath = os.path.join(os.path.expanduser('~'), '.faraday')
path = ''

for location in os.curdir, relpath1, relpath2, setuppath, userpath:
    try:
        logging.config.fileConfig(os.path.join(location, "loggingConfig.ini"))
        path = location
        break
    except ConfigParser.NoSectionError:
        pass

logger = logging.getLogger('SimpleConfig')

#Open configuration INI
config = ConfigParser.RawConfigParser()
filename = os.path.abspath(os.path.join(path, "deviceconfiguration.ini"))
config.read(filename)

#Variables
local_device_callsign = config.get("DEVICES", "CALLSIGN")
local_device_node_id = config.get("DEVICES", "NODEID")
local_device_callsign = str(local_device_callsign).upper()

hostname = config.get("FLASK", "HOST")
port = config.get("FLASK", "PORT")

#Start the proxy server after configuring the configuration file correctly
#Setup a Faraday IO object
faraday_1 = faradaybasicproxyio.proxyio()
faraday_cmd = faradaycommands.faraday_commands()
faraday_parser = telemetryparser.TelemetryParse()

#########################################################################################
###Update configuration using INI file as defined by Faraday device object and functions
#########################################################################################

# Send POST data to Proxy to configure unit
try:
    r = requests.post('http://{0}:{1}'.format(hostname, port), params={'callsign': str(local_device_callsign), 'nodeid': int(local_device_node_id)})
    logging.debug("POST URL: " + r.url)
    logging.info("Sent POST configuration command to Proxy")

except requests.exceptions.RequestException as e:
    # Some error occurred
    logging.error(r.text)

#Check to see if programming was successful (HTTP 204 response)
if r.status_code != 204:
    logging.error(r.text)
else:
    # Programming apparently successful. Let unit reboot and then query for flash data

    timer = 5  # Wait five seconds
    logging.info("Programmed Faraday, waiting {0} seconds for reboot".format(str(timer)))
    while(timer > 0):
        time.sleep(1)  # Sleep to allow unit to process, polling and slow, not sure why THIS slow...
        timer += -1

    try:
        r = requests.get("http://127.0.0.1:8002", params={'callsign': str(local_device_callsign), 'nodeid': int(local_device_node_id)})
    except requests.exceptions.RequestException as e:
        # Some error occurred
        logging.error(r.text)

    # Obtain JSON response with data from Faraday
    raw_unit_json = r.json()

    # Decode and depickle (serialize) device configuration parsed dictionary data
    b64_unit_json = base64.b64decode(raw_unit_json['data'])
    unit_configuration_dict = json.loads(b64_unit_json)
    logging.debug(unit_configuration_dict)

    #Print configuration values
    logging.info("************************************")

    logging.info("POST CONFIGURATION UPDATE")
    logging.info("***BASIC***")
    logging.info("Unit Callsign:", str(unit_configuration_dict['local_callsign'])[0:unit_configuration_dict['local_callsign_length']])
    logging.info("ID: {0}".format(str(unit_configuration_dict['local_callsign_id'])))
    logging.info("CONFIGBOOTBITMASK: {0}".format(unit_configuration_dict['configuration_bitmask'], '#010b'))
    logging.info("GPIO_P3: {0}".format(unit_configuration_dict['default_gpio_port_3_bitmask'], '#010b'))
    logging.info("GPIO_P4: {0}".format(unit_configuration_dict['default_gpio_port_4_bitmask'], '#010b'))
    logging.info("GPIO_P5: {0}".format(unit_configuration_dict['default_gpio_port_5_bitmask'], '#010b'))
    logging.info("***RF***")
    logging.info("BOOT_FREQUENCY_MHZ 0: {0}".format(str(unit_configuration_dict['default_boot_freq_0'])))
    logging.info( "BOOT_FREQUENCY_MHZ 1: {0}".format(str(unit_configuration_dict['default_boot_freq_1'])))
    logging.info( "BOOT_FREQUENCY_MHZ 2: {0}".format(str(unit_configuration_dict['default_boot_freq_2'])))
    logging.info( "BOOT_RF_POWER: {0}".format(str(unit_configuration_dict['default_rf_power'])))
    logging.info( "***GPS***")
    logging.info( "DEFAULT_LATITUDE: {0}".format(str(unit_configuration_dict['default_gps_latitude'])))
    logging.info( "DEFAULT_LATITUDE_DIR: {0}".format(str(unit_configuration_dict['default_gps_latitude_dir'])))
    logging.info( "DEFAULT_LONGITUDE: {0}".format(str(unit_configuration_dict['default_longitude'])))
    logging.info( "DEFAULT_LONGITUDE_DIR: {0}".format(str(unit_configuration_dict['default_longitude_dir'])))
    logging.info( "DEFAULT_ALTITUDE: {0}".format(str(unit_configuration_dict['default_altitude'])))
    logging.info( "DEFAULT_ALTITUDE_UNITS: {0}".format(str(unit_configuration_dict['default_altitude_units'])))
    logging.info( "GPS_BOOT_BIT & GPS_PRESENT_BIT: {0}".format(unit_configuration_dict['gps_boot_bitmask'], '#010b'))
    logging.info( "***TELEMETRY***")
    logging.info( "UART_TELEMETRY_BOOT_BIT & RF_TELEMETRY_BOOT_BIT: {0}".format(unit_configuration_dict['telemetry_boot_bitmask'], '#010b'))
    logging.info( "TELEMETRY_DEFAULT_UART_INTERVAL: {0}".format(str(unit_configuration_dict['default_telemetry_uart_beacon_interval'])))
    logging.info( "TELEMETRY_DEFAULT_RF_INTERVAL: {0}".format(str(unit_configuration_dict['default_telemetry_rf_beacon_interval'])))
    logging.info( "************************************")
    logging.info( "Quit with ctrl+c")
    while True:
        #Loop until user presses ctrl+c so they can read response
        time.sleep(1)
        pass

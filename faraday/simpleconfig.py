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
import argparse


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

# Add command line options
parser = argparse.ArgumentParser(description='SimpleConfig sends a request to faraday-deviceconfiguration to initiate a POST or GET command resulting in programming a Faraday radio and/or reading its FLASH memory configuration')

parser.add_argument('--read', action='store_true', help='Read FLASH configuration only, do not program')

# Parse the arguments
args = parser.parse_args()

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
if not args.read:
    try:
        r = requests.post('http://{0}:{1}'.format(hostname, port), params={'callsign': str(local_device_callsign), 'nodeid': int(local_device_node_id)})
        logger.debug("POST URL: " + r.url)
        logger.info("Sent POST configuration command to Proxy")

    except requests.exceptions.RequestException as e:
        # Some error occurred
        logger.error(r.text)

    #Check to see if programming was successful (HTTP 204 response)
    if r.status_code != 204:
        logger.error(r.text)

    # Programming apparently successful. Let unit reboot and then query for flash data
    timer = 5  # Wait five seconds
    logger.info("Programmed Faraday, waiting {0} seconds for reboot".format(str(timer)))

    while (timer > 0):
        time.sleep(1)  # Sleep to allow unit to process, polling and slow, not sure why THIS slow...
        timer += -1


# Read configuration of FLASH memory
try:
    r = requests.get('http://{0}:{1}'.format(hostname, port), params={'callsign': str(local_device_callsign), 'nodeid': int(local_device_node_id)})
except requests.exceptions.RequestException as e:
    # Some error occurred
    logger.error(r.text)

# Obtain JSON response with data from Faraday
raw_unit_json = r.json()

# Decode and depickle (serialize) device configuration parsed dictionary data
b64_unit_json = base64.b64decode(raw_unit_json['data'])
unit_configuration_dict = json.loads(b64_unit_json)
logger.debug(unit_configuration_dict)

#Print configuration values
logger.info("************************************")
logger.info("POST CONFIGURATION UPDATE")
logger.info("***BASIC***")
logger.info("Unit Callsign:", str(unit_configuration_dict['local_callsign'])[0:unit_configuration_dict['local_callsign_length']])
logger.info("ID: {0}".format(str(unit_configuration_dict['local_callsign_id'])))
logger.info("CONFIGBOOTBITMASK: {0}".format(unit_configuration_dict['configuration_bitmask'], '#010b'))
logger.info("GPIO_P3: {0}".format(unit_configuration_dict['default_gpio_port_3_bitmask'], '#010b'))
logger.info("GPIO_P4: {0}".format(unit_configuration_dict['default_gpio_port_4_bitmask'], '#010b'))
logger.info("GPIO_P5: {0}".format(unit_configuration_dict['default_gpio_port_5_bitmask'], '#010b'))
logger.info("***RF***")
logger.info("BOOT_FREQUENCY_MHZ 0: {0}".format(str(unit_configuration_dict['default_boot_freq_0'])))
logger.info("BOOT_FREQUENCY_MHZ 1: {0}".format(str(unit_configuration_dict['default_boot_freq_1'])))
logger.info("BOOT_FREQUENCY_MHZ 2: {0}".format(str(unit_configuration_dict['default_boot_freq_2'])))
logger.info("BOOT_RF_POWER: {0}".format(str(unit_configuration_dict['default_rf_power'])))
logger.info("***GPS***")
logger.info("DEFAULT_LATITUDE: {0}".format(str(unit_configuration_dict['default_gps_latitude'])))
logger.info("DEFAULT_LATITUDE_DIR: {0}".format(str(unit_configuration_dict['default_gps_latitude_dir'])))
logger.info("DEFAULT_LONGITUDE: {0}".format(str(unit_configuration_dict['default_longitude'])))
logger.info("DEFAULT_LONGITUDE_DIR: {0}".format(str(unit_configuration_dict['default_longitude_dir'])))
logger.info("DEFAULT_ALTITUDE: {0}".format(str(unit_configuration_dict['default_altitude'])))
logger.info("DEFAULT_ALTITUDE_UNITS: {0}".format(str(unit_configuration_dict['default_altitude_units'])))
logger.info("GPS_BOOT_BIT & GPS_PRESENT_BIT: {0}".format(unit_configuration_dict['gps_boot_bitmask'], '#010b'))
logger.info("***TELEMETRY***")
logger.info("UART_TELEMETRY_BOOT_BIT & RF_TELEMETRY_BOOT_BIT: {0}".format(unit_configuration_dict['telemetry_boot_bitmask'], '#010b'))
logger.info("TELEMETRY_DEFAULT_UART_INTERVAL: {0}".format(str(unit_configuration_dict['default_telemetry_uart_beacon_interval'])))
logger.info("TELEMETRY_DEFAULT_RF_INTERVAL: {0}".format(str(unit_configuration_dict['default_telemetry_rf_beacon_interval'])))
logger.info("************************************")
logger.info("Quit with ctrl+c")

while True:
    #Loop until user presses ctrl+c so they can read response
    time.sleep(1)
    pass

#-------------------------------------------------------------------------------
# Name:        /faraday/simpleconfig.py
# Purpose:     Kick off faraday-deviceconfiguration programming via API and
#              print results to the screen
#
# Author:      Brent Salmi / Bryce Salmi
#
# Created:     7/2/2017
# Licence:     GPLv3
#-------------------------------------------------------------------------------

#Imports - General
import os
import sys
import requests
import base64
import time
import ConfigParser
import json
import argparse


#Imports - Faraday Specific
from faraday.proxyio import faradaybasicproxyio
from faraday.proxyio import faradaycommands
from faraday.proxyio import telemetryparser
from classes import helper

# Global Filenames
configTruthFile = "deviceconfiguration.sample.ini"
configFile = "deviceconfiguration.ini"

# Start logging after importing modules
faradayHelper = helper.Helper("SimpleConfig")
logger = faradayHelper.getLogger()

# Create configuration paths
deviceConfigPath = os.path.join(faradayHelper.path, configFile)

deviceConfigurationConfig = ConfigParser.RawConfigParser()
deviceConfigurationConfig.read(deviceConfigPath)

# Add command line options
parser = argparse.ArgumentParser(description='SimpleConfig sends a request to faraday-deviceconfiguration to initiate a POST or GET command resulting in programming a Faraday radio and/or reading its FLASH memory configuration')

parser.add_argument('--read', action='store_true', help='Read FLASH configuration only, do not program')
parser.add_argument('--start', action='store_true', help='Start SimpleConfig script')

# Parse the arguments
args = parser.parse_args()

# Check for --start option and exit if not present
if not args.start:
    logger.warning("--start option not present, exiting SimpleConfig script!")
    sys.exit(0)

#Variables
local_device_callsign = deviceConfigurationConfig.get("DEVICES", "CALLSIGN")
local_device_node_id = deviceConfigurationConfig.get("DEVICES", "NODEID")
local_device_callsign = str(local_device_callsign).upper()

hostname = deviceConfigurationConfig.get("FLASK", "HOST")
port = deviceConfigurationConfig.get("FLASK", "PORT")

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
        logger.error("Request exception!")
        logger.error("Is \'faraday-deviceconfiguration\' configured and running?")
        sys.exit(0)

    except ValueError as e:
        # Some error occurred
        logger.error("ValueError!")
        logger.error("Is \'faraday-deviceconfiguration\' configured correctly for Proxy?")
        sys.exit(0)

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
    logger.error("Request exception!")
    logger.error("Is \'faraday-deviceconfiguration\' configured and running?")
    sys.exit(0)

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
logger.info("Unit Callsign: {0}".format(str(unit_configuration_dict['local_callsign'])[0:unit_configuration_dict['local_callsign_length']]))
logger.info("ID: {0}".format(str(unit_configuration_dict['local_callsign_id'])))

# Convert configboot bitmask to a list and display
bootbitmask = bin(unit_configuration_dict['configuration_bitmask'])[2:].zfill(8)
bootbitmask = list(bootbitmask)
bootbitmask.reverse()
logger.info("UNITCONFIGURED: {0}".format(bootbitmask[0]))
logger.info("REDLEDTX: {0}".format(bootbitmask[1]))
logger.info("GREENLEDRX: {0}".format(bootbitmask[2]))

# Convert gpiop3 bitmask to a list and display
gpiop3 = bin(unit_configuration_dict['default_gpio_port_3_bitmask'])[2:].zfill(8)
gpiop3 = list(gpiop3)
gpiop3.reverse()
logger.info("GPIO_P3_0: {0}".format(gpiop3[0]))
logger.info("GPIO_P3_1: {0}".format(gpiop3[1]))
logger.info("GPIO_P3_2: {0}".format(gpiop3[2]))
logger.info("GPIO_P3_3: {0}".format(gpiop3[3]))
logger.info("GPIO_P3_4: {0}".format(gpiop3[4]))
logger.info("GPIO_P3_5: {0}".format(gpiop3[5]))
logger.info("GPIO_P3_6: {0}".format(gpiop3[6]))
logger.info("GPIO_P3_7: {0}".format(gpiop3[7]))

# Convert gpiop4 bitmask to a list and display
gpiop4 = bin(unit_configuration_dict['default_gpio_port_4_bitmask'])[2:].zfill(8)
gpiop4 = list(gpiop4)
gpiop4.reverse()
logger.info("GPIO_P4_0: {0}".format(gpiop4[0]))
logger.info("GPIO_P4_1: {0}".format(gpiop4[1]))
logger.info("GPIO_P4_2: {0}".format(gpiop4[2]))
logger.info("GPIO_P4_3: {0}".format(gpiop4[3]))
logger.info("GPIO_P4_4: {0}".format(gpiop4[4]))
logger.info("GPIO_P4_5: {0}".format(gpiop4[5]))
logger.info("GPIO_P4_6: {0}".format(gpiop4[6]))
logger.info("GPIO_P4_7: {0}".format(gpiop4[7]))

# Convert gpiop5 bitmask to a list and display
gpiop5 = bin(unit_configuration_dict['default_gpio_port_5_bitmask'])[2:].zfill(8)
gpiop5 = list(gpiop5)
gpiop5.reverse()
logger.info("GPIO_P5_0: {0}".format(gpiop5[0]))
logger.info("GPIO_P5_1: {0}".format(gpiop5[1]))
logger.info("GPIO_P5_2: {0}".format(gpiop5[2]))
logger.info("GPIO_P5_3: {0}".format(gpiop5[3]))
logger.info("GPIO_P5_4: {0}".format(gpiop5[4]))
logger.info("GPIO_P5_5: {0}".format(gpiop5[5]))
logger.info("GPIO_P5_6: {0}".format(gpiop5[6]))
logger.info("GPIO_P5_7: {0}".format(gpiop5[7]))

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

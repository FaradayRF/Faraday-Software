#-------------------------------------------------------------------------------
# Name:         debug.py
# Purpose:      Connects to a localhost proxy.py and automatically queries for
#               open application ports sending Faraday data and then requests
#               data for each open port and displays the decoded values (BASE64)
#
# Author:      Bryce Salmi
#
# Created:     03/04/2016
# Copyright:   (c) Bryce 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import json
import requests
import time
import threading
from collections import deque
import logging
import base64
import datetime
import CC430_Radio_Config
import struct
from ConfigParser import SafeConfigParser
#from faraday import FaradayRF_CMD
#from Command_Module import Command_Module

## Is this a deprecated script now? Used?


def create_test_config_packet():
    #Create a device configuration class (this allows rolling creation/edit of the configuration packet)
    test = Command_Module.Device_Config_Class()

    #Update bitmask for basic configurations
    config_bitmask = test.update_bitmask_configuration(True)
    p3_bitmask = test.update_bitmask_gpio_p3(0,0,0,0,1,0,0,0)
    p4_bitmask = test.update_bitmask_gpio_p4(0,0,0,1,0,0,0,0)

    #Update the local basic information
    test.update_basic(config_bitmask, 'kb1lqd', 5, p3_bitmask, p4_bitmask)

    #Update default RF configuration
    test.update_rf(915.500)

    #Update the GPS configuration
    gps_boot_bitmask = test.update_bitmask_gps_boot(True)
    test.update_gps(gps_boot_bitmask, '52.4162', 'N', '22.6021', 'W', '37.5', 'M')

    #Update the Telemetry configuration
    telem_boot_bitmask = test.update_bitmask_telemetry_boot(True, True)
    test.update_telemetry(telem_boot_bitmask, 1, 10)

    #Create the configuration command packet payload
    packet_config = test.create_config_packet()

    #Create the full command packet with configuration packet as payload
    command_packet = Command_Module.create_command_packet(255, packet_config)

    return command_packet

def test_update():
    #Create test configuration packet
    config_packet_payload = create_test_config_packet()

    #Transmit configuration packet (Port 2)
    #service_number = 2
    #Faraday_Device.uartDevice.transmit_service_payload(int(service_number), len(config_packet_payload), config_packet_payload)

    b64cmd = base64.b64encode(config_packet_payload)
    #print b64cmd
    status = requests.post('http://127.0.0.1:5000/faraday/2?cmd=%s' % b64cmd)
    return status

def main():
    """main function reads in configuration and sends commands"""

    #setup SQLite Uploader from configuration file
##    parser = SafeConfigParser()
##    parser.read('faraday.ini')
##    callsign = str(parser.get('faraday','callsign'))
##    nodeid = int(parser.get('faraday','nodeid'))
##    powerconf = int(parser.get('faraday','powerconf'))
##    bootfreq = float(parser.get('faraday','bootfreq'))
##    gpsboot = int(parser.get('faraday','gpsboot'))
##    uarttelemboot = int(parser.get('faraday','uarttelemboot'))
##    rftelemboot = int(parser.get('faraday','rftelemboot'))
##
##    print "CALLSIGN: ", callsign
##    print "NODEID: ", nodeid
##    print "POWERCONF: ", powerconf
##    print "BOOTFREQ: ", bootfreq
##    print "GPSBOOT: ", gpsboot
##    print "UARTTELEMBOOT: ", uarttelemboot
##    print "RFTELEMBOOT: ", rftelemboot, "\n"

    #faraday = FaradayRF_CMD()
    stat = test_update()
    #stat = send_config(faraday, callsign, nodeid,powerconf, bootfreq, gpsboot, uarttelemboot, rftelemboot)
    print "POST command status: ", stat.status_code





if __name__ == '__main__':
    main()

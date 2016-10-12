#-------------------------------------------------------------------------------
# Name:        /telemetry/telemetry.py
# Purpose:      Query proxy for telemetry data and parse it to a local database
#               as well as provide a RESTful interface to decoded data.
#
# Author:      Bryce Salmi
#
# Created:     11/10/2016
# Licence:     GPLv3
#-------------------------------------------------------------------------------

import time
import logging
import logging.config
import threading
import ConfigParser
from collections import deque
import os
import sys

from flask import Flask
from flask import request

# Can we clean this up?
sys.path.append(os.path.join(os.path.dirname(__file__), "../Faraday_Proxy_Tools/")) #Append path to common tutorial FaradayIO module
from FaradayIO import faradaybasicproxyio
from FaradayIO import telemetryparser

# Start logging after importing modules
logging.config.fileConfig('loggingConfig.ini')
logger = logging.getLogger('telemetry')

# Load Telemetry Configuration from telemetry.ini file
# Should have common file for apps...
telemetryConfig = ConfigParser.RawConfigParser()
telemetryConfig.read('telemetry.ini')

# Create and initialize dictionary queues
getDicts = {}


def telemetry_worker(config):
    """
    Interface Faraday Proxy to obtain telemtry

    This function interfaces the Proxy application via its RESTful interface.
    It is a one-way operation as it makes no sense to POST data to proxy for
    telemetry to a specific unit with this application.
    """
    logger.info('Starting telemetry_worker thread')

    # initialize variables
    stations = {}



    # Initialize proxy object
    proxy = faradaybasicproxyio.proxyio()

    # Pragmatically create descriptors for each Faraday connected to Proxy
    count = config.getint("telemetry", "units")

    for num in range(count):
        callsign = config.get("telemetry", "unit" + str(num) + "call").upper()
        nodeid = config.get("telemetry", "unit" + str(num) + "id")
        stations["UNIT" + str(num) + "CALL"] = callsign
        stations["UNIT" + str(num) + "ID"] = nodeid
        getDicts[str(callsign) + str(nodeid)] = deque([], maxlen=10)

    # check for data on telemetry port, if True place into deque
    while(1):
         for radio in range(count):
            callsign = stations["UNIT" + str(num) + "CALL"]
            nodeid = stations["UNIT" + str(num) + "ID"]
            data = proxy.GET(str(callsign), str(nodeid), int(proxy.TELEMETRY_PORT))

            # Iterate through each packet and append to station dictionary
            if data != None:
                for item in data:
                    getDicts[str(callsign) + str(nodeid)].append(item)
            print getDicts

         time.sleep(0.5) # should slow down

def main():
    """Main function which starts telemery worker thread + Flask server."""
    logger.info('Starting telemetry server')

    # Initialize local variables
    threads = []

    t = threading.Thread(target=telemetry_worker, args=(telemetryConfig,))
    threads.append(t)
    t.start()

    #telemetry_worker(telemetryConfig);

if __name__ == '__main__':
    main()
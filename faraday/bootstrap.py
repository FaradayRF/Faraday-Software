#-------------------------------------------------------------------------------
# Name:        /faraday/bootstrap.py
# Purpose:     Bootstrap loads firmware onto the Faraday Wireless Node via USB
#
# Author:      Bryce Salmi
#
# Created:     7/12/2017
# Licence:     GPLv3
#-------------------------------------------------------------------------------

import logging.config
#import threading
import ConfigParser
#import socket
#import requests
import os
#from time import sleep
import sys
import argparse
import shutil
import subprocess

from classes import createtiscript
from classes import faradayFTDI

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

logger = logging.getLogger('BSL')

#Create APRS configuration file path
bslConfigPath = os.path.join(path, "bsl.ini")
logger.debug('bsl.ini PATH: ' + bslConfigPath)

bslConfig = ConfigParser.RawConfigParser()
bslConfig.read(bslConfigPath)

# Command line input
parser = argparse.ArgumentParser(description='BSL will Boostrap load firmware onto Faraday via USB connection')
parser.add_argument('--init-config', dest='init', action='store_true', help='Initialize BSL configuration file')
parser.add_argument('--start', action='store_true', help='Start APRS server')

# Parse the arguments
args = parser.parse_args()


def initializeBSLConfig():
    '''
    Initialize BSL configuration file from bsl.sample.ini

    :return: None, exits program
    '''

    logger.info("Initializing BSL")
    shutil.copy(os.path.join(path, "bsl.sample.ini"), os.path.join(path, "bsl.ini"))
    logger.info("Initialization complete")
    sys.exit(0)


def configureBSL(args, bslConfigPath):
    '''
    Configure BSL configuration file from command line

    :param args: argparse arguments
    :param bslConfigPath: Path to bsl.ini file
    :return: None
    '''

    config = ConfigParser.RawConfigParser()
    config.read(os.path.join(path, "bsl.ini"))

    # if args.callsign is not None:
    #     config.set('APRSIS', 'CALLSIGN', args.callsign)

    with open(bslConfigPath, 'wb') as configfile:
        config.write(configfile)


# Now act upon the command line arguments
# Initialize and configure bsl
if args.init:
    initializeBSLConfig()
configureBSL(args, bslConfigPath)

# Read in BSL configuration parameters
bslFile = bslConfig.read(bslConfigPath)

# Check for --start option and exit if not present
if not args.start:
    logger.warning("--start option not present, exiting BSL server!")
    sys.exit(0)


def main():
    """
    Main function which starts the Boostrap Loader.

    :return: None
    """

    logger.info('Starting Faraday Bootstrap Loader application')

    #print os.path.join(path, 'firmware.txt')

    filename = bslConfig.get("BOOTSTRAP", "FILENAME")
    port = bslConfig.get("BOOTSTRAP", "PORT")

    test = createtiscript.CreateTiBslScript(path, filename, port)

    test.createscript()

    #Enable BSL Mode
    device_bsl = faradayFTDI.FtdiD2xxCbusControlObject()
    #
    device_bsl.EnableBslMode()
    subprocess.call([os.path.join(path, 'bsl-scripter-windows.exe'), os.path.join(path, 'faradayFirmwareUpgradeScript.txt')])
    device_bsl.DisableBslMode()


    # Initialize local variables
    #threads = []

    # t = threading.Thread(target=aprs_worker, args=(aprsConfig, sock))
    # threads.append(t)
    # t.start()


if __name__ == '__main__':
    main()

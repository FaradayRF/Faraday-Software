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
import urllib2

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
parser = argparse.ArgumentParser(description='BSL will Boostrap load firmware onto Faraday via USB connection. Requires http://www.ftdichip.com/Drivers/D2XX.htm')
parser.add_argument('--init-config', dest='init', action='store_true', help='Initialize BSL configuration file')
parser.add_argument('--start', action='store_true', help='Start APRS server')
parser.add_argument('--getmaster', action='store_true', help='Download newest firmware from master firmware repository')
parser.add_argument('--port', help='Set UART port to bootstrap load firmware')

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

    if args.port is not None:
        config.set('BOOTSTRAP', 'COM', args.port)

    # if args.callsign is not None:
    #     config.set('APRSIS', 'CALLSIGN', args.callsign)

    with open(bslConfigPath, 'wb') as configfile:
        config.write(configfile)

def getMaster():
    '''
    Downloads latest firmware from master github repo

    :return: None, exits program
    '''

    url = bslConfig.get("BOOTSTRAP", "MASTERURL")
    logger.info("Downloading latest Master firmware...")

    # Download latest firmware from url
    response = urllib2.urlopen(url)
    data = response.read()
    logger.debug(data)

    firmwarePath = os.path.join(os.path.expanduser('~'), '.faraday', 'firmware')

    # Create folders if not present
    try:
        os.makedirs(firmwarePath)
    except:
        pass

    # Create master.txt if it doesn't exist, otherwise write over it
    firmware = os.path.join(firmwarePath, 'master.txt')
    f = open(firmware, 'w+')
    f.write(data)
    f.close()

    logger.info("Download complete")


# Now act upon the command line arguments
# Initialize and configure bsl
if args.init:
    initializeBSLConfig()
configureBSL(args, bslConfigPath)

# Read in BSL configuration parameters
bslFile = bslConfig.read(bslConfigPath)

# Check for --getmaster
if args.getmaster:
    getMaster()

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
    outputFilename = bslConfig.get("BOOTSTRAP", "OUTPUTFILENAME")
    upgradeScript = bslConfig.get("BOOTSTRAP", "FIRMWAREUPGRADESCRIPT")
    bslExecutable = bslConfig.get("BOOTSTRAP", "BSLEXECUTABLE")
    port = bslConfig.get("BOOTSTRAP", "COM")

    script = createtiscript.CreateTiBslScript(path,
                                            filename,
                                            port,
                                            outputFilename,
                                            upgradeScript,
                                            logger)

    script.createscript()

    #Enable BSL Mode
    device_bsl = faradayFTDI.FtdiD2xxCbusControlObject()
    #
    device_bsl.EnableBslMode()
    subprocess.call([os.path.join(path, bslExecutable), os.path.join(path, upgradeScript)])
    device_bsl.DisableBslMode()


    # Initialize local variables
    #threads = []

    # t = threading.Thread(target=aprs_worker, args=(aprsConfig, sock))
    # threads.append(t)
    # t.start()


if __name__ == '__main__':
    main()

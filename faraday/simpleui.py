#-------------------------------------------------------------------------------
# Name:        /faraday/simpleui.py
# Purpose:     SimpleUI provides a no frills method of interfacing Faraday telemetry
#              with a webpage in a formatted manner. This is different than the
#              Telemetry application since it renders the data in an automatically
#              updating manner using Javascript.
#
# Author:      Bryce Salmi
#
# Created:     4/27/2017
# Licence:     GPLv3
#-------------------------------------------------------------------------------

import json
import logging.config
import ConfigParser
import os
import sys
import argparse
import shutil
import webbrowser

from flask import Flask
from flask import request
from flask import render_template
from flask import redirect

# Imports - Faraday Specific
from faraday.proxyio import faradaybasicproxyio
from faraday.proxyio import faradaycommands
from faraday.proxyio import gpioallocations

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

logger = logging.getLogger('SimpleUI')

#Create SimpleUI configuration file path
simpleuiConfigPath = os.path.join(path, "simpleui.ini")
logger.debug('simpleui.ini PATH: ' + simpleuiConfigPath)

simpleuiConfig = ConfigParser.RawConfigParser()

# Command line input
parser = argparse.ArgumentParser(description='SimpleUI application provides a simple user interface for Faraday radios at http://localhost/')
parser.add_argument('--start', action='store_true', help='Start SimpleUI in browser')
parser.add_argument('--init-config', dest='init', action='store_true', help='Initialize SimpleUI configuration file')
parser.add_argument('--callsign', help='Set Local SimpleUI callsign for data display')
parser.add_argument('--nodeid', help='Set Local SimpleUI nodeid for data display')
parser.add_argument('--cmdlocalcallsign', help='Set Local SimpleUI command callsign')
parser.add_argument('--cmdlocalnodeid', help='Set Local SimpleUI command nodeid')
parser.add_argument('--cmdremotecallsign', help='Set remote SimpleUI command callsign')
parser.add_argument('--cmdremotenodeid', help='Set remote SimpleUI command nodeid')
parser.add_argument('--flaskhost', help='Set Flask server hostname/address')
parser.add_argument('--flaskport', help='Set Flask server port')
parser.add_argument('--proxyhost', help='Set Proxy server hostname/address')
parser.add_argument('--proxyport', help='Set Proxy server port')
parser.add_argument('--telemetryhost', help='Set Telemetry server hostname/address')
parser.add_argument('--telemetryport', help='Set Telemetry server port')

# Parse the arguments
args = parser.parse_args()


def initializeSimpleUIConfig():
    '''
    Initialize SimpleUI configuration file from simpleui.sample.ini

    :return: None, exits program
    '''

    logger.info("Initializing SimpleUI")
    shutil.copy(os.path.join(path, "simpleui.sample.ini"), os.path.join(path, "simpleui.ini"))
    logger.info("Initialization complete")
    sys.exit(0)


def configureSimpleUI(args, simpleuiConfigPath):
    '''
    Configure SimpleUI configuration file from command line

    :param args: argparse arguments
    :param SimpleUIConfigPath: Path to simpleui.ini file
    :return: None
    '''

    config = ConfigParser.RawConfigParser()
    config.read(os.path.join(path, "simpleui.ini"))

    if args.callsign is not None:
        config.set('SIMPLEUI', 'CALLSIGN', args.callsign)
    if args.nodeid is not None:
        config.set('SIMPLEUI', 'NODEID', args.nodeid)
    if args.cmdlocalcallsign is not None:
        config.set('SIMPLEUI', 'LOCALCALLSIGN', args.cmdlocalcallsign)
    if args.cmdlocalnodeid is not None:
        config.set('SIMPLEUI', 'LOCALNODEID', args.cmdlocalnodeid)
    if args.cmdremotecallsign is not None:
        config.set('SIMPLEUI', 'REMOTECALLSIGN', args.cmdremotecallsign)
    if args.cmdremotenodeid is not None:
        config.set('SIMPLEUI', 'REMOTENODEID', args.cmdremotenodeid)
    if args.flaskhost is not None:
        config.set('FLASK', 'HOST', args.flaskhost)
    if args.flaskport is not None:
        config.set('FLASK', 'PORT', args.flaskport)
    if args.proxyhost is not None:
        config.set('PROXY', 'HOST', args.proxyhost)
    if args.proxyport is not None:
        config.set('PROXY', 'PORT', args.proxyport)
    if args.telemetryhost is not None:
        config.set('TELEMETRY', 'HOST', args.telemetryhost)
    if args.telemetryport is not None:
        config.set('TELEMETRY', 'PORT', args.telemetryport)

    with open(simpleuiConfigPath, 'wb') as configfile:
        config.write(configfile)


# Now act upon the command line arguments
# Initialize and configure SimpleUI
if args.init:
    initializeSimpleUIConfig()
configureSimpleUI(args, simpleuiConfigPath)

# Read in configuration file settings
simpleuiConfig.read(simpleuiConfigPath)

# Start web browser pointed to SimpleUI if requested
if args.start:
    host = simpleuiConfig.get("FLASK", "HOST")
    port = simpleuiConfig.get("FLASK", "PORT")
    url = "http://" + host + ":" + port

    logging.debug("SimpleUI URL: " + url)

    webbrowser.open_new(url)


# Initialize Flask microframework
app = Flask(__name__,
            static_folder='../Applications/SimpleUI/static',
            template_folder='../Applications/SimpleUI/templates')


@app.route('/', methods=['GET', 'POST'])
def simpleui():
    """
    Provides a simple user interface with python and javascript

    Uses Flask to return the user interface template file when a GET request is made while this function
    checks form data for appropriate commands intended to be sent to a local/remote station. Once completed
    the user is redirected to the main simpleui page.
    """
    if request.method == "GET":
        # Obtain telemetry station from config file
        callsign = simpleuiConfig.get("SIMPLEUI", "CALLSIGN").upper()
        nodeid = simpleuiConfig.getint("SIMPLEUI", "NODEID")

        #Return HTML/Javascript template
        return render_template('index.html',
                               callsign=callsign,
                               nodeid=nodeid)

    if request.method == "POST":
        # Start the proxy server after configuring the configuration file correctly
        # Setup a Faraday IO object
        faraday_1 = faradaybasicproxyio.proxyio()  # default proxy port
        faraday_cmd = faradaycommands.faraday_commands()

        # Obtain local station from config file, check form data for intended command
        callsign = simpleuiConfig.get("SIMPLEUI", "LOCALCALLSIGN").upper()
        nodeid = simpleuiConfig.getint("SIMPLEUI", "LOCALNODEID")

        if request.form["IO"] == "LED1 ON":
            logger.debug("Local {0}-{1} LED1 commanded ON".format(callsign, nodeid))
            command = faraday_cmd.CommandLocalGPIOLED1On()

        if request.form["IO"] == "LED1 OFF":
            logger.debug("Local {0}-{1} LED1 commanded OFF".format(callsign, nodeid))
            command = faraday_cmd.CommandLocalGPIOLED1Off()

        if request.form["IO"] == "LED2 ON":
            logger.debug("Local {0}-{1} LED2 commanded ON".format(callsign, nodeid))
            command = faraday_cmd.CommandLocalGPIOLED2On()

        if request.form["IO"] == "LED2 OFF":
            logger.debug("Local {0}-{1} LED2 commanded OFF".format(callsign, nodeid))
            command = faraday_cmd.CommandLocalGPIOLED2Off()

        if request.form["IO"] == "GPIO0 ON":
            logger.debug("Local {0}-{1} GPIO0 commanded ON".format(callsign, nodeid))
            command = faraday_cmd.CommandLocalGPIO(gpioallocations.DIGITAL_IO_0, 0, 0, 0, 0, 0)

        if request.form["IO"] == "GPIO0 OFF":
            logger.debug("Local {0}-{1} GPIO0 commanded OFF".format(callsign, nodeid))
            command = faraday_cmd.CommandLocalGPIO(0, 0, 0, gpioallocations.DIGITAL_IO_0, 0, 0)

        if request.form["IO"] == "GPIO1 ON":
            logger.debug("Local {0}-{1} GPIO1 commanded ON".format(callsign, nodeid))
            command = faraday_cmd.CommandLocalGPIO(gpioallocations.DIGITAL_IO_1, 0, 0, 0, 0, 0)

        if request.form["IO"] == "GPIO1 OFF":
            logger.debug("Local {0}-{1} GPIO1 commanded OFF".format(callsign, nodeid))
            command = faraday_cmd.CommandLocalGPIO(0, 0, 0, gpioallocations.DIGITAL_IO_1, 0, 0)

        if request.form["IO"] == "GPIO2 ON":
            logger.debug("Local {0}-{1} GPIO2 commanded ON".format(callsign, nodeid))
            command = faraday_cmd.CommandLocalGPIO(gpioallocations.DIGITAL_IO_2, 0, 0, 0, 0, 0)

        if request.form["IO"] == "GPIO2 OFF":
            logger.debug("Local {0}-{1} GPI2 commanded OFF".format(callsign, nodeid))
            command = faraday_cmd.CommandLocalGPIO(0, 0, 0, gpioallocations.DIGITAL_IO_2, 0, 0)

        if request.form["IO"] == "GPIO3 ON":
            logger.debug("Local {0}-{1} GPIO3 commanded ON".format(callsign, nodeid))
            command = faraday_cmd.CommandLocalGPIO(0, gpioallocations.DIGITAL_IO_3, 0, 0, 0, 0)

        if request.form["IO"] == "GPIO3 OFF":
            logger.debug("Local {0}-{1} GPIO3 commanded OFF".format(callsign, nodeid))
            command = faraday_cmd.CommandLocalGPIO(0, 0, 0, 0, gpioallocations.DIGITAL_IO_3, 0)

        if request.form["IO"] == "GPIO4 ON":
            logger.debug("Local {0}-{1} GPIO4 commanded ON".format(callsign, nodeid))
            command = faraday_cmd.CommandLocalGPIO(0, gpioallocations.DIGITAL_IO_4, 0, 0, 0, 0)

        if request.form["IO"] == "GPIO4 OFF":
            logger.debug("Local {0}-{1} GPIO4 commanded OFF".format(callsign, nodeid))
            command = faraday_cmd.CommandLocalGPIO(0, 0, 0, 0, gpioallocations.DIGITAL_IO_4, 0)

        if request.form["IO"] == "GPIO5 ON":
            logger.debug("Local {0}-{1} GPIO5 commanded ON".format(callsign, nodeid))
            command = faraday_cmd.CommandLocalGPIO(0, gpioallocations.DIGITAL_IO_5, 0, 0, 0, 0)

        if request.form["IO"] == "GPIO5 OFF":
            logger.debug("Local {0}-{1} GPIO5 commanded OFF".format(callsign, nodeid))
            command = faraday_cmd.CommandLocalGPIO(0, 0, 0, 0, gpioallocations.DIGITAL_IO_5, 0)

        if request.form["IO"] == "GPIO6 ON":
            logger.debug("Local {0}-{1} GPIO6 commanded ON".format(callsign, nodeid))
            command = faraday_cmd.CommandLocalGPIO(0, gpioallocations.DIGITAL_IO_6, 0, 0, 0, 0)

        if request.form["IO"] == "GPIO6 OFF":
            logger.debug("Local {0}-{1} GPIO6 commanded OFF".format(callsign, nodeid))
            command = faraday_cmd.CommandLocalGPIO(0, 0, 0, 0, gpioallocations.DIGITAL_IO_6, 0)

        if request.form["IO"] == "GPIO7 ON":
            logger.debug("Local {0}-{1} GPIO7 commanded ON".format(callsign, nodeid))
            command = faraday_cmd.CommandLocalGPIO(0, gpioallocations.DIGITAL_IO_7, 0, 0, 0, 0)

        if request.form["IO"] == "GPIO7 OFF":
            logger.debug("Local {0}-{1} GPIO7 commanded OFF".format(callsign, nodeid))
            command = faraday_cmd.CommandLocalGPIO(0, 0, 0, 0, gpioallocations.DIGITAL_IO_7, 0)

        if request.form["IO"] == "GPIO8 ON":
            logger.debug("Local {0}-{1} GPIO8 commanded ON".format(callsign, nodeid))
            command = faraday_cmd.CommandLocalGPIO(0, 0, gpioallocations.DIGITAL_IO_8, 0, 0, 0)

        if request.form["IO"] == "GPIO8 OFF":
            logger.debug("Local {0}-{1} GPIO8 commanded OFF".format(callsign, nodeid))
            command = faraday_cmd.CommandLocalGPIO(0, 0, 0, 0, 0, gpioallocations.DIGITAL_IO_8)

        if request.form["IO"] == "MOSFET":
            logger.debug("Local {0}-{1} MOSFET commanded to fire".format(callsign, nodeid))
            command = faraday_cmd.CommandLocalHABActivateCutdownEvent()

        if request.form["IO"] == "HABTIMERRESET":
            logger.debug("Local {0}-{1} HAB timer reset commanded".format(callsign, nodeid))
            command = faraday_cmd.CommandLocalHABResetAutoCutdownTimer()

        if request.form["IO"] == "HABDISABLETIMER":
            logger.debug("Local {0}-{1} HAB timer disable commanded".format(callsign, nodeid))
            command = faraday_cmd.CommandLocalHABDisableAutoCutdownTimer()

        if request.form["IO"] == "HABTIMERIDLE":
            logger.debug("Local {0}-{1} HAB timer idle commanded".format(callsign, nodeid))
            command = faraday_cmd.CommandLocalHABResetCutdownIdle()

        # Obtain remote station from config file, check form data for intended command
        remotecallsign = simpleuiConfig.get("SIMPLEUI", "REMOTECALLSIGN").upper()
        remotenodeid = simpleuiConfig.getint("SIMPLEUI", "REMOTENODEID")

        if request.form["IO"] == "LED1R ON":
            logger.debug("Remote {0}-{1} LED1 commanded ON".format(remotecallsign, remotenodeid))
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIOLED1On(remotecallsign, remotenodeid))

        if request.form["IO"] == "LED1R OFF":
            logger.debug("Remote {0}-{1} LED1 commanded OFF".format(remotecallsign, remotenodeid))
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIOLED1Off(remotecallsign, remotenodeid))

        # Below here does not work
        if request.form["IO"] == "LED2R ON":
            logger.debug("Remote {0}-{1} LED2 commanded ON".format(remotecallsign, remotenodeid))
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIOLED2On(remotecallsign, remotenodeid))

        if request.form["IO"] == "LED2R OFF":
            logger.debug("Remote {0}-{1} LED2 commanded OFF".format(remotecallsign, remotenodeid))
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIOLED2Off(remotecallsign, remotenodeid))

        if request.form["IO"] == "GPIO0R ON":
            logger.debug("Remote {0}-{1} GPIO0 commanded ON".format(remotecallsign, remotenodeid))
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                gpioallocations.DIGITAL_IO_0,
                                                                                0, 0, 0, 0, 0))

        if request.form["IO"] == "GPIO0R OFF":
            logger.debug("Remote {0}-{1} GPIO0 commanded OFF".format(remotecallsign, remotenodeid))
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                0, 0, 0, gpioallocations.DIGITAL_IO_0,
                                                                                0, 0))
        if request.form["IO"] == "GPIO1R ON":
            logger.debug("Remote {0}-{1} GPIO1 commanded ON".format(remotecallsign, remotenodeid))
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                gpioallocations.DIGITAL_IO_1,
                                                                                0, 0, 0, 0, 0))
        if request.form["IO"] == "GPIO1R OFF":
            logger.debug("Remote {0}-{1} GPIO1 commanded OFF".format(remotecallsign, remotenodeid))
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                0, 0, 0, gpioallocations.DIGITAL_IO_1,
                                                                                0, 0))
        if request.form["IO"] == "GPIO2R ON":
            logger.debug("Remote {0}-{1} GPIO2 commanded ON".format(remotecallsign, remotenodeid))
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                gpioallocations.DIGITAL_IO_2,
                                                                                0, 0, 0, 0, 0))

        if request.form["IO"] == "GPIO2R OFF":
            logger.debug("Remote {0}-{1} GPIO2 commanded OFF".format(remotecallsign, remotenodeid))
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                0, 0, 0, gpioallocations.DIGITAL_IO_2,
                                                                                0, 0))
        if request.form["IO"] == "GPIO3R ON":
            logger.debug("Remote {0}-{1} GPIO3 commanded ON".format(remotecallsign, remotenodeid))
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                0,
                                                                                gpioallocations.DIGITAL_IO_3,
                                                                                0, 0, 0, 0))
        if request.form["IO"] == "GPIO3R OFF":
            logger.debug("Remote {0}-{1} GPIO3 commanded OFF".format(remotecallsign, remotenodeid))
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                0, 0, 0, 0,
                                                                                gpioallocations.DIGITAL_IO_3, 0))

        if request.form["IO"] == "GPIO4R ON":
            logger.debug("Remote {0}-{1} GPIO4 commanded ON".format(remotecallsign, remotenodeid))
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                0, 0, 0, 0,
                                                                                gpioallocations.DIGITAL_IO_4, 0))

        if request.form["IO"] == "GPIO4R OFF":
            logger.debug("Remote {0}-{1} GPIO4 commanded OFF".format(remotecallsign, remotenodeid))
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                0, 0, 0, 0,
                                                                                gpioallocations.DIGITAL_IO_4, 0))

        if request.form["IO"] == "GPIO5R ON":
            logger.debug("Remote {0}-{1} GPIO5 commanded ON".format(remotecallsign, remotenodeid))
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                0, 0, 0, 0,
                                                                                gpioallocations.DIGITAL_IO_5, 0))

        if request.form["IO"] == "GPIO5R OFF":
            logger.debug("Remote {0}-{1} GPIO5 commanded OFF".format(remotecallsign, remotenodeid))
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                0, 0, 0, 0,
                                                                                gpioallocations.DIGITAL_IO_5, 0))

        if request.form["IO"] == "GPIO6R ON":
            logger.debug("Remote {0}-{1} GPIO6 commanded ON".format(remotecallsign, remotenodeid))
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                0, 0, 0, 0,
                                                                                gpioallocations.DIGITAL_IO_6, 0))

        if request.form["IO"] == "GPIO6R OFF":
            logger.debug("Remote {0}-{1} GPIO6 commanded OFF".format(remotecallsign, remotenodeid))
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                0, 0, 0, 0,
                                                                                gpioallocations.DIGITAL_IO_6, 0))

        if request.form["IO"] == "GPIO7R ON":
            logger.debug("Remote {0}-{1} GPIO7 commanded ON".format(remotecallsign, remotenodeid))
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                0, 0, 0, 0,
                                                                                gpioallocations.DIGITAL_IO_7, 0))

        if request.form["IO"] == "GPIO7R OFF":
            logger.debug("Remote {0}-{1} GPIO7 commanded OFF".format(remotecallsign, remotenodeid))
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                0, 0, 0, 0,
                                                                                gpioallocations.DIGITAL_IO_7, 0))

        if request.form["IO"] == "GPIO8R ON":
            logger.debug("Remote {0}-{1} GPIO8 commanded ON".format(remotecallsign, remotenodeid))
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                0, 0, 0, 0,
                                                                                0, gpioallocations.DIGITAL_IO_8))

        if request.form["IO"] == "GPIO8R OFF":
            logger.debug("Remote {0}-{1} GPIO8 commanded OFF".format(remotecallsign, remotenodeid))
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                0, 0, 0, 0,
                                                                                0, gpioallocations.DIGITAL_IO_8))

        if request.form["IO"] == "MOSFETR":
            logger.debug("Remote {0}-{1} MOSFET commanded to fire".format(remotecallsign, remotenodeid))
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteHABActivateCutdownEvent(remotecallsign,
                                                                                                   remotenodeid))

        if request.form["IO"] == "HABTIMERRESETR":
            logger.debug("Remote {0}-{1} HAB timer commanded to reset".format(remotecallsign, remotenodeid))
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteHABResetAutoCutdownTimer(remotecallsign,
                                                                                                    remotenodeid))

        if request.form["IO"] == "HABDISABLETIMERR":
            logger.debug("Remote {0}-{1} HAB timer disable commanded".format(remotecallsign, remotenodeid))
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteHABDisableAutoCutdownTimer(remotecallsign,
                                                                                                      remotenodeid))

        if request.form["IO"] == "HABTIMERIDLER":
            logger.debug("Remote {0}-{1} HAB timer idle commanded".format(remotecallsign, remotenodeid))
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteHABResetCutdownIdle(remotecallsign,
                                                                                               remotenodeid))

        # Send POST command for remote station control
        faraday_1.POST(callsign, nodeid, faraday_1.CMD_UART_PORT, command)

        # Return to simple user interface page after commanding
        return redirect("http://localhost/", code=302)


@app.errorhandler(404)
def pageNotFound(error):
    """HTTP 404 response for incorrect URL"""
    logger.error("Error: " + str(error))
    return json.dumps({"error": "HTTP " + str(error)}), 404


def main():
    """Main function which starts the Flask server."""
    logger.info('Starting Simple User Interface')

    # Start the flask server on localhost:8000
    uihost = simpleuiConfig.get("FLASK", "host")
    uiport = simpleuiConfig.getint("FLASK", "port")

    app.run(host=uihost, port=uiport, threaded=True)


if __name__ == '__main__':
    main()

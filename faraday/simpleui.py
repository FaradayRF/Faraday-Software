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

from flask import Flask
from flask import request
from flask import render_template
from flask import redirect

# Imports - Faraday Specific
from faraday.proxyio import faradaybasicproxyio
from faraday.proxyio import faradaycommands
from faraday.proxyio import gpioallocations

# Start logging after importing modules
filename = os.path.join(os.path.dirname(__file__), '..', 'Applications', 'SimpleUI', 'loggingConfig.ini')
filename = os.path.abspath(filename)
logging.config.fileConfig(filename)
logger = logging.getLogger('SimpleUI')

# Load configuration file
simpleuiconfig = ConfigParser.RawConfigParser()
filename = os.path.join(os.path.dirname(__file__), '..', 'Applications', 'SimpleUI', 'simpleui.ini')
simpleuiconfig.read(filename)

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
        callsign = simpleuiconfig.get("SIMPLEUI", "CALLSIGN").upper()
        nodeid = simpleuiconfig.getint("SIMPLEUI", "NODEID")

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
        callsign = simpleuiconfig.get("SIMPLEUI", "LOCALCALLSIGN").upper()
        nodeid = simpleuiconfig.getint("SIMPLEUI", "LOCALNODEID")

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
        remotecallsign = simpleuiconfig.get("SIMPLEUI", "REMOTECALLSIGN").upper()
        remotenodeid = simpleuiconfig.getint("SIMPLEUI", "REMOTENODEID")

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
    uihost = simpleuiconfig.get("FLASK", "host")
    uiport = simpleuiconfig.getint("FLASK", "port")

    app.run(host=uihost, port=uiport, threaded=True)


if __name__ == '__main__':
    main()

# /SimpleUI/simpleui.py
# License: GPLv3 with Network Interface Clause

"""
SimpleUI provides a no frills method of interfacing Faraday telemetry with a webpage in a formatted manner. This is
different than the Telemetry application since it renders the data in an automatically updating manner using Javascript.
"""

import json
import logging.config
import ConfigParser
import os
import sys

from flask import Flask
from flask import request
from flask import render_template
from flask import redirect
from flask_bootstrap import Bootstrap

# Add Faraday library to the Python path.
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

# Imports - Faraday Specific
from faraday.proxyio import faradaybasicproxyio
from faraday.proxyio import faradaycommands
from faraday.proxyio import gpioallocations

# Start logging after importing modules
filename = os.path.abspath("loggingConfig.ini")
logging.config.fileConfig(filename)
logger = logging.getLogger('SimpleUI')

# Load configuration file
simpleuiconfig = ConfigParser.RawConfigParser()
filename = os.path.abspath("simpleui.ini")
simpleuiconfig.read(filename)

# Initialize Flask microframework
app = Flask(__name__)
Bootstrap(app)


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
            print "LED1 ON"
            command = faraday_cmd.CommandLocalGPIOLED1On()

        if request.form["IO"] == "LED1 OFF":
            print "LED1 OFF"
            command = faraday_cmd.CommandLocalGPIOLED1Off()

        if request.form["IO"] == "LED2 ON":
            print "LED2 ON"
            command = faraday_cmd.CommandLocalGPIOLED2On()

        if request.form["IO"] == "LED2 OFF":
            print "LED2 OFF"
            command = faraday_cmd.CommandLocalGPIOLED2Off()

        if request.form["IO"] == "GPIO0 ON":
            print "GPIO0 ON"
            command = faraday_cmd.CommandLocalGPIO(gpioallocations.DIGITAL_IO_0, 0, 0, 0, 0, 0)

        if request.form["IO"] == "GPIO0 OFF":
            print "GPIO0 OFF"
            command = faraday_cmd.CommandLocalGPIO(0, 0, 0, gpioallocations.DIGITAL_IO_0, 0, 0)

        if request.form["IO"] == "GPIO1 ON":
            print "GPIO1 ON"
            command = faraday_cmd.CommandLocalGPIO(gpioallocations.DIGITAL_IO_1, 0, 0, 0, 0, 0)

        if request.form["IO"] == "GPIO1 OFF":
            print "GPIO1 OFF"
            command = faraday_cmd.CommandLocalGPIO(0, 0, 0, gpioallocations.DIGITAL_IO_1, 0, 0)

        if request.form["IO"] == "GPIO2 ON":
            print "GPIO2 ON"
            command = faraday_cmd.CommandLocalGPIO(gpioallocations.DIGITAL_IO_2, 0, 0, 0, 0, 0)

        if request.form["IO"] == "GPIO2 OFF":
            print "GPIO2 OFF"
            command = faraday_cmd.CommandLocalGPIO(0, 0, 0, gpioallocations.DIGITAL_IO_2, 0, 0)

        if request.form["IO"] == "GPIO3 ON":
            print "GPIO3 ON"
            command = faraday_cmd.CommandLocalGPIO(0, gpioallocations.DIGITAL_IO_3, 0, 0, 0, 0)

        if request.form["IO"] == "GPIO3 OFF":
            print "GPIO3 OFF"
            command = faraday_cmd.CommandLocalGPIO(0, 0, 0, 0, gpioallocations.DIGITAL_IO_3, 0)

        if request.form["IO"] == "GPIO4 ON":
            print "GPIO4 ON"
            command = faraday_cmd.CommandLocalGPIO(0, gpioallocations.DIGITAL_IO_4, 0, 0, 0, 0)

        if request.form["IO"] == "GPIO4 OFF":
            print "GPIO4 OFF"
            command = faraday_cmd.CommandLocalGPIO(0, 0, 0, 0, gpioallocations.DIGITAL_IO_4, 0)

        if request.form["IO"] == "GPIO5 ON":
            print "GPIO5 ON"
            command = faraday_cmd.CommandLocalGPIO(0, gpioallocations.DIGITAL_IO_5, 0, 0, 0, 0)

        if request.form["IO"] == "GPIO5 OFF":
            print "GPIO5 OFF"
            command = faraday_cmd.CommandLocalGPIO(0, 0, 0, 0, gpioallocations.DIGITAL_IO_5, 0)

        if request.form["IO"] == "GPIO6 ON":
            print "GPIO6 ON"
            command = faraday_cmd.CommandLocalGPIO(0, gpioallocations.DIGITAL_IO_6, 0, 0, 0, 0)

        if request.form["IO"] == "GPIO6 OFF":
            print "GPIO6 OFF"
            command = faraday_cmd.CommandLocalGPIO(0, 0, 0, 0, gpioallocations.DIGITAL_IO_6, 0)

        if request.form["IO"] == "GPIO7 ON":
            print "GPIO7 ON"
            command = faraday_cmd.CommandLocalGPIO(0, gpioallocations.DIGITAL_IO_7, 0, 0, 0, 0)

        if request.form["IO"] == "GPIO7 OFF":
            print "GPIO7 OFF"
            command = faraday_cmd.CommandLocalGPIO(0, 0, 0, 0, gpioallocations.DIGITAL_IO_7, 0)

        if request.form["IO"] == "GPIO8 ON":
            print "GPIO8 ON"
            command = faraday_cmd.CommandLocalGPIO(0, 0, gpioallocations.DIGITAL_IO_8, 0, 0, 0)

        if request.form["IO"] == "GPIO8 OFF":
            print "GPIO8 OFF"
            command = faraday_cmd.CommandLocalGPIO(0, 0, 0, 0, 0, gpioallocations.DIGITAL_IO_8)

        if request.form["IO"] == "MOSFET":
            print "MOSFET ON"
            command = faraday_cmd.CommandLocalHABActivateCutdownEvent()

        if request.form["IO"] == "HABTIMERRESET":
            print "HAB TIMER RESET"
            command = faraday_cmd.CommandLocalHABResetAutoCutdownTimer()

        if request.form["IO"] == "HABDISABLETIMER":
            print "HAB DISABABLE TIMER"
            command = faraday_cmd.CommandLocalHABDisableAutoCutdownTimer()

        if request.form["IO"] == "HABTIMERIDLE":
            print "HAB IDLE TIMER"
            command = faraday_cmd.CommandLocalHABResetCutdownIdle()

        # Obtain remote station from config file, check form data for intended command
        remotecallsign = simpleuiconfig.get("SIMPLEUI", "REMOTECALLSIGN").upper()
        remotenodeid = simpleuiconfig.getint("SIMPLEUI", "REMOTENODEID")

        if request.form["IO"] == "LED1R ON":
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIOLED1On(remotecallsign, remotenodeid))

        if request.form["IO"] == "LED1R OFF":
            print "LED1R OFF"
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIOLED1Off(remotecallsign, remotenodeid))

        # Below here does not work
        if request.form["IO"] == "LED2R ON":
            print "LED2 ON"
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIOLED2On(remotecallsign, remotenodeid))

        if request.form["IO"] == "LED2R OFF":
            print "LED2 OFF"
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIOLED2Off(remotecallsign, remotenodeid))

        if request.form["IO"] == "GPIO0R ON":
            print "GPIO0 ON"
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                gpioallocations.DIGITAL_IO_0,
                                                                                0, 0, 0, 0, 0))
        if request.form["IO"] == "GPIO0R OFF":
            print "GPIO0 OFF"
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                0, 0, 0, gpioallocations.DIGITAL_IO_0,
                                                                                0, 0))
        if request.form["IO"] == "GPIO1R ON":
            print "GPIO1 ON"
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                gpioallocations.DIGITAL_IO_1,
                                                                                0, 0, 0, 0, 0))
        if request.form["IO"] == "GPIO1R OFF":
            print "GPIO1 OFF"
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                0, 0, 0, gpioallocations.DIGITAL_IO_1,
                                                                                0, 0))
        if request.form["IO"] == "GPIO2R ON":
            print "GPIO2 ON"
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                gpioallocations.DIGITAL_IO_2,
                                                                                0, 0, 0, 0, 0))

        if request.form["IO"] == "GPIO2R OFF":
            print "GPIO2 OFF"
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                0, 0, 0, gpioallocations.DIGITAL_IO_2,
                                                                                0, 0))
        if request.form["IO"] == "GPIO3R ON":
            print "GPIO3 ON"
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                0,
                                                                                gpioallocations.DIGITAL_IO_3,
                                                                                0, 0, 0, 0))
        if request.form["IO"] == "GPIO3R OFF":
            print "GPIO3 OFF"
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                0, 0, 0, 0,
                                                                                gpioallocations.DIGITAL_IO_3, 0))

        if request.form["IO"] == "GPIO4R ON":
            print "GPIO4 ON"
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                0, 0, 0, 0,
                                                                                gpioallocations.DIGITAL_IO_4, 0))

        if request.form["IO"] == "GPIO4R OFF":
            print "GPIO4 OFF"
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                0, 0, 0, 0,
                                                                                gpioallocations.DIGITAL_IO_4, 0))

        if request.form["IO"] == "GPIO5R ON":
            print "GPIO5 ON"
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                0, 0, 0, 0,
                                                                                gpioallocations.DIGITAL_IO_5, 0))

        if request.form["IO"] == "GPIO5R OFF":
            print "GPIO5 OFF"
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                0, 0, 0, 0,
                                                                                gpioallocations.DIGITAL_IO_5, 0))

        if request.form["IO"] == "GPIO6R ON":
            print "GPIO6 ON"
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                0, 0, 0, 0,
                                                                                gpioallocations.DIGITAL_IO_6, 0))

        if request.form["IO"] == "GPIO6R OFF":
            print "GPIO6 OFF"
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                0, 0, 0, 0,
                                                                                gpioallocations.DIGITAL_IO_6, 0))

        if request.form["IO"] == "GPIO7R ON":
            print "GPIO7 ON"
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                0, 0, 0, 0,
                                                                                gpioallocations.DIGITAL_IO_7, 0))

        if request.form["IO"] == "GPIO7R OFF":
            print "GPIO7 OFF"
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                0, 0, 0, 0,
                                                                                gpioallocations.DIGITAL_IO_7, 0))

        if request.form["IO"] == "GPIO8R ON":
            print "GPIO8 ON"
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                0, 0, 0, 0,
                                                                                0, gpioallocations.DIGITAL_IO_8))

        if request.form["IO"] == "GPIO8R OFF":
            print "GPIO8 OFF"
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIO(remotecallsign,
                                                                                remotenodeid,
                                                                                0, 0, 0, 0,
                                                                                0, gpioallocations.DIGITAL_IO_8))

        if request.form["IO"] == "MOSFETR":
            print "MOSFET ON"
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteHABActivateCutdownEvent(remotecallsign,
                                                                                                    remotenodeid))

        if request.form["IO"] == "HABTIMERRESETR":
            print "HABTIMERRESETR"
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteHABResetAutoCutdownTimer(remotecallsign,
                                                                                                   remotenodeid))

        if request.form["IO"] == "HABDISABLETIMERR":
            print "HABDISABLETIMERR"
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteHABDisableAutoCutdownTimer(remotecallsign,
                                                                                                    remotenodeid))

        if request.form["IO"] == "HABTIMERIDLER":
            print "HABTIMERIDLER"
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

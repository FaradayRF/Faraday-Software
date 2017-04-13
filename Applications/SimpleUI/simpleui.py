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

sys.path.append(os.path.join(os.path.dirname(__file__),
                             "../../Faraday_Proxy_Tools"))  # Append path to common tutorial FaradayIO module

# Imports - Faraday Specific
from FaradayIO import faradaybasicproxyio
from FaradayIO import faradaycommands
from FaradayIO import gpioallocations



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
    Provides a simple user interface
    """
    if request.method == "GET":
        callsign = request.args.get('callsign', '').upper()
        nodeid = request.args.get('nodeid', '')

        if callsign and nodeid:
            # This is the GET routine to return data to the user
            return render_template('index.html',
                                   callsign=callsign,
                                   nodeid=nodeid)
        else:
            return "Please provide a callsign and nodeid in URL i.e. <br />localhost/?callsign=nocall&nodeid=1"
    if request.method == "POST":
        # Start the proxy server after configuring the configuration file correctly
        # Setup a Faraday IO object
        faraday_1 = faradaybasicproxyio.proxyio()  # default proxy port
        faraday_cmd = faradaycommands.faraday_commands()

        callsign = request.form["CALLSIGN"]
        nodeid = request.form["NODEID"]

        # CommandLocalGPIO(self, p3_bitmask_on, p4_bitmask_on, p5_bitmask_on, p3_bitmask_off, p4_bitmask_off, p5_bitmask_off):

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

        remotecallsign = "KB1LQC"
        remotenodeid = 1

        #Trying to get to work
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
            command = faraday_cmd.CommandLocal(9, faraday_cmd.CommandRemoteGPIOLED2Off(remotecallsign,remotenodeid))

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
            command = faraday_cmd.CommandRemoteHABActivateCutdownEvent(remotecallsign, remotenodeid)



        faraday_1.POST(callsign, int(nodeid), faraday_1.CMD_UART_PORT, command)

        logger.info(request.form)



        return redirect("http://localhost/?callsign={0}&nodeid={1}".format(callsign,nodeid), code=302)

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

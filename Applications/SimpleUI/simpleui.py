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

from flask import Flask
from flask import request
from flask import render_template
from flask import redirect
from flask_bootstrap import Bootstrap


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
        logger.info(request.form)
        callsign = request.form["CALLSIGN"]
        nodeid = request.form["NODEID"]
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

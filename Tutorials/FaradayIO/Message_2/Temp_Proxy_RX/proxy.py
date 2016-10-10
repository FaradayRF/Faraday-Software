#-------------------------------------------------------------------------------
# Name:        Proxy.py
# Purpose:
#
# Author:      Bryce

#
# Created:     03/04/2016
# Copyright:   (c) Bryce 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sys
# add relative paths for import to find Faraday modules
#sys.path.insert(0,'FaradayRFUART')
sys.path.insert(0,'FaradayRFclasses')
#sys.path.insert(0,'Command_Module')
#import Simple_Transport_Services
#import Simple_Transport_Protocol

from faraday_uart_stack import layer_4_service

import faraday
#import command
import threading
from collections import deque
import logging
import logging.config
import time
from flask import Flask, request, render_template, redirect
from flask_bootstrap import Bootstrap
import json
import base64
import requests
from ConfigParser import SafeConfigParser
from werkzeug.serving import WSGIRequestHandler
from Command_Module import Command_Module
from Command_Module import general_command as general_command
from Command_Module import gpio_allocation
import sqlite3
import os
import copy
import Telemetry
from flask_sqlalchemy import SQLAlchemy
from flask import json,jsonify
from marshmallow import Schema, fields
import aprs
import database



#temp
telemport = 5

#Setup local faraday instance
faradayUnit = faraday.faraday()
faradayAP = faraday.faraday()

# Enable Logging
with open('logging.json') as f:
    configfile = json.load(f)
    logging.config.dictConfig(configfile)
#logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("proxy")

#set log level for Flask to ERROR
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


#setup proxy from configuration file
parser = SafeConfigParser()
parser.read('faraday.ini')

comport = parser.get('proxy','com')
baudrate = parser.getint('proxy','baudrate')
timeout = parser.getint('proxy','timeout')
port = str(parser.getint('proxy','port'))
telemetry_autoretrieve = parser.getboolean('telemetry', 'autoretrieve') #Telemetry application auto-retrieve. Default=True, to disable telemetry retrieve if you wish to retrieve packet from telemetry port manual (learning...) the change to False

logging.info('PORT: %s, BAUDRATE: %d, TIMEOUT: %d' % (comport,baudrate,timeout))

db_filename = 'data/faraday.db'
#Open SQLite database, create one if not, timestamp ISO 8601 format
timestamp = time.strftime("%Y-%m-%dT%H%M%S")
#db_filename = 'data/telemetry_' + timestamp + '.db'
db_filename = 'data/faraday.db'
#print "Creating database file " + db_filename + "\n"
schema_filename = 'telemetryschema.sql'


#Create database table
if(os.path.isfile(db_filename)) == True:
    print "File found!"
    conn = sqlite3.connect(db_filename)
    c = conn.cursor()

else:
    with open(schema_filename, 'rt') as f:
        schema = f.read()
    try:
        conn = sqlite3.connect(db_filename)
        conn.executescript(schema)
        c = conn.cursor()
    except StandardError as e:
        print e


#make one global dictionaries
queDict = {}
queDict2 = []
portDict = {}
postDict = {}

#Create threaded worker definition for RX
def uart_worker(modem,que):
    logging.info('Starting UART worker thread...')

    #start an infinit loop
    while(1):
        # Place data into the FIFO coming from UART for GET function
        try:
            for port in range(0,255):
                if(modem.RxPortHasItem(port)):
                    #data is waiting from UART, encode BASE64 and place in qeue
                    item = {}
                    item["port"] = port
                    item["data"] = \
                    base64.b64encode(modem.GET(port))
                    #print item
                    try:
                        que[port].append(item)
                    except:
                        # Qeue does not exist for port, create one
                        que[port] = deque([], maxlen=100)
                        que[port].append(item)
        except:
            print "FaradayRF Modem not detected on UART"
        time.sleep(0.01)
        # Check for data in the POST FIFO to send to UART
        try:
            for port in range(0,255):
                try:
                    postDict[port]
                except:
                    pass
                else:
                    for num in range(len(postDict[port])):
                        #Data is present in qeue, decode BASE64, send to UART
                        message = postDict[port].popleft()
                        message = base64.b64decode(message)
                        modem.POST(port, len(message), message)
        except:
            pass
        time.sleep(0.01)

#start flask
app = Flask(__name__)

#Setup database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_filename
db = SQLAlchemy(app)

#database.addDatabaseSchemas(Schema);
# Configure marchmallow schema
class DataSchema(Schema):
    keyid = fields.Int()
    aprf = fields.Int()
    apcallsign = fields.Str()
    apid = fields.Int()
    callsign = fields.Str()
    id = fields.Int()
    rtcsec = fields.Int()
    rtcmin = fields.Int()
    rtchour = fields.Int()
    rtcday = fields.Int()
    rtcdow = fields.Int()
    rtcmon = fields.Int()
    rtcyear = fields.Int()
    apgpsfix = fields.Int()
    aplatdeg = fields.Int()
    aplatdec = fields.Float()
    aplatdir = fields.Str()
    aplondeg = fields.Int()
    aplondec = fields.Float()
    aplondir = fields.Str()
    apaltitude = fields.Float()
    apaltunits = fields.Str()
    apspeed = fields.Float()
    aphdop = fields.Float()
    gpsfix = fields.Int()
    latdeg = fields.Int()
    latdec = fields.Float()
    latdir = fields.Str()
    londeg = fields.Int()
    londec = fields.Float()
    londir = fields.Str()
    altitude = fields.Float()
    altunits = fields.Str()
    speed = fields.Float()
    hdop = fields.Float()
    gpio0 = fields.Int()
    gpio1 = fields.Int()
    gpio2 = fields.Int()
    adc0 = fields.Int()
    adc1 = fields.Int()
    adc2 = fields.Int()
    adc3 = fields.Int()
    adc4 = fields.Int()
    adc5 = fields.Int()
    adc6 = fields.Int()
    adc7 = fields.Int()
    adc8 = fields.Int()
    apepoch = fields.Int()
    crc = fields.Int()
    packettype = fields.Int()
    destcallsign = fields.Str()
    destid = fields.Int()
    faradayport = fields.Int()
    uChar_auto_cutdown_timer_state_status = fields.Int()
    uChar_cutdown_event_state_status = fields.Int()
    uInt_timer_set = fields.Int()
    uInt_timer_current = fields.Int()

data_schema = DataSchema(many=True)

# Configure marchmallow schema
class scalingSchema(Schema):
    keyid = fields.Int()
    keyname = fields.Str()
    callsign = fields.Str()
    id = fields.Int()
    adc0m = fields.Float(default=3)
    adc0b = fields.Float()
    adc1m = fields.Float()
    adc1b = fields.Float()
    adc2m = fields.Float()
    adc2b = fields.Float()
    adc3m = fields.Float()
    adc3b = fields.Float()
    adc4m = fields.Float()
    adc4b = fields.Float()
    adc5m = fields.Float()
    adc5b = fields.Float()
    adc6m = fields.Float()
    adc6b = fields.Float()
    adc7m = fields.Float()
    adc7b = fields.Float()
    adc8m = fields.Float()

    adc8b = fields.Float()
    tempcal = fields.Float()

scaling_schema = scalingSchema(many=True)

# Configure marchmallow schema
class scaledTelemetry(Schema):
    keyid = fields.Int()
    callsign = fields.Str()
    id = fields.Int()
    adc0scaled = fields.Float()
    adc1scaled = fields.Float()
    adc2scaled = fields.Float()
    adc3scaled = fields.Float()
    adc4scaled = fields.Float()
    adc5scaled = fields.Float()
    adc6scaled = fields.Float()
    adc7scaled = fields.Float()
    adc8scaled = fields.Float()
    paenable = fields.Int()
    lnaenable = fields.Int()
    hgmselect = fields.Int()
    mosfet = fields.Int()
    led1 = fields.Int()
    led2 = fields.Int()
    gpsreset = fields.Int()
    gpsstandby = fields.Int()
    button = fields.Int()
    gpio0 = fields.Int()
    gpio1 = fields.Int()
    gpio2 = fields.Int()
    gpio3 = fields.Int()
    gpio4 = fields.Int()
    gpio5 = fields.Int()
    gpio6 = fields.Int()
    gpio7 = fields.Int()
    gpio8 = fields.Int()
    gpio9 = fields.Int()

scaledtelemetry_schema = scaledTelemetry(many=True)

class faradaytelemetry(db.Model):
    __tablename__ = 'telemetry'
    keyid = db.Column(db.Integer, primary_key=True)
    faradayport = db.Column(db.Integer)
    packettype = db.Column(db.Integer)
    aprf = db.Column(db.Integer)
    apcallsign = db.Column(db.String(9))
    apid = db.Column(db.Integer)
    callsign = db.Column(db.String(9))
    id = db.Column(db.Integer)
    rtcsec = db.Column(db.Integer)
    rtcmin = db.Column(db.Integer)
    rtchour = db.Column(db.Integer)
    rtcday = db.Column(db.Integer)
    rtcdow = db.Column(db.Integer)
    rtcmon = db.Column(db.Integer)
    rtcyear = db.Column(db.Integer)
    apgpsfix = db.Column(db.Integer)
    aplatdeg = db.Column(db.Integer)
    aplatdec = db.Column(db.Float)
    aplatdir = db.Column(db.String(1))
    aplondeg = db.Column(db.Integer)
    aplondec = db.Column(db.Float)
    aplondir = db.Column(db.String(1))
    apaltitude = db.Column(db.Integer)
    apaltunits = db.Column(db.Float)
    apspeed = db.Column(db.Float)
    aphdop = db.Column(db.Float)
    gpsfix = db.Column(db.Integer)
    latdeg = db.Column(db.Integer)
    latdec = db.Column(db.Float)
    latdir = db.Column(db.String(1))
    londeg = db.Column(db.Integer)
    londec = db.Column(db.Float)
    londir = db.Column(db.String(1))
    altitude = db.Column(db.Integer)
    altunits = db.Column(db.Float)
    speed = db.Column(db.Float)
    hdop = db.Column(db.Float)
    gpio0 = db.Column(db.Integer)
    gpio1 = db.Column(db.Integer)
    gpio2 = db.Column(db.Integer)
    adc0 = db.Column(db.Integer)
    adc1 = db.Column(db.Integer)
    adc2 = db.Column(db.Integer)
    adc3 = db.Column(db.Integer)
    adc4 = db.Column(db.Integer)
    adc5 = db.Column(db.Integer)
    adc6 = db.Column(db.Integer)
    adc7 = db.Column(db.Integer)
    adc8 = db.Column(db.Integer)
    apepoch = db.Column(db.Integer)
    crc = db.Column(db.Integer)
    destid = db.Column(db.Integer)
    destcallsign = db.Column(db.String(9))
    uChar_auto_cutdown_timer_state_status = db.Column(db.Integer)
    uChar_cutdown_event_state_status = db.Column(db.Integer)
    uInt_timer_set = db.Column(db.Integer)
    uInt_timer_current = db.Column(db.Integer)

class faradayscaling(db.Model):
    __tablename__ = 'faradayio'
    keyid = db.Column(db.Integer, primary_key=True)
    keyname = db.Column(db.String(25))
    callsign = db.Column(db.String(9))
    id = db.Column(db.Integer)
    adc0m = db.Column(db.Float)
    adc0b = db.Column(db.Float)
    adc1m = db.Column(db.Float)
    adc1b = db.Column(db.Float)
    adc2m = db.Column(db.Float)
    adc2b = db.Column(db.Float)
    adc3m = db.Column(db.Float)
    adc3b = db.Column(db.Float)
    adc4m = db.Column(db.Float)
    adc4b = db.Column(db.Float)
    adc5m = db.Column(db.Float)
    adc5b = db.Column(db.Float)
    adc6m = db.Column(db.Float)
    adc6b = db.Column(db.Float)
    adc7m = db.Column(db.Float)
    adc7b = db.Column(db.Float)
    adc8m = db.Column(db.Float)
    adc8b = db.Column(db.Float)
    tempcal = db.Column(db.Float)

class faradayScaledTelemetry(db.Model):
    __tablename__ = 'scaledtelemetry'
    keyid = db.Column(db.Integer, primary_key=True)
    callsign = db.Column(db.String(9))
    id = db.Column(db.Integer)
    adc0scaled = db.Column(db.Float)
    adc1scaled = db.Column(db.Float)
    adc2scaled = db.Column(db.Float)
    adc3scaled = db.Column(db.Float)
    adc4scaled = db.Column(db.Float)
    adc5scaled = db.Column(db.Float)
    adc6scaled = db.Column(db.Float)
    adc7scaled = db.Column(db.Float)
    adc8scaled = db.Column(db.Float)
    paenable = db.Column(db.Integer)
    lnaenable = db.Column(db.Integer)
    hgmselect = db.Column(db.Integer)
    mosfet = db.Column(db.Integer)
    led1 = db.Column(db.Integer)
    led2 = db.Column(db.Integer)
    gpsreset = db.Column(db.Integer)
    gpsstandby = db.Column(db.Integer)
    button = db.Column(db.Integer)
    gpio0 = db.Column(db.Integer)
    gpio1 = db.Column(db.Integer)
    gpio2 = db.Column(db.Integer)
    gpio3 = db.Column(db.Integer)
    gpio4 = db.Column(db.Integer)
    gpio5 = db.Column(db.Integer)
    gpio6 = db.Column(db.Integer)
    gpio7 = db.Column(db.Integer)
    gpio8 = db.Column(db.Integer)
    gpio9 = db.Column(db.Integer)

    # Configure marchmallow schema APP_HAB_Telemetry
class APP_HAB_Telemetry(Schema):
    keyid = fields.Int()
    status_bitmask = fields.Int()
    uInt_timer_set = fields.Int()
    uInt_timer_remaining = fields.Float()

APP_HAB_Telemetry_schema = APP_HAB_Telemetry(many=True)

    # Configure db.Model APP_HAB_Telemetry
class faraday_APP_HAB_Telemetry(db.Model):
    __tablename__ = 'APP_HAB_Telemetry'
    keyid = db.Column(db.Integer, primary_key=True)
    status_bitmask = db.Column(db.Integer)
    uInt_timer_set = db.Column(db.Integer)
    uInt_timer_remaining = db.Column(db.Integer)

    # Configure marchmallow schema faradayDebugTelemetry
class debugTelemetry(Schema):
    keyid = fields.Int()
    callsign = fields.Str()
    id = fields.Int()
    packettype = fields.Int()
    epoch = fields.Int()
    faradayport = fields.Int()
    aprf = fields.Int()
    bootcount = fields.Int()
    resetcount = fields.Int()
    bor = fields.Int()
    rstnmi = fields.Int()
    svsl = fields.Int()
    svsh = fields.Int()
    svmlovp = fields.Int()
    svmhovp = fields.Int()
    wdtto = fields.Int()
    flashkeyviolation = fields.Int()
    fllunlock = fields.Int()
    peripheralconfigcnt = fields.Int()
    accessviolation = fields.Int()


debugTelemetry_schema = debugTelemetry(many=True)

    # Configure db.Model faradayDebugTelemetry
class faradayDebugTelemetry(db.Model):
    __tablename__ = 'faradayDebug'
    keyid = db.Column(db.Integer, primary_key=True)
    callsign = db.Column(db.String(9))
    id = db.Column(db.Integer)
    packettype = db.Column(db.Integer)
    epoch = db.Column(db.Integer)
    faradayport = db.Column(db.Integer)
    aprf = db.Column(db.Integer)
    bootcount = db.Column(db.Integer)
    resetcount = db.Column(db.Integer)
    bor = db.Column(db.Integer)
    rstnmi = db.Column(db.Integer)
    svsl = db.Column(db.Integer)
    svsh = db.Column(db.Integer)
    svmlovp = db.Column(db.Integer)
    svmhovp = db.Column(db.Integer)
    wdtto = db.Column(db.Integer)
    flashkeyviolation = db.Column(db.Integer)
    fllunlock = db.Column(db.Integer)
    peripheralconfigcnt = db.Column(db.Integer)
    accessviolation = db.Column(db.Integer)

    # Configure marchmallow schema faradaySystemSettings
class systemSettings(Schema):
    keyid = fields.Int()
    callsign = fields.Str()
    id = fields.Int()
    packettype = fields.Int()
    epoch = fields.Int()
    faradayport = fields.Int()
    aprf = fields.Int()
    rffreq0 = fields.Int()
    rffreq1 = fields.Int()
    rffreq2 = fields.Int()
    rfpwr = fields.Int()

systemSettings_schema = systemSettings(many=True)

    # Configure db.Model faradaySystemSettings
class faradaySystemSettings(db.Model):
    __tablename__ = 'faradaySystemSettings'
    keyid = db.Column(db.Integer, primary_key=True)
    callsign = db.Column(db.String(9))
    id = db.Column(db.Integer)
    packettype = db.Column(db.Integer)
    epoch = db.Column(db.Integer)
    faradayport = db.Column(db.Integer)
    aprf = db.Column(db.Integer)
    rffreq0 = db.Column(db.Integer)
    rffreq1 = db.Column(db.Integer)
    rffreq2 = db.Column(db.Integer)
    rfpwr = db.Column(db.Integer)

## Faraday API GET
## GET(Callsign, Node ID, Service Port, Limit)
## Returns the requested data from the specified service port of Faraday in
## BASE64 directly from the UART dequeue. Sends all packets in queue unless
## specified

@app.route('/get', methods=['GET'])
def get():
    if request.method == 'GET':
        print units
        callsign = str(request.args.get("callsign"))
        nodeid = int(request.args.get("nodeid"))
        port = int(request.args.get("port"))
        limit = request.args.get("limit")
        if limit == None:
            try:
                limit = len(queDict[port])
            except KeyError as e:
                # Service port has never been used and has no data in it
                print "KeyError: ", e
                return ' ', 204

        # Make sure to do something with looking up callsign and nodeid for
        # COM port. Right now it does nothing. Will be important when using
        # two faradays on same computer via USB
##        num = int(parser.get('proxy','units'))
##        units = range(0,num)
##        for unit in units:
##            print "UNIT" + str(unit)
##
##        sections = parser.sections()
##        print sections
##        for item in sections:
##            print item

        try:
            # Check if there is a queue for the specified service port
            if (len(queDict[port]) > 0):
                queryTime = time.asctime(time.localtime(time.time())) #I SHOULD ADD TIMESTAMP TO DATA SENT
                data = []
                try:
                    while queDict[port]:
                        data.append(queDict[port].popleft())
                        if (limit == 1):
                            break;
                    return json.dumps(data, indent = 4), 200, {'Content-\
                    Type': 'application/json'}

                # StandardError encountered
                except StandardError as e:
                    print e

            else:
                # No data in service port, but port is being used
                return ' ', 204

        except KeyError as e:
            # Service port has never been used and has no data in it
            print "KeyError: ", e
            return ' ', 204

        except StandardError as e:
            print e

## Faraday API POST
## POST(Callsign, Node ID, Service Port, Data[])
## Receives data from the user and sends it to the specified service port of
## Faraday in BASE64. Should be no queue

@app.route('/post', methods=['POST'])
def post():
        callsign = str(request.args.get("callsign"))
        nodeid = int(request.args.get("nodeid"))
        port = int(request.args.get("port"))
        data = request.get_json(force=False)

        #Find COM Port
        for station in units:
            #print units
            if units[station][0] == callsign and int(units[station][1]) == nodeid:
                com = units[station][2] #do something with this

        for item in data['data']:
            try:
                postDict[port].append(str(item))
            except:
                postDict[port] = deque([], maxlen=100)
                postDict[port].append(str(item))

        try:
            if(len(data)>0):
                return ' ', 200

            else:
                return ' ', 204

        except KeyError as e:
            # Service port has never been used and has no data in it
            print "KeyError: ", e
            return ' ', 204

        except StandardError as e:
            print e

@app.route('/faraday/<int:port>', methods=['GET', 'POST'])
def data(port):
    if request.method == 'GET':
        limit = request.args.get("limit")
        #logger.info("GET request for port %d started..." % port)
        try:
            if (len(queDict[port]) > 0):
                queryTime = time.asctime(time.localtime(time.time()))
                #print "Sending %d items for port %d: %s" % \
                #(len(queDict[port]), port, queryTime)
                data = []
                try:
                    while queDict[port]:
                        data.append(queDict[port].popleft())
                        if (limit == '1'):
                            break;
                    return json.dumps(data, indent = 4), 200, {'Content-\
                Type': 'application/json'}

                except TypeError as e:
                    logger.error("TypeError for queDict...", exc_info=True)

                except ValueError as e:
                    logger.error("ValueError for queDict...",
                    exc_info=True)

                except StandardError as e:
                    #pass
                    logger.error("StandardError for queDict...",
                    exc_info=True)
            else:
                return ' ', 204
        except:
            logger.warning("HTTP 404: Application port %d not found" % port)
            return "HTTP 404: Application port %d not found" % port, 404

    elif request.method == 'POST':
        #logger.info("POST request for port %d started..." % port)
        b64cmd = request.args.get('cmd')
        cmd = base64.b64decode(b64cmd)
        #print "Command on port %d: %s" % (port,repr(cmd))

        try:
            uartDevice.transmit_service_payload(int(port), len(cmd), cmd)
        except StandardError as e:
            logger.error("StandardError for uartDevice.transmit_service_\
            payload encountered...", exc_info=True)
            return ' ', 500
        else:
            return ' ', 200

@app.route('/faraday/ports', methods=['GET'])
def return_ports():
    if request.method == 'GET':
        #print "Sending application port information\r"
        portDict = {}
        for i in range(0,255):
            try:
                if(queDict[i]):
                    portitem = {'port': i}
                    portDict[i] = portitem
            except ValueError:
                logger.error("ValueError for port queDict encountered...",
                exc_info=True)
            except TypeError:
                logger.error("TypeError for port queDict encountered...",
                exc_info=True)
            except StandardError:
                pass
                #logger.error("StandardError for port queDict encountered...",
                #exc_info=True)

        if len(portDict) > 0:
            return json.dumps(portDict, indent = 4, sort_keys = True), 200

        else:
            logger.warning("HTTP 204: Application ports not found")
            return "HTTP 204: Application ports not found", 204

@app.route('/faraday/stations', methods=['GET'])
def stations():
    if request.method == 'GET':
        epochStamp = time.time() - 15*60
        results = faradaytelemetry.query.distinct(faradaytelemetry.callsign,faradaytelemetry.id).filter(faradaytelemetry.apepoch >= epochStamp).with_entities(faradaytelemetry.callsign,faradaytelemetry.id).all()
        results = data_schema.dump(results)
        #print results
        return json.dumps(results[0], indent = 4), 200
##        db_filename = 'data/faraday.db'
##        conn = sqlite3.connect(db_filename)
##        c= conn.cursor()
##        epochStamp = time.time() - 15*60
##        c.execute('SELECT DISTINCT callsign, id FROM telemetry WHERE apepoch >= ' + str(epochStamp))
##        results = c.fetchall()
##        data = []
##        for index, result in enumerate(results):
##            data.append({'callsign': result[0], 'nodeid': result[1]})
##        return json.dumps(data)

@app.route('/faraday/telemetry', methods=['GET'])
def telemetry():
##    if request.method == 'GET':
##        limit = request.args.get("limit", 1)
##        callsign = request.args.get("callsign")
##        nodeid = request.args.get("nodeid")
####        db_filename = 'data/faraday.db'
####        conn = sqlite3.connect(db_filename)
####        c= conn.cursor()
##        if callsign and nodeid:
##            results = faradaytelemetry.query.order_by(faradaytelemetry.keyid.desc()).filter(faradaytelemetry.callsign == str(callsign), faradaytelemetry.id == int(nodeid)).limit(limit).all()
##            results = data_schema.dump(results)
##        else:
##            results = faradaytelemetry.query.order_by(faradaytelemetry.keyid.desc()).limit(limit).all()
##            results = data_schema.dump(results)
    if request.method == 'GET':
        allTelemetry = []
        limit = request.args.get("limit", 1)
        callsign = request.args.get("callsign")
        nodeid = request.args.get("nodeid")
        if callsign and nodeid:
            results = faradaytelemetry.query.order_by(faradaytelemetry.keyid.desc()).filter(faradaytelemetry.callsign == str(callsign), faradaytelemetry.id == int(nodeid)).limit(limit).all()
            results = data_schema.dump(results)
            telemetry = results[0]
            scaledresults = faradayScaledTelemetry.query.order_by(faradayScaledTelemetry.keyid.desc()).filter(faradayScaledTelemetry.callsign == str(callsign), faradayScaledTelemetry.id == int(nodeid)).limit(limit).all()
            scaledresults = scaledtelemetry_schema.dump(scaledresults)
            scaledTelemetry = scaledresults[0]
            #Both debug and system settings do not yet specify callsign or node ID
            debugResults = faradayDebugTelemetry.query.order_by(faradayDebugTelemetry.keyid.desc()).limit(1)
            debugResults = debugTelemetry_schema.dump(debugResults)
            debugTelem = debugResults[0]
            systemResults = faradaySystemSettings.query.order_by(faradaySystemSettings.keyid.desc()).limit(1)
            systemResults = systemSettings_schema.dump(systemResults)
            systemSettingsTelem = systemResults[0]

            #combine telemetry
            try:
                allTelemetry.append(telemetry[0])
            except IndexError as e:
                allTelemetry.append(0)
                print "/telemetry Could not obtain telemetry[0]: ", e

            try:
                allTelemetry.append(scaledTelemetry[0])
            except IndexError as e:
                allTelemetry.append(0)
                print "/telemetry Could not obtain scaledTelemetry[0]: ", e
            try:
                allTelemetry.append(debugTelem[0])
            except IndexError as e:
                allTelemetry.append(0)
                print "/telemetry Could not obtain debugTelem[0]: ", e
            try:
                allTelemetry.append(systemSettingsTelem[0])
            except IndexError as e:
                allTelemetry.append(0)
                print "/telemetry Could not obtain systemSettingsTelem[0]: ", e

        else:
            results = faradaytelemetry.query.order_by(faradaytelemetry.keyid.desc()).limit(limit).all()
            results = data_schema.dump(results)

        #only return data, not errors
        #return json.dumps(results[0], indent = 4), 200
        return json.dumps(allTelemetry, indent = 4), 200

@app.route('/faraday/stats', methods=['GET'])
def stats():
    if request.method == 'GET':
        #limit = request.args.get("limit", 1)
        callsign = request.args.get("callsign")
        nodeid = request.args.get("nodeid")
##        db_filename = 'data/faraday.db'
##        conn = sqlite3.connect(db_filename)
##        c= conn.cursor()
        if callsign and nodeid:
            totalCount = faradaytelemetry.query.filter(faradaytelemetry.callsign == str(callsign), faradaytelemetry.id == int(nodeid)).count()
            results = faradaytelemetry.query.order_by(faradaytelemetry.keyid.desc()).filter(faradaytelemetry.callsign == str(callsign), faradaytelemetry.id == int(nodeid)).limit(1)
            results = data_schema.dump(results)
            lastHeard = results[0]
            #print lastHeard[0]

        else:
            pass
            #results = faradaytelemetry.query.order_by(faradaytelemetry.keyid.desc()).limit(limit).all()
            #results = data_schema.dump(results)

        #only return data, not errors

        return json.dumps([totalCount,lastHeard], indent = 4), 200
        #return '',200

@app.route('/faraday/addstation', methods=['POST'])
def addStation():
    if request.method == 'POST':
        callsign = request.form['callsign']
        nodeid = request.form['nodeid']
        aprf = request.form['aprf']
        print callsign, nodeid, aprf
        db.session.add(faradaytelemetry(callsign=str(callsign.upper()),id=str(nodeid),aprf=aprf,apepoch=time.time()))
        db.session.commit()
    return redirect("http://127.0.0.1:" + port + "/", code=302)

@app.route('/faraday/scaling', methods=['GET','POST'])
def stationScalingParameters():
    if request.method == 'GET':
        #print "scaling"

        callsign = request.args.get("callsign")
        nodeid = request.args.get("nodeid")
        try:
            results = faradayscaling.query.order_by(faradayscaling.keyid.desc()).filter(faradayscaling.callsign == str(callsign), faradayscaling.id == int(nodeid)).all()

        except StandardError as e:
            print e

        if len(results) == 0:
            print "didn't find station"
            # manually connect to database
            conn = sqlite3.connect(db_filename)
            c = conn.cursor()

            # add station to database scaling factor with standard scaling values
            c.execute("INSERT INTO faradayio(`callsign`,`id`,`keyname`) VALUES(?,?,?)",(callsign.upper(),int(nodeid),"STANDARD"))
            conn.commit()
            conn.close()

            #grab scaling values
            results = faradayscaling.query.order_by(faradayscaling.keyid.desc()).filter(faradayscaling.callsign == str(callsign), faradayscaling.id == int(nodeid)).all()

        results = scaling_schema.dump(results)
        return json.dumps(results[0], indent = 4), 200

@app.route('/', methods=['GET'])
def index():
    parser.read('faraday.ini')
    user = {"callsign": parser.get('faraday','callsign'),
            "nodeid": parser.get('faraday','nodeid'),
            "powerconf": parser.get('faraday','powerconf'),
            "bootfreq": parser.get('faraday','bootfreq'),
            "gpsboot": parser.get('faraday','gpsboot'),
            "uarttelemboot": parser.get('faraday','uarttelemboot'),
            "rftelemboot": parser.get('faraday','rftelemboot'),
            "telemport": parser.get('faraday','telemport'),
            "uartinterval": parser.get('faraday','uartinterval'),
            "rfinterval": parser.get('faraday','rfinterval'),
            "latitude": parser.get('location','latitude'),
            "latdir": parser.get('location','latdir'),
            "longitude": parser.get('location','longitude'),
            "londir": parser.get('location','londir'),
            "altitude": parser.get('location','altitude'),
            "adcscaling": parser.get('faraday','adcscaling'),
            "tempscaling": parser.get('faraday','tempscaling'),
            "tempoffset": parser.get('faraday','tempoffset'),
            "vddscaling": parser.get('faraday','vddscaling'),
            "vccscaling": parser.get('faraday','vccscaling')
            }

    IOState = { "led1": parser.get('faradayio','led1'),
                "led2": parser.get('faradayio','led2'),
                "gpio0": parser.get('faradayio','gpio0'),
                "gpio1": parser.get('faradayio','gpio1'),
                "gpio2": parser.get('faradayio','gpio2'),
                "gpio3": parser.get('faradayio','gpio3'),
                "gpio4": parser.get('faradayio','gpio4'),
                "gpio5": parser.get('faradayio','gpio5'),
                "gpio6": parser.get('faradayio','gpio6'),
                "gpio7": parser.get('faradayio','gpio7'),
                "gpio8": parser.get('faradayio','gpio8'),
                "gpio9": parser.get('faradayio','gpio9'),
                "mosfet": parser.get('faradayio','mosfet')}

    return render_template('index2.html', title='FaradayRF Modem',
                            user=user, accesspoint = faradayAP,
                            IOState = IOState)

@app.route('/config/', methods=['POST'])
def configure():
    if request.method == 'POST':
        #receive POST form data and parse it into the configuration format
        data = request.form
        print data
        if data['callsign']:
            parser.set('faraday','callsign',str(data['callsign']))
        if data['nodeid']:
            parser.set('faraday','nodeid',str(data['nodeid']))
        if data['powerconf']:
            parser.set('faraday','powerconf',str(data['powerconf']))
        if data['bootfreq']:
            parser.set('faraday','bootfreq',str(data['bootfreq']))
        if data['gpsboot']:
            parser.set('faraday','gpsboot',str(data['gpsboot']))
        if data['uarttelemboot']:
            parser.set('faraday','uarttelemboot',str(data['uarttelemboot']))
        if data['rftelemboot']:
            parser.set('faraday','rftelemboot',str(data['rftelemboot']))
        if data['uartinterval']:
            parser.set('faraday','uartinterval',str(data['uartinterval']))
        if data['rfinterval']:
            parser.set('faraday','rfinterval',str(data['rfinterval']))
        if data['latitude']:
            parser.set('location','latitude',str(data['latitude']))
        if data['latdir']:
            parser.set('location','latdir',str(data['latdir']))
        if data['longitude']:
            parser.set('location','longitude',str(data['longitude']))
        if data['londir']:
            parser.set('location','londir',str(data['londir']))
        if data['altitude']:
            parser.set('location','altitude',str(data['altitude']))


        #write configuration to file
        with open('faraday.ini', 'wb') as configfile:
            parser.write(configfile)
        unit = faraday.faraday()
        config_packet_payload = unit.create_config_packet()
        b64cmd = base64.b64encode(config_packet_payload)
        #Temporary fix for Proxy configuraration! Should move over to better Basic IO proxy. BSALMI 9-17-16
        #status = requests.post("http://127.0.0.1:" + port + "/faraday/2?cmd=%s" % b64cmd)
        payload = {'data' : [b64cmd]}
        status = requests.post("http://127.0.0.1:" + str(port) + "/post?" + "callsign=" + str('NOCALL').upper() + '&port=' + str(2) + '&' + 'nodeid=' + str(1), json = payload)
        print "SENDING CONFIG", status
        return redirect("http://127.0.0.1:" + port + "/", code=302)


    else:
        return "Error"

@app.route('/command/', methods=['POST'])
def command():
    data = request.form
    #print data

    p3on = int(0)
    p3off = int(0)
    p4on = int(0)
    p4off = int(0)
    p5on = int(0)
    p5off = int(0)

    try:
        if data['LED1'] == "ON":
            parser.set('faradayio','led1','1')
            p3on += gpio_allocation.LED_1
        else:
            parser.set('faradayio','led1','0')
            p3off += gpio_allocation.LED_1

        if data['LED2'] == "ON":
            parser.set('faradayio','led2','1')
            p3on += gpio_allocation.LED_2
        else:
            parser.set('faradayio','led2','0')
            p3off += gpio_allocation.LED_2

        if data['GPIO0'] == "ON":
            parser.set('faradayio','gpio0','1')
            p4on |= gpio_allocation.DIGITAL_IO_0
        else:
            parser.set('faradayio','gpio0','0')
            p4off |= gpio_allocation.DIGITAL_IO_0

        if data['GPIO1'] == "ON":
            parser.set('faradayio','gpio1','1')
            p4on |= gpio_allocation.DIGITAL_IO_1
        else:
            parser.set('faradayio','gpio1','0')
            p4off |= gpio_allocation.DIGITAL_IO_1

        if data['GPIO2'] == "ON":
            parser.set('faradayio','gpio2','1')
            p4on |= gpio_allocation.DIGITAL_IO_2
        else:
            parser.set('faradayio','gpio2','0')
            p4off |= gpio_allocation.DIGITAL_IO_2

        if data['GPIO3'] == "ON":
            parser.set('faradayio','gpio3','1')
            p4on |= gpio_allocation.DIGITAL_IO_3
        else:
            parser.set('faradayio','gpio3','0')
            p4off |= gpio_allocation.DIGITAL_IO_3

        if data['GPIO4'] == "ON":
            parser.set('faradayio','gpio4','1')
            p4on |= gpio_allocation.DIGITAL_IO_4
        else:
            parser.set('faradayio','gpio4','0')
            p4off |= gpio_allocation.DIGITAL_IO_4

        if data['GPIO5'] == "ON":
            parser.set('faradayio','gpio5','1')
            p4on |= gpio_allocation.DIGITAL_IO_5
        else:
            parser.set('faradayio','gpio5','0')
            p4off |= gpio_allocation.DIGITAL_IO_5

        if data['GPIO6'] == "ON":
            parser.set('faradayio','gpio6','1')
            p4on |= gpio_allocation.DIGITAL_IO_6
        else:
            parser.set('faradayio','gpio6','0')
            p4off |= gpio_allocation.DIGITAL_IO_6

        if data['GPIO7'] == "ON":
            parser.set('faradayio','gpio7','1')
            p4on |= gpio_allocation.DIGITAL_IO_7
        else:
            parser.set('faradayio','gpio7','0')
            p4off |= gpio_allocation.DIGITAL_IO_7

        if data['GPIO8'] == "ON":
            parser.set('faradayio','gpio8','1')
            p5on |= gpio_allocation.DIGITAL_IO_8
        else:
            parser.set('faradayio','gpio8','0')
            p5off |= gpio_allocation.DIGITAL_IO_8

        if data['GPIO9'] == "ON":
            parser.set('faradayio','gpio9','1')
            p5on |= gpio_allocation.DIGITAL_IO_9
        else:
            parser.set('faradayio','gpio9','0')
            p5off |= gpio_allocation.DIGITAL_IO_9

        if data['MOSFET'] == "ON":
            parser.set('faradayio','mosfet','1')
        else:
            parser.set('faradayio','mosfet','0')


    except StandardError as e:
        print "StandardError: ", e

    #print repr(p3on), repr(p3off)
    if data['aprf'] == "0":
        general_command.SendCommand(5, Command_Module.create_gpio_command_packet(p3on,p4on,p5on,p3off,p4off,p5off))
        if data['MOSFET'] == "ON":
            general_command.SendCommand(14, Command_Module.create_send_telemetry_device_debug_flash())
        if data['GETFLASHDEBUG'] == "ON":
            general_command.SendCommand_Send_Telem_Device_Debug_Flash()
        if data['GETSYSTEMSETTINGS'] == "ON":
            general_command.SendCommand_Send_Telem_Device_System_Settings()
        if data['RESETFLASHDEBUG'] == "ON":
            general_command.SendCommand_Reset_Device_Debug_Flash()
    else:
        callsign = str(data['callsign'])
        nodeid = int(data['id'])
        general_command.SendCommand(9,Command_Module.create_rf_command_packet(callsign, nodeid, 5, Command_Module.create_gpio_command_packet(p3on,p4on,p5on,p3off,p4off,p5off)))
        if data['MOSFET'] == "ON":
            general_command.SendCommand(9, Command_Module.create_rf_command_packet(callsign, nodeid, 14, Command_Module.create_local_telem_update_packet()))

    #with open('faraday.ini', 'wb') as configfile:
        #parser.write(configfile)


    return redirect("http://127.0.0.1:" + port + "/", code=302)

@app.route('/command/missions', methods=['POST'])
def commandMissions():
    data = request.form
    print data

    p3on = int(0)
    p3off = int(0)
    p4on = int(0)
    p4off = int(0)
    p5on = int(0)
    p5off = int(0)

    if data['aprf'] == "0":
        if data['RESETHABTIMER'] == "ON":
            general_command.SendCommand_HAB_Reset_Auto_Cutdown_Timer()
        if data['DISABLEHABTIMER'] == "ON":
            general_command.SendCommand_HAB_Disable_Auto_Cutdown_Timer()
        if data['CUTDOWN'] == "ON":
            general_command.SendCommand_HAB_Activate_Cutdown_Event()
        if data["SETHABCUTDOWNEVENTIDLE"] == "ON":
            general_command.SendCommand_HAB_Set_Cutdown_Idle()


    else:
        callsign = str(data['callsign'])
        nodeid = int(data['id'])
        if data['RESETHABTIMER'] == "ON":
            general_command.SendCommand_RF_HAB_Reset_Auto_Cutdown_Timer(callsign,nodeid)
        if data['DISABLEHABTIMER'] == "ON":
            general_command.SendCommand_RF_HAB_Disable_Auto_Cutdown_Timer(callsign,nodeid)
        if data['CUTDOWN'] == "ON":
            general_command.SendCommand_RF_HAB_Activate_Cutdown_Event(callsign,nodeid)
        if data["SETHABCUTDOWNEVENTIDLE"] == "ON":
            general_command.SendCommand_RF_HAB_Set_Cutdown_Idle(callsign,nodeid)


    return redirect("http://127.0.0.1:" + port + "/", code=302)


@app.route('/command/ram', methods=['POST','GET'])
def ramcommand():
    if request.method == 'POST':
        data = request.form
        if(data['callsign'] and data['nodeid']):
            general_command.SendCommand(4, Command_Module.create_update_callsign_packet(data['callsign'], data['nodeid']))
        if(data['rffreq']):
            general_command.SendCommand(4, Command_Module.create_update_rf_frequency_packet(data['rffreq']))

        return redirect("http://127.0.0.1:" + port + "/", code=302)

    if request.method == 'GET':
        data = request.form
        print request.args.get("TXUART")
        if(request.args.get("TXUART")):
            general_command.SendCommand(7, Command_Module.create_local_telem_update_packet())
            print "SENT!"
        return redirect("http://127.0.0.1:" + port + "/", code=302)

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    t.interrupt_main()
    return 'Server shutting down...',200

def callsign2COM():
    local = {}
    num = int(parser.get('proxy','units'))
    units = range(0,num)
    for unit in units:
        item = "UNIT" + str(unit)
        callsign = parser.get(item,"callsign")
        nodeid = parser.get(item,"nodeid")
        com = parser.get(item,"com")
        #print callsign, nodeid
        local[str(item)] = [callsign,nodeid,com]

    local = json.dumps(local)
    return json.loads(local)

def main():
    global units #maybe bad to do?
    units = callsign2COM()
    threads = []

    global uartDevice
    while True:
        try:
            #uartDevice = Simple_Transport_Services.uart_interface_class(comport,baudrate,timeout)
            uartDevice = layer_4_service.faraday_uart_object(comport,baudrate,timeout)
            break
        except:
            print "No FaradayRF Modem detected"
        time.sleep(1)


    t = threading.Thread(target=uart_worker, args=(uartDevice,queDict))
    threads.append(t)
    t.start()

    #Start the telemetry retrieval thread if configuration enables
    if(telemetry_autoretrieve):
        Telemetry.main()

    aprs.main()
    #Not the most reliable, I should write this code to ENSURE that telemetry and aprs start AFTER app.run...
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    app.run(port=port, threaded=True)



if __name__ == '__main__':
    main()

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
import logging.config
import base64
import datetime
import struct
import sqlite3
import os
from faraday import faraday
from ConfigParser import SafeConfigParser
#import HAB

#setup proxy from configuration file
parser = SafeConfigParser()
parser.read('faraday.ini')
port = str(parser.getint('proxy','port'))


#Setup Logging
with open('logging.json') as f:
    configfile = json.load(f)
    logging.config.dictConfig(configfile)
logger = logging.getLogger("telemetry")

logger.info("Starting Telemetry Application")

#make one global dictionary of queues
portList = []
queDict = {}

# Set telemetry port
telemport = 5

def port_Worker(queDict):
    """Queries local proxy for open ports and obtains data from them

    keyword arguments:
    queDict -- dictionary to be used for LIFO buffer
    """
    #Find open ports on localhost

    while(True):
        portInfo = requests.get("http://127.0.0.1:" + port + "/faraday/ports")
        try:
            ports = json.loads(portInfo.text)
            break

        except ValueError:
            logging.debug("No JSON port data returned from API call")
            pass
        time.sleep(1) #wait 1 second and try again

    #Append open ports received to local ports list
    for key in ports:
        logging.info("Faraday port %d available" % ports[key]['port'])
        portList.append(ports[key]['port'])

    #setup requests session so we efficiently use the connection
    s = requests.session()

    #Infinite loop through telemetry port to obtain data
    #Save data to a LIFO que for each port

    while True:
        queryTime = time.asctime(time.localtime(time.time()))
        #print "Obtaining port %d telemetry data..." % telemport, queryTime
        #logging.info("Querying port %d data from queue" % telemport)
        #Localhost in URL can cause massive delay due to FQDN resolution
        try:
            data = s.get("http://127.0.0.1:" + port + "/faraday/%d" % telemport)

        except requests.exceptions.RequestException as error:
            print "RequestException: ", error
        if(data.text):
            try:
                #print data.text
                JSONdata = json.loads(data.text)
                for i in range(0,len(JSONdata)):
                    #data is encoded in BASE64 for network transmission, decode
                    b64Data = base64.b64decode(JSONdata[i]['data'])
                    #print repr(b64Data)
                    dataTime = datetime.datetime.now()
                    JSONdata[i]['data'] = b64Data
                    try:
                        #print(len(queDict[telemport]))
                        queDict[telemport].append(JSONdata[i])

                    except:
                        # this exception likely due to buffer not existing
                        queDict[telemport] = deque([], maxlen=100)
                        queDict[telemport].append(JSONdata[i])

            except ValueError as error:
                print "ValueError: ", error
            except IndexError as error:
                print "IndexError: ", error

        time.sleep(1) #try to obtain telemetry every second



def telemetry_Worker(queDict):
    """Pops items to the left off of port queues and saves to SQLite database

    keyword arguments:
    queDict -- dictionary to be used for LIFO buffer
    """

    # Create Faraday Access Point
    accesspoint = faraday()
    node = faraday()

    #Open SQLite database, create one if not, timestamp ISO 8601 format
    timestamp = time.strftime("%Y-%m-%dT%H%M%S")
    #db_filename = 'data/telemetry_' + timestamp + '.db'
    db_filename = 'data/faraday.db'
    #print "Creating database file " + db_filename + "\n"
    schema_filename = 'telemetryschema.sql'
    conn = sqlite3.connect(db_filename)
    c= conn.cursor()

    #Bytestream Application initialization
    #habclassobj = HAB.HabPacketClass(db_filename, schema_filename) #HAB application packet parsing object

    #infinite loop through queue popping off items and saving to database
    #each dataset takes about 100ms to parse and save to database
    while True:
        for i in range(0,len(portList)):
            try:
                #check to see that queue has data in it
                if(len(queDict) > 0):
                    #check to make sure at least two lines are in queue
                    if(len(queDict[portList[i]]) > 0):
                        data = queDict[portList[i]].popleft()
                        try:
                            telemetryData = node.unpackTelemetry(data)
                            #print telemetryData
                            if telemetryData[1] == 3:
                                checksum_status = telemetryData[6]
                            if telemetryData[1] == 2:
                                checksum_status = telemetryData[5]
##                            #Check if checksum is OK in telemetry data!
##                            checksum_rx = telemetryData[4]
##                            checksum_computed = telemetryData[5]
##                            checksum_status = checksum_rx == checksum_computed
                        except IndexError as e:
                            print "IndexError unpacking telemetry: ", e
                        except StandardError as e:
                            print "StandardError unpacking telemetry: ", e
                        try:
                            #node.saveSQLTelem(tlmJSON,conn)
                            if(checksum_status == True):
                                #print "Received Telemetry"
                                if(telemetryData[1] == 3):
                                    tlmJSON = node.parseTelemetry(telemport,telemetryData[0],telemetryData[1],telemetryData[2],telemetryData[3],accesspoint)
                                    node.saveSQLTelem(tlmJSON,conn)
                                elif(telemetryData[1] == 2):
                                    tlmJSON = node.parseDebugTelemetry(telemport,telemetryData[0],telemetryData[1],telemetryData[2])
                                    node.saveSQLDebugTelem(tlmJSON,conn)
                                elif(telemetryData[1] == 1):
                                    tlmJSON = node.parseSystemSettings(telemport,telemetryData[0],telemetryData[1],telemetryData[2])
                                    node.saveSQLSystemSettings(tlmJSON,conn)
                                else:
                                    print "No saving of: ", telemetryData

                                #Application loops for telemetry bytestream parsing
                                #BytestreamApplicationLoops(habclassobj)

                            else:
                                print "CHECKSUM FAILED"
                        except StandardError as e:
                            print "Save Telemetry StandardError: ", e

            except IndexError as e:
                print "index error :", e
            except TypeError as e:
                print "Type error 5:", e
            except ValueError as e:
                print "ValueError ", e
            except KeyError as e:
                #Dictionary key not found
                print e
                pass

        time.sleep(0.05)



##def BytestreamApplicationLoops(*args):
##    #HAB - Use object to parse only new items from byte stream
##    HAB.HabMainLoop(args[0])

def main():
    """main function connects or creates database and spawns thread workers"""

    threads = []
    t1 = threading.Thread(target = port_Worker, args = (queDict,))
    t2 = threading.Thread(target = telemetry_Worker, args = (queDict,))
    threads.append(t1)
    threads.append(t2)
    t1.start()
    t2.start()

if __name__ == '__main__':
    main()

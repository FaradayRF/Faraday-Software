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
import base64
import datetime
from faraday import faraday

#make one global dictionary of queues
portList = []
queDict = {}

#define telemetry port
telemport = 5       # Port 5 is the predefined telemetry port


def port_Worker(queDict):
    """Queries local proxy for open ports and obtains data from them

    keyword arguments:
    queDict -- dictionary to be used for LIFO buffer
    """
    #Find open ports on localhost

    while(True):
        portInfo = requests.get('http://127.0.0.1/faraday/ports')
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
        logging.info("Querying port %d data from queue" % telemport)
        #Localhost in URL can cause massive delay due to FQDN resolution
        try:
            data = s.get('http://127.0.0.1/faraday/%d' % telemport)

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

    #Open connection to faradayrf.com API
    s = requests.session()
    headers = {'content-type': 'application/json'}

    #infinite loop through queue popping off items and saving to database
    #each dataset takes about 100ms to parse and save to database
    while True:
        for i in range(0,len(portList)):
            try:
                #check to see that queue has data in it
                if(len(queDict) > 0):
                    #check to make sure data is actually in the qeue
                    if(len(queDict[portList[i]]) > 0):
                        data = queDict[portList[i]].popleft()
                        telemetryData = node.unpackTelemetry(data)
                        tlmJSON = node.parseTelemetry(telemport,telemetryData[0],telemetryData[1],telemetryData[2],telemetryData[3],accesspoint)
                        try:
                            tlmDumped = json.dumps(tlmJSON)
                            #print tlmDumped, "\r"

                        except ValueError as e:
                            print e
                        except StandardError as e:
                            print e

                        try:
                            server = "http://faradayrf.com/api/telemetry"
                            result = requests.post(server, data = tlmDumped, headers = headers)
                            result.raise_for_status()
                            queryTime = time.asctime(time.localtime(time.time()))
                            print "Sent telemetry data to %s on %s" % (server,queryTime)

                        except requests.exceptions.Timeout as e:
                            print "Timeout Error\n", e
                        except requests.ConnectionError as e:
                            print "Connection Error\n", e
                        except requests.HTTPError as e:
                            print "HTTP Error\n", e

            except IndexError as e:
                print "index error :", e
            except TypeError as e:
                print "Type error :", e
            except ValueError as e:
                print "ValueError ", e
            except KeyError as e:
                #Dictionary key not found
                pass

        time.sleep(0.05)

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

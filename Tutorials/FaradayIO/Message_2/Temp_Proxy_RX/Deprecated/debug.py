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


#make one global dictionary of queues
portList = []

def port_Worker():
    """This thread queries for open ports on localhost and obtains data from them"""
    #Find open ports on localhost

    while(True):
        portInfo = requests.get('http://127.0.0.1:5000/faraday/ports', timeout=0.5)
        if len(portInfo.text) > 0:
            try:
                ports = json.loads(portInfo.text)
            except ValueError as error:
                print "Problem obtaining port info\r"
                print error;

            else:
                for key in ports:
                    #Append all port numbers to a local python list
                    portList.append(ports[key]['port'])
                while True:
                    #infinit loop to obtain data from all open ports, restart script if new
                    #ports open after initialization
                    for port in portList:
                        data = requests.get('http://127.0.0.1:5000/faraday/%d' % port)
                        if len(data.text) > 0:
                            try:
                                JSONdata = json.loads(data.text)
                            except ValueError as error:
                                print "ports" , error
                            else:
                                for i in range(0,len(JSONdata)):
                                    #data is encoded in BASE64 for network transmission, decode
                                    b64Data = base64.b64decode(JSONdata[i]['data'])
                                    dataTime = datetime.datetime.now()
                                    print dataTime.strftime("%a %b %d %H:%M:%S %Y")
                                    print "Port %d: " % JSONdata[i]['appPort'], repr(b64Data), "\r\n"
                    time.sleep(1)
        time.sleep(1) #wait 1 second before trying to find ports again

def main():
    """main functoin spawns thread worker"""
    threads = []
    t1 = threading.Thread(target= port_Worker)
    threads.append(t1)
    t1.start()

if __name__ == '__main__':
    main()

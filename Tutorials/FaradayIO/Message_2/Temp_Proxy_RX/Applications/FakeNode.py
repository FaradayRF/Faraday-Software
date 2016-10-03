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
import logging
import sqlite3
from ConfigParser import SafeConfigParser

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def SQL_Worker():
    """Opens up SQLite database from config file and uploads to webserver

    keyword arguments:
    None
    """
    i = 0
    flag1 = False
    flag2 = False
    flag3 = False

    #setup SQLite Uploader from configuration file
    parser = SafeConfigParser()
    parser.read('faraday.ini')

    filename = 'data/'
    filename += parser.get('sqliteuploader','filename')
    filename += '.db'
    print "Starting upload of %s\n" %filename

    #Replace with config file read later. or console browse
    conn = sqlite3.connect(filename)
    conn.row_factory = dict_factory
    c = conn.cursor()
    headers = {'content-type': 'application/json'}

    c.execute('SELECT * FROM telemetry ORDER BY keyid')
    data = c.fetchall()
    length = len(data)
    print "Uploading %d telemetry packets to server" % length

    for row in data:
        jsonTelem = json.dumps(row)
        print jsonTelem, '\r'
        result = requests.post("http://127.0.0.1/faraday/telemetry", jsonTelem, headers = headers)
        #result = requests.post("http://www.faradayrf.com/api/telemetry", jsonTelem, headers = headers)
        #print result.text
        i+=1
        if((i > length*0.25) and (flag1 == False)):
            print "25% complete..."
            flag1 = True
        if((i > length*0.5) and (flag2 == False)):
            print "50% complete..."
            flag2 = True
        if((i > length*0.75) and (flag3 == False)):
            print "75% complete..."
            flag3 = True
        time.sleep(1)
    print "Upload Complete!"

def main():
    """main function simply calls SQL_Worker function"""

    SQL_Worker()

if __name__ == '__main__':
    main()

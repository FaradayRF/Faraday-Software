import requests
import base64
import json
import time
import ConfigParser
import os

# Open configuration INI
config = ConfigParser.RawConfigParser()
filename = os.path.abspath("simpleui.ini")
config.read(filename)

telemhost = config.get('FLASKTELEM', 'HOST')
telemport = int(config.get('FLASKTELEM', 'PORT'))

localcallsign = config.get('UNITS', 'UNIT0CALL')
localnodeid = int(config.get('UNITS', 'UNIT0ID'))


def getstations():
    """
    Get stations heard.
    """

    queuelen = requests.get('http://' + str(telemhost) + ':' + str(telemport) + '/stations')
    queuesize = queuelen.json()

    return queuesize

print getstations()
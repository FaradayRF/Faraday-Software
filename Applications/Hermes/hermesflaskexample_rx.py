import requests
import base64
import cPickle
import time
import ConfigParser
import os

#Open configuration INI
config = ConfigParser.RawConfigParser()
filename = os.path.abspath("hermes.ini")
config.read(filename)

localcallsign = config.get('UNIT0', 'CALLSIGN')
localnodeid = int(config.get('UNIT0', 'NODEID'))


def getQueueSize(callsign, nodeid):
        payload = {'localcallsign': callsign, 'localnodeid': int(nodeid)}
        queuelen = requests.get('http://127.0.0.1:8005/queue', params = payload)
        queue_raw = queuelen.json()
        queue_b64 = base64.b64decode(queuelen.json())
        queue_b64_pickle = cPickle.loads(base64.b64decode(queuelen.json()))
        return queue_b64_pickle['queuesize']


def main():
    while 1:
        #Sleep to release python process
        time.sleep(0.1)

        #Check if items in queue
        while getQueueSize(localcallsign, localnodeid) > 0:
            payload = {'localcallsign': localcallsign, 'localnodeid': localnodeid}
            rxdata = requests.get('http://127.0.0.1:8005/', params=payload)
            rx_raw = rxdata.json()
            rx_b64 = base64.b64decode(rxdata.json())
            rx_b64_pickle = cPickle.loads(base64.b64decode(rxdata.json()))
            print "\nFROM:", rx_b64_pickle['source_callsign']
            print "Message:", rx_b64_pickle['message']


if __name__ == '__main__':
    main()




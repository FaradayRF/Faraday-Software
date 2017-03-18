import requests
import base64
import cPickle
import time


while 1:
    #Sleep to release python process
    time.sleep(5)
    #Check if items in queue
    queuelen = requests.get('http://127.0.0.1:8005/queue')
    queue_raw = queuelen.json()
    queue_b64 = base64.b64decode(queuelen.json())
    queue_b64_pickle = cPickle.loads(base64.b64decode(queuelen.json()))
    if queue_b64_pickle['queuesize'] > 0:
        rxdata = requests.get('http://127.0.0.1:8005')
        rx_raw = rxdata.json()
        rx_b64 = base64.b64decode(rxdata.json())
        rx_b64_pickle = cPickle.loads(base64.b64decode(rxdata.json()))
        print "\nFROM:", rx_b64_pickle['source_callsign']
        print "Message:", rx_b64_pickle['message']







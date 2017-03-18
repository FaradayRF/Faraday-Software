import requests
import base64
import cPickle

#r = requests.get('http://127.0.0.1:8005/queue')
#print "Queue:", r.json()

queuelen = requests.get('http://127.0.0.1:8005/queue')


queue_raw = queuelen.json()
queue_b64 = base64.b64decode(queuelen.json())
queue_b64_pickle = cPickle.loads(base64.b64decode(queuelen.json()))

print queue_raw
print queue_b64_pickle

rxdata = requests.get('http://127.0.0.1:8005')

rx_raw = rxdata.json()
rx_b64 = base64.b64decode(rxdata.json())
rx_b64_pickle = cPickle.loads(base64.b64decode(rxdata.json()))

print "\nFROM:", rx_b64_pickle['source_callsign']
print "Message:", rx_b64_pickle['message']

print '\n**** DEBUG INFO ****'
print "Message RAW (Base64):", rx_raw
print "Message Decoded Base64 and Cpickle:", rx_b64_pickle


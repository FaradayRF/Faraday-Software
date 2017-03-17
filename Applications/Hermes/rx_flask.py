import requests
import base64
import cPickle

#r = requests.get('http://127.0.0.1:8005/queue')
#print "Queue:", r.json()

r = requests.get('http://127.0.0.1:8005')
print "Message RAW:", r.json()
print "Message Decoded Base64:", base64.b64decode(r.json())
print "Message Decoded Base64 and Cpickle:", cPickle.loads(base64.b64decode(r.json()))
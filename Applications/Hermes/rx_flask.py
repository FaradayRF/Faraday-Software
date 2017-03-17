import requests

r = requests.get('http://127.0.0.1:8005/queue')
print "Queue:", r.json()

r = requests.get('http://127.0.0.1:8005')
print "Message:", r.json()
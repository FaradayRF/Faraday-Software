import requests
import base64
import cPickle
import time



def main():
    message = "Hello World!"
    payload = {'localcallsign': 'kb1lqd', 'localnodeid': 1, 'data': message}
    rxdata = requests.post('http://127.0.0.1:8005/', params=payload)


if __name__ == '__main__':
    main()




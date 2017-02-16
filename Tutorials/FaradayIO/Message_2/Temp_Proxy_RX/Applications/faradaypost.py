#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Bryce
#
# Created:     13/09/2016
# Copyright:   (c) Bryce 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import requests
import time

def main():
    # Sends a post request to /post with automaticly json.dumps(payload) from
    # the requests module. First command turns LED1 on, one second later
    # LED1 is turned off.
    payload = {"data": ["BQZAAACA/wwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHW"]}
    r = requests.post("http://localhost/post?callsign=KB1LQD&nodeid=22&port=2", json=payload)
    print r
    time.sleep(1)
    payload = {"data": ["BQYAAADA/wwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHW"]}
    r = requests.post("http://localhost/post?callsign=KB1LQD&nodeid=22&port=2", json=payload)
    print r

if __name__ == '__main__':
    main()

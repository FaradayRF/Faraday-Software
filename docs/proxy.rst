================
Proxy
================
The Proxy application is the interface between a Faraday UART USB compliant radio and the Localhost interface on a computer. It handles all serial COM port communications presenting data to the user through a RESTful interface. Nearly all applications will use the Proxy to communicate over the radio hardware. Unless you are absolutely sure you need to bypass Proxy it is highly encouraged to use it.

.. image:: images/FaradayBlocks.png

Basic Operation
-----------------
Proxy works on the premise of spinning up a thread which has the sole purpose of querying every "port" (0-255) of the Faraday radio to see if new data is available. This is called the "UART Worker". Upon data being available the thread will receive the data and place it into a buffer queue. This queue is 100 packets long and is a FIFO resulting in old data being popped off if no user is requesting data. The same occurs in reverse. 

A flask server runs in the main process which provides a RESTful interface for the Proxy. When the RESTful interface is queried with a GET request the thread-safe queue will pop off packets from the left for the requested Faraday "port". This data is served to the user in a JSON dictionary. If the RESTful interface received a POST request to send data to Faraday then the flask server will place the packet onto the queue from the right. Every 10ms the UART Worker checks to see if there is any data for any port in the transmit queue. If present, this data is immediately sent to Faraday via USB UART.

API Documentation
==================
Send/Receive Faraday Data
-------------------------
Checks the proxy queue for the specified port. If packets are present in the qeue they are returned as a JSON dictionary as an HTTP response. Additionally, the POST method will add packets to the POST queue which are sent to Faraday on a periodica basis. Invalid parameters are responded with appropriate HTTP responses and relevant warning messages.

* **http://localhost:8000/**
	Port 8000 of localhost (127.0.0.1)

* **Method**
	GET | POST

* **URL Params**
	**Required**
		* ``Callsign=[String]``
		* ``NodeID=[Integer]``
		* ``Port=[Integer]``
	
	**Optional**
		* ``Limit=[Integer]``

* **Data Params**
	When making a POST request Proxy expects to receive JSON data in the body with an object containing a string "data" and value being an array of BASE64 encoded strings each 163 characters long. The header of the POST request must specify the content type as application/json. Only a data array of 100 packets is accepted.
	
* **Success Response**
	GET
	
	* **Code**: 200 OK
		**Content**: ``[{"data": "<163 Characters of BASE64>"},{"data": "<163 Characters of BASE64>"},...]``
	
	
	* **Code**: 204 NO CONTENT
		**Content**: Empty string
	
	POST
	
	* **Code**: 200 OK
		**Content**: ``{ "status": "Posted x of y Packet(s)" }``

	
	* **Code**: 204 NO CONTENT
		**Content**: Empty String
	
* **Error Response**
	GET

	* **Code**: 400 BAD REQUEST
		**Content**: ``{ "error": "<Python exception string>" }``
		
	POST

	* **Code**: 400 BAD REQUEST
		**Content**: ``{ "error": "<Python exception string>" }``
		
* **Sample Call**
    GET::

        # Simple GET request putting response into variable r
        # Port 5 is the telemetry port of Faraday so we will receive three telemetry packets
        payload = {'callsign': 'kb1lqd','nodeid': 22,'port':5,'limit': 3}
        r = requests.get('http://localhost:8000/',params=payload)

        # Printing text response from Proxy
        print(r.text)

        # Printing with requests built-in JSON decoder
        for item in r.json():
            print item, '\n'

    *Printing text output from Python sample GET call*::

        [
         {
          "data": "AwBhS0IxTFFEBXsDBhZLQjFMUUQFewMGFggAAAACANAHMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMAAHYAkuCBAIDAfaB9cHtwAAACQLJwAAHCAAAAAAAAAAAAAAAAAAAAAAAAAAAABOxBIs"
         }, 
         {
          "data": "AwBhS0IxTFFEAADDBhZLQjFMUUSxAAAGFgkAAAACANAHMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMAAHYAktCBEIDQfaB9cHugAAACMLLAAAHCAAAAAAAAAAAAAAAAAAAAAAAE7EAACXIxNd"
         }, 
         {
          "data": "AwBhS0IxTFFEBXsDBhZLQjFMUUQAAMMGFgoAAAACANAHMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMAAHYAksCBAICwfaB9UHtwAAACMLLwAAHCAAAAAAAAAAAAAAAAAAAAAAAAAATsQAABJw"
         }
        ]

    *Printing output of requests built-in JSON decoder from Python Sample GET Call*::

        {u'data': u'AwBhS0IxTFFEBXsDBhZLQjFMUUQFewMGFggAAAACANAHMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMAAHYAkuCBAIDAfaB9cHtwAAACQLJwAAHCAAAAAAAAAAAAAAAAAAAAAAAAAAAABOxBIs'} 

        {u'data': u'AwBhS0IxTFFEAADDBhZLQjFMUUSxAAAGFgkAAAACANAHMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMAAHYAktCBEIDQfaB9cHugAAACMLLAAAHCAAAAAAAAAAAAAAAAAAAAAAAE7EAACXIxNd'} 

        {u'data': u'AwBhS0IxTFFEBXsDBhZLQjFMUUQAAMMGFgoAAAACANAHMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMAAHYAksCBAICwfaB9UHtwAAACMLLwAAHCAAAAAAAAAAAAAAAAAAAAAAAAAATsQAABJw'}

    POST::

        # Create dictionary with array of one BASE64 string which turns LED 1 ON
        # Send POST data to port 2 of Faraday radio which is the command port
        content = {'data': ["BQZAAACA/wwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHW"]}
        payload = {'callsign': 'kb1lqd','nodeid': 22,'port':2}
        
        r = requests.post('http://localhost:8000/', params=payload, json=content)
        
        # Print text response from Proxy
        print(r.text)

    *Printing text output response from Python Sample POST call*::

        {"status": "Posted 1 of 1 Packet(s)"}

* **Notes**
    * 10/9/2016
        * Proxy uses the built-in debug server of Flask. For higher performance one may need to move to an Apache or WSGI based server.
        * All text responses from Proxy are to be JSON
        * No attempt to secure local communications have been made yet with HTTPS as these services are intended to stay localhost.
        * Running on http://localhost:8000 allows port 80 to be used by a User Interface (UI) application.
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
--------------------
Checks the proxy queue for the specified port to receive any data packets that may be present. If present the packets are returned as a JSON dictionary as an HTTP response. Additionally, the POST call will add packets to the POST queue which are sent to Faraday on a periodica basis.

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
	* **Code**: 200
	* **Content**: ``JSON response, {'Content-Type': 'application/json'}``
	
	*OR*
	
	POST
	* **Code**: 200
	* **Content**: ``{ status : "POSTED" }``
	
	*OR*
	
	* **Code**: 204
	* **Content**: ``{ status : "EMPTY" }``
	
* ** Error Response**
	GET
	* **Code**: 204
	* **Content**: ``{ error : "NO QUEUE DATA" }``
	
	*OR*
	
	* **Code**: 400
	* **Content**: ``{ error : PYTHON EXCEPTION STRING }``
	
	*OR*
	
	* **Code**: 400
	* **Content**: ``{ error : "MISSING URL PARAMETER" }``
	

	
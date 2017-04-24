# Proxy
Proxy is defined as 

> "...the agency, function, or office of a deputy who acts as a substitute for another" 

and this is exactly what this program does. Proxy is the piece of software which any other software communicates with in order to communicate with the hardware. It is the middle-man between the CC430 serial UART and network interface from which other software applications can communicate with. Providing this layer of abstraction greatly simplifies any application development.

## Basic Operation
Proxy works on the premise of spinning up a thread which has the sole purpose of querying every “port” (0-255) of the Faraday radio to see if new data is available. This is called the [UART Worker](https://github.com/FaradayRF/Faraday-Software/blob/master/proxy/proxy.py#L44). Upon data being available, the thread will receive the data and place it into a buffer queue. This queue is 100 packets long and is a FIFO resulting in old data being popped off if no user is requesting data. The same occurs in reverse with data posted to Proxy using the HTTP POST method.

A flask server runs in the main process which provides a RESTful interface for the Proxy. When the RESTful interface is queried with a GET request the thread-safe queue will pop off packets for the requested Faraday “port” from the left . This data is served to the user in a JSON dictionary. If the RESTful interface received a POST request to send data to Faraday then the flask server will place the packet onto the queue from the right. Every 10ms the UART Worker checks to see if there is any data for any port in the transmit queue. If present, this data is immediately sent to Faraday via USB UART.

Checks the proxy queue for the specified port. If packets are present in the qeue they are returned as a JSON dictionary as an HTTP response. Additionally, the POST method will add packets to the POST queue which are sent to Faraday on a periodica basis. Invalid parameters are responded with appropriate HTTP responses and relevant warning messages.

## Basic Configuration
 
Before Proxy can connect to any radio hardware, it needs to be configured using the `proxy.ini` file with your callsign and the serial port.
 
 1. Navigate to the `Proxy` folder
 2. Create a copy of `proxy.sample.ini` and rename the new file `proxy.ini`
 3. Open `proxy.ini` in a text editor and update the requested information noted  by `REPLACEME`
 
Configuring Proxy consists of changing three parameters for basic use:`CALLSIGN`, `NODEID` and `COM`. These will let Telemetry properly query Proxy to obtain the correct telemetry data.  
 
* `[UNIT0]`: Unit 0 Proxy configuration values section
  * `CALLSIGN`: Callsign to associate with radio on this USB port
  * `NODEID`: Node ID of radio connected on this USB port
  * `COM`: COM/serial Port associated with the radio connected

## Logging Configuration
Proxy is able to save all data in BASE64 format to a SQLite database for future playback. This is extremely helpful if raw UART data is desired as BASE64 can be converted into binary. Additionally, it enabled replays of events and use of software without the need for hardware in "Test Mode".

Open `proxy.ini` and configure the following in addition to the Basic Configuration above:

`[DATABASE]`
* `FILENAME=log.db`: Filename of Proxy log to be created

`[PROXY]`
* `LOG=1`: Enable Proxy logging mode (boolean)
* `UNITS=1`: Number of UART units to log

Now, when you run `Proxy` it will log to the database in the background while you are free to use software normally. You can stop Proxy normally without issue.

## Test Mode Configuration
With a SQLite log file, one can play it back as if hardware is connected. To do so please disable logging mode and edit the following `proxy.ini` configuration items:

`[TESTDATABASE]`
* `FILENAME=examplelogs/2017-04-20-01.db`: Proxy log file to play in test mode. Example log provided in examplelogs/ folder.

`[PROXY]`
* `TESTMODE=1`: Enable payback test mode
* `TESTRATE=1`: Set rate in Hz to read each row of database back
* `TESTCALLSIGN=KB1LQC`: Set callsign to appear as Proxy connected Faraday radio
* `TESTNODEID=2`: Set nodeid to appear as Proxy connected Faraday radio

Once properly configured and logging mode is disabled in `proxy.ini` then running `Proxy` normally will result in the log file being read into `Proxy` at the indicated rate. It will not repeat once the end of the file is reached.

## Examples
### GET
```
import requests

# Simple GET request putting response into variable r
# Port 5 is the telemetry port of Faraday so we will receive three telemetry packets
payload = {'callsign': 'kb1lqd','nodeid': 22,'port':5,'limit': 3}
r = requests.get('http://localhost:8000/',params=payload)

# Printing text response from Proxy
print(r.text)

# Printing with requests built-in JSON decoder
for item in r.json():
    print item, '\n'
```
Printing text response from Python sample GET call:
```
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
```
Printing output of requests built-in JSON decoder from Python Sample GET Call:
```
{u'data': u'AwBhS0IxTFFEBXsDBhZLQjFMUUQFewMGFggAAAACANAHMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMAAHYAkuCBAIDAfaB9cHtwAAACQLJwAAHCAAAAAAAAAAAAAAAAAAAAAAAAAAAABOxBIs'}

{u'data': u'AwBhS0IxTFFEAADDBhZLQjFMUUSxAAAGFgkAAAACANAHMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMAAHYAktCBEIDQfaB9cHugAAACMLLAAAHCAAAAAAAAAAAAAAAAAAAAAAAE7EAACXIxNd'}

{u'data': u'AwBhS0IxTFFEBXsDBhZLQjFMUUQAAMMGFgoAAAACANAHMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMAAHYAksCBAICwfaB9UHtwAAACMLLwAAHCAAAAAAAAAAAAAAAAAAAAAAAAAATsQAABJw'}
```

## API Reference
### http://localhost:8000/
Port 8000 of localhost (127.0.0.1) hosts the flask server where Proxy is exposed

### Method
`GET` | `POST`

### URL Params
 * Required
  * `Callsign` = [String]
  * `NodeID` = [Integer]
  * `Port` = [Integer]
 * Optional
  * `Limit` = [Integer]

### Data Params
When making a POST request Proxy expects to receive JSON data in the body with an object containing a string “data” and value being an array of BASE64 encoded strings each 164 characters long. The header of the POST request must specify the content type as application/json. Only a data array of 100 packets is accepted.

### Success Response

#### GET
```
Code: 200 OK

    Content: [{"data": "<164 Characters of BASE64>"},{"data": "<164 Characters of BASE64>"},...]

Code: 204 NO CONTENT

    Content: Empty string
```

#### POST
```
Code: 200 OK

    Content: { "status": "Posted x of y Packet(s)" }

Code: 204 NO CONTENT

    Content: Empty String
```
####Error Response
```
GET

    Code: 400 BAD REQUEST

        Content: { "error": "<Python exception string>" }

POST

    Code: 400 BAD REQUEST

        Content: { "error": "<Python exception string>" }
```

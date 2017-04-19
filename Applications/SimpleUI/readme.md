# Simple UI
This is a basic user interface to interact with the Faraday radios whether local or remote. It is based on Flask and Jquery/Bootstrap to provide a simplistic experience. Simple UI is usable for general commanding and monitoring of live data as well as basic High Altitude Balloon flights.

A secondary goal of having a basic user interface that can be used to show how python/javascript are used to create a simple interfae was also achieved with this program.

# Software Requirements
In order for SimpleUI to operation one must have the following programs running in the background:
- Proxy
- Telemetry

# Configuration
Before you can run the interface you need to create a `simpleui.ini` file.

 1. Navigate to the `Applications/SimpleUI` folder
 2. Create a copy of `simpleui.sample.ini` and rename the new file `simpleui.ini`
 3. Open `simpleui.ini` in a text editor and update the requested information noted by `REPLACEME`

Configuring SimpleUI consists of a few stations for basic use:

* `[SIMPLEUI]` SimpleUI application section
 * `CALLSIGN` Callsign of station to display telemetry from
 * `NODEID` NodeID of station to display telemetry from.
 * `LOCALCALLSIGN` Callsign of Faraday radio connected to the computer from which to send commands
 * `LOCALNODEID` NodeID of Faraday radio connected to the computer from which to send commands
 * `REMOTECALLSIGN` Callsign of Faraday radio to be commanded over RF
 * `REMOTENODEID` NodeID of Faraday radio to be commanded over RF

This configuration file also contains the following:

* `[FLASK]` Flask telemetry server section
 * `HOST` Flask hostname or IP address
 * `PORT` Network port to serve data

* `[PROXY]` Proxy server section
 * `HOST` Flask hostname or IP address
 * `PORT` Network port to serve data

* `[TELEMETRY]` Telemetry server section
 * `HOST` Flask hostname or IP address
 * `PORT` Network port to serve

# Running Simple UI
## Windoews
### Command Line
1. Navigate to SimpleUI folder i.e. `cd C:\git\faradayrf\software\SimpleUI`
2. Open simpleui.py with python `python simpleui.py`

## Viewing  in Browser
Open up your favorite web browser (Firefox and Chrome tested) to view the latest telemetry located at `http://localhost/`

Once open, telemetry is updated at the 500ms intervals and therefore will be limited by the update rate of Faraday which tends to be 1 to 5 second intervals. Below, the local Faraday LEDs are commanded on and off. These are clearly visible and the telemetry indicates their state as well.
[SimpleUI being used](images/simpleuibasic.gif)
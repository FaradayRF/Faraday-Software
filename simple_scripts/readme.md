# Faraday - Simple Scripts
The python scripts provided in this folder offer a concise location for configuring, enabling, and executing various faraday software tools. They also provide great examples of how to interact through the command line interfaces.

These scripts provide a base, _modify them as needed_ to provide the functionality desired.

These scripts currently only open new terminals in Windows. Updates will soon allow this to be cross-platform.

**Scripts Provides**
* `faraday_start.py` - A script to configure and start all hardware operation software
* `faraday_program.py` - A script that uses `faraday-deviceconfiguration` to program the FLASH memory configuration of a Faraday device.

## `faraday_start.py`
This script configures and opens new terminals for each faraday program. Edit the main variables block as needed. Comment out python script code to not configure/open programs as desired.

```python
# Proxy
proxy_unitcnt = 1  # Number of units proxy is connecting to (starts at unit0)
proxy_unit0_callsign = 'REPLACEME'
proxy_unit0_nodeid = REPLACEME
proxy_unit0_port = 'REPLACEME'
#proxy_unit1_callsign = 'REPLACEME'
#proxy_unit1_nodeid = REPLACEME
#proxy_unit1_port = 'REPLACEME'

# APRS
aprs_callsign = 'REPLACEME'

# SIMPLEUI
simpleui_cmdremotecallsign = 'REPLACEME'
simpleui_cmdremotenodeid = REPLACEME
```
## `faraday_program.py`
This script configures and opens new terminals for `faraday-proxy` and `faraday-deviceconfiguration` and programs the FLASH memory configuration of a local faraday device. Unit configuration such as unit callsign/nodeid, boot functionality, and GPS defaults can be programmed into the device.

Edit the main variables block as needed. Comment out python script code to not configure/open programs as desired.

```python
# Proxy
proxy_callsign = 'REPLACEME'
proxy_nodeid = REPLACEME
proxy_port = 'REPLACEME'


# Device Configuration
proxy_unitcnt = 1  # Only program a single unit at a time!
rfbootpower = 20  # MAX = 152
uart_interval = 1  # Seconds
rf_interval = 1  # Seconds
# DEFAULT_LATITUDE MAX LENGTH = 9 Bytes in format "ddmm.mmmm" (including decimal)
default_latitude='0000.0000'
# DEFAULT_LATITUDE_DIRECTION MAX LENGTH = 1 Byte
default_latitude_direction='N'
# DEFAULT_LONGITUDE MAX LENGTH = 10 Bytes in format "dddmm.mmmm" (including decimal)
default_longitude='00000.0000'
# DEFAULT_LONGITUDE_DIRECTION MAX LENGTH = 1 Byte
default_longitude_direction='W'
# DEFAULT_ALTITUDE MAX LENGTH = 8 Bytes (including decimal) in meters
default_altitude='00000.00'
```

### GPS Defaults `DDMM.mmmm` format
The GPS default values to be used (i.e if no GPS present AND GPS is disabled) are saved in `DDMM.mmmm` format as received in NMEA from the GPS unit on Faraday. An example of how to convert from lat/lon to DDMM.mmmm format is below.

```
Location: Los Angeles, CA
Lat = `34.052234`
Lon = `-118.243685`
```
Converting Lat/Lon to `DDMM.mmmm`.
```
DDMM.mmmm Lat (RAW) = `N 34 0.010`
DDMM.mmmm Lon (RAW) = `W 118 26.171`
```

Converting into a valid Faraday configuration:

```
DDMM.mmmm Lat (Faraday) = `3400.0100`
DDMM.mmmm Lat Direction (Faraday) = `N`
DDMM.mmmm Lon (Faraday) = `11826.1710`
DDMM.mmmm Lon Direction (Faraday) = `W`
```

_NOTE: Be aware that the `ddMM` conversion resulted in `3400` not `0340`!_

#### GPS References
* http://www.latlong.net/
* http://www.gpscoordinates.eu/convert-gps-coordinates.php

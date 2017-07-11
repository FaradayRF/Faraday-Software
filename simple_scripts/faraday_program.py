from subprocess import call
import os
import time
import sys

#Detect operating system
#LINUX: Assumed terminal is gnome-terminal standard with Ubuntu
running_os = sys.platform

# Proxy
proxy_callsign = 'REPLACEME'
proxy_nodeid = REPLACEME
proxy_port = 'REPLACEME'


# Device Configuration
proxy_unitcnt = 1  # Only program a single unit at a time!
rfbootpower = 20  # MAX = 152
uart_interval = 5  # Seconds
rf_interval = 20  # Seconds
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

# initialize configurations files
print ("--- INITIALIZING PROXY SERVER ---")
call(['faraday-proxy', '--init-config'])
call(['faraday-proxy', '--unit', str(0), '--callsign', proxy_callsign, '--nodeid', str(proxy_nodeid), '--port', proxy_port])


# initialize configurations files
print ("--- INITIALIZING DEVICE CONFIGURATION SERVER ---")
call(['faraday-deviceconfiguration', '--init-config'])
call(['faraday-deviceconfiguration', '--init-faraday-config'])  # Initialize faraday configuration INI holding program settings

# Basics
call(['faraday-deviceconfiguration', '--proxycallsign', proxy_callsign, '--proxynodeid', str(proxy_nodeid), '--nodeid', str(proxy_nodeid), '--callsign', proxy_callsign])
call(['faraday-deviceconfiguration', '--redledtxon', '--greenledrxon'])

# GPS (NMEA DMM Format)
#call(['faraday-deviceconfiguration', '--gpsbooton', '--gpsenabled'])
call(['faraday-deviceconfiguration', '--gpsbootoff', '--gpsdisabled'])
call(['faraday-deviceconfiguration', '--latitude', default_latitude, '--latitudedir', default_latitude_direction])
call(['faraday-deviceconfiguration', '--longitude', default_longitude, '--longitudedir', default_longitude_direction])
call(['faraday-deviceconfiguration', '--altitude', default_altitude])


# Telemetry
call(['faraday-deviceconfiguration', '--uarttelemetryenabled', '--uartinterval', str(uart_interval)])
call(['faraday-deviceconfiguration', '--rftelemetryenabled', '--rfinterval', str(rf_interval)])

# RF
call(['faraday-deviceconfiguration', '--bootrfpower', str(rfbootpower)])

# Start servers
print ("--- STARTING PROXY SERVER ---")
print type(running_os), running_os == 'linux2'
if running_os == 'win32':
	command = " ".join(['start', 'cmd', '/k', 'faraday-proxy', '--number', str(proxy_unitcnt), '--start'])
elif running_os == 'linux2':
	command = " ".join(['gnome-terminal', '-x', 'faraday-proxy', '--number', str(proxy_unitcnt), '--start'])
os.system(command)  # Not sure how to do this with call()...

print ("--- STARTING DEVICE CONFIGURATION SERVER ---")
if running_os == 'win32':
	command = " ".join(['start', 'cmd', '/k', 'faraday-deviceconfiguration', '--start'])
elif running_os == 'linux2':
	command = " ".join(['gnome-terminal', '-x', 'faraday-deviceconfiguration', '--start'])
os.system(command)  # Not sure how to do this with call()..

time.sleep(3)

print ("--- STARTING SIMPLECONFIG SERVER ---")
if running_os == 'win32':
	command = " ".join(['start', 'cmd', '/k', 'faraday-simpleconfig', '--start'])
elif running_os == 'linux2':
	command = " ".join(['gnome-terminal', '-x', 'faraday-simpleconfig', '--start'])
os.system(command)  # Not sure how to do this with call()..

from subprocess import call
import os
import time
import sys

#Detect operating system
#LINUX: Assumed terminal is gnome-terminal standard with Ubuntu
running_os = sys.platform

# Proxy
proxy_unitcnt = 1  # Number of units proxy is connecting to (starts at unit0)
proxy_unit0_callsign = 'REPLACEME'
proxy_unit0_nodeid = 0
proxy_unit0_port = 'REPLACEME'
#proxy_unit1_callsign = 'REPLACEME'
#proxy_unit1_nodeid = REPLACEME
#proxy_unit1_port = 'REPLACEME'

# APRS
aprs_callsign = 'REPLACEME'

# SIMPLEUI
simpleui_cmdremotecallsign = 'REPLACEME'
simpleui_cmdremotenodeid = 0


# initialize configurations files
print ("--- INITIALIZING PROXY SERVER ---")
call(['faraday-proxy', '--init-config'])
call(['faraday-proxy', '--unit', str(0), '--callsign', proxy_unit0_callsign, '--nodeid', str(proxy_unit0_nodeid), '--port', proxy_unit0_port])
#call(['faraday-proxy', '--unit', str(1), '--callsign', proxy_unit1_callsign, '--nodeid', str(proxy_unit1_nodeid), '--port', proxy_unit1_port])  # Uncomment if second unit

print ("--- INITIALIZING TELEMETRY SERVER ---")
call(['faraday-telemetry', '--init-config'])
call(['faraday-telemetry', '--unit', str(0), '--callsign', proxy_unit0_callsign, '--nodeid', str(proxy_unit0_nodeid)])  # Only a single unit is allowed by telemetry at this time!

print ("--- INITIALIZING APRS SERVER ---")
call(['faraday-aprs', '--init-config'])
call(['faraday-aprs', '--callsign', aprs_callsign])

print ("--- INITIALIZING SIMPLEUI ---")
call(['faraday-simpleui', '--init-config'])
call(['faraday-simpleui', '--callsign', proxy_unit0_callsign, '--nodeid', str(proxy_unit0_nodeid)])
call(['faraday-simpleui', '--cmdlocalcallsign', proxy_unit0_callsign, '--cmdlocalnodeid', str(proxy_unit0_nodeid)])
call(['faraday-simpleui', '--cmdremotecallsign', simpleui_cmdremotecallsign, '--cmdremotenodeid', str(simpleui_cmdremotenodeid)])

# Start servers
print ("--- STARTING PROXY SERVER ---")
if running_os == 'win32':
    command = " ".join(['start', 'cmd', '/k', 'faraday-proxy', '--number', str(proxy_unitcnt), '--start'])
elif running_os == 'linux2':
    command = " ".join(['gnome-terminal', '-x', 'faraday-proxy', '--number', str(proxy_unitcnt), '--start'])
os.system(command)

print ("--- STARTING TELEMETRY SERVER ---")
if running_os == 'win32':
    command = " ".join(['start', 'cmd', '/k', 'faraday-telemetry', '--start'])
elif running_os == 'linux2':
    command = " ".join(['gnome-terminal', '-x', 'faraday-telemetry', '--start'])
os.system(command)

time.sleep(2)  # Sleep time to allow proxy and telemetry to initialize and serve data

print ("--- STARTING APRS SERVER ---")
if running_os == 'win32':
    command = " ".join(['start', 'cmd', '/k', 'faraday-aprs', '--start'])
elif running_os == 'linux2':
    command = " ".join(['gnome-terminal', '-x', 'faraday-aprs', '--start'])
os.system(command)

print ("--- STARTING SIMPLEUI SERVER ---")
if running_os == 'win32':
    command = " ".join(['start', 'cmd', '/k', 'faraday-simpleui', '--start'])
elif running_os == 'linux2':
    command = " ".join(['gnome-terminal', '-x', 'faraday-simpleui', '--start'])
os.system(command)

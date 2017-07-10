from subprocess import call
import os
import time

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


# initialize configurations files
print ("--- INITIALIZING PROXY SERVER ---")
call(['faraday-proxy', '--init-config'])
call(['faraday-proxy', '--unit', str(0), '--callsign', proxy_unit0_callsign, '--nodeid', str(proxy_unit0_nodeid), '--port', proxy_unit0_port])
#call(['faraday-proxy', '--unit', str(1), '--callsign', proxy_unit1_callsign, '--nodeid', str(proxy_unit1_nodeid), '--port', proxy_unit1_port])  # Uncomment if second unit

print ("--- INITIALIZING TELEMETRY SERVER ---")
call(['faraday-telemetry', '--init-config'])
call(['faraday-telemetry', '--unit', str(0), '--callsign', proxy_unit0_callsign, '--nodeid', str(proxy_unit0_nodeid)]) #  Only a single unit is allowed by telemetry at this time!

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
command = " ".join(['start', 'cmd', '/k', 'faraday-proxy', '--number', str(proxy_unitcnt), '--start']) ## Windows ONLY!
os.system(command)  # Not sure how to do this with call()...

print ("--- STARTING TELEMETRY SERVER ---")
command = " ".join(['start', 'cmd', '/k', 'faraday-telemetry', '--start']) ## Windows ONLY!
os.system(command)  # Not sure how to do this with call()...

print ("--- STARTING APRS SERVER ---")
time.sleep(2)  # Sleep time to allow proxy and telemetry to initialize and serve data
command = " ".join(['start', 'cmd', '/k', 'faraday-aprs', '--start']) ## Windows ONLY!
os.system(command)  # Not sure how to do this with call()...

print ("--- STARTING SIMPLEUI SERVER ---")
time.sleep(2)  # Sleep time to allow proxy and telemetry to initialize and serve data
command = " ".join(['start', 'cmd', '/k', 'faraday-simpleui', '--start']) ## Windows ONLY!
os.system(command)  # Not sure how to do this with call()...

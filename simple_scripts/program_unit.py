from subprocess import call
import os
import time

# Proxy
proxy_callsign = 'kb1lqd'
proxy_nodeid = 2
proxy_port = 'COM112'
proxy_unitcnt = 1

# Device Configuration
rfbootpower = 0
uart_interval = 1
rf_interval = 1

# initialize configurations files
print ("--- INITIALIZING PROXY SERVER ---")
call(['faraday-proxy', '--init-config'])
call(['faraday-proxy', '--unit', str(0), '--callsign', proxy_callsign, '--nodeid', str(proxy_nodeid), '--port', proxy_port])


# initialize configurations files
print ("--- INITIALIZING DEVICE CONFIGURATION SERVER ---")
call(['faraday-deviceconfiguration', '--init-config'])
call(['faraday-deviceconfiguration', '--init-faraday-config'])
call(['faraday-deviceconfiguration', '--proxycallsign', proxy_callsign, '--proxynodeid', str(proxy_nodeid), '--nodeid', str(proxy_nodeid), '--callsign', proxy_callsign])
call(['faraday-deviceconfiguration', '--redledtxon', '--greenledrxon'])
call(['faraday-deviceconfiguration', '--gpsbooton', '--gpsenabled'])
call(['faraday-deviceconfiguration', '--uarttelemetryenabled', '--uartinterval', str(uart_interval)])
call(['faraday-deviceconfiguration', '--rftelemetryenabled', '--rfinterval', str(rf_interval)])
call(['faraday-deviceconfiguration', '--bootrfpower', str(rfbootpower)])

# initialize configurations files
#print ("--- INITIALIZING SIMPLECONFIG SERVER ---")
#call(['faraday-simpleconfig', '--init-config'])


# Start servers
print ("--- STARTING PROXY SERVER ---")
command = " ".join(['start', 'cmd', '/k', 'faraday-proxy', '--number', str(proxy_unitcnt), '--start']) ## Windows ONLY!
os.system(command)  # Not sure how to do this with call()...

print ("--- STARTING DEVICE CONFIGURATION SERVER ---")
command = " ".join(['start', 'cmd', '/k', 'faraday-deviceconfiguration', '--start']) ## Windows ONLY!
os.system(command)  # Not sure how to do this with call()..

time.sleep(3)

print ("--- STARTING SIMPLECONFIG SERVER ---")
command = " ".join(['start', 'cmd', '/k', 'faraday-simpleconfig', '--start']) ## Windows ONLY!
os.system(command)  # Not sure how to do this with call()..
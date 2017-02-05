import devicetest
import proxy_settings

import time

#Setup script to use correct proxy unit
devicetest.local_device_callsign = proxy_settings.local_device_callsign
devicetest.local_device_node_id = proxy_settings.local_device_node_id


# MOSFET Test
user_input = ''

try:
    rx_debug = devicetest.GetDebugFlash()
    print "---Current DEBUG Flash Values---"
    for key in rx_debug:
        print key, " = ", rx_debug[key]

except:
    print "Failed to get telemetry packet!"

while user_input != 'q':
    user_input = raw_input('\nHit Enter to RESET Faraday flash DEBUG memory value. Type q to quit.')
    if user_input == '':
        try:
            devicetest.ResetDebugFlash()
            print "Sleeping 3 seconds."
            time.sleep(3)
            rx_debug = devicetest.GetDebugFlash()
            print "---Updated DEBUG Flash Values---"
            for key in rx_debug:
                print key, " = ", rx_debug[key]
        except:
            print "Failed to get telemetry packet!"
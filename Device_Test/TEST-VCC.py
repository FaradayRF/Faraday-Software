import devicetest
import proxy_settings

#Setup script to use correct proxy unit
devicetest.local_device_callsign = proxy_settings.local_device_callsign
devicetest.local_device_node_id = proxy_settings.local_device_node_id

# Constants and sub calculations
refv = float(2.41)
bitv = refv / 2 ** 12

# MOSFET Test
user_input = ''

while user_input != 'q':
    user_input = raw_input('\nHit Enter to retrieve Faraday VCC Voltage telemetry. Type q to quit.')
    if user_input == '':
        try:
            telem = devicetest.GetTelem3()
            vcc = devicetest.ReadVCCTelem(telem)
            if vcc > 0:
                pass
            else:
                vcc = float(0.0)
            print "VCC:", str(vcc)[0:4], "V"
        except:
            print "Failed to get telemetry packet!"

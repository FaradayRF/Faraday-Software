import devicetest
import proxy_settings

#Setup script to use correct proxy unit
devicetest.local_device_callsign = proxy_settings.local_device_callsign
devicetest.local_device_node_id = proxy_settings.local_device_node_id

# MOSFET Test
user_input = ''

while user_input != 'q':
    user_input = raw_input('Type "on" to enable GPIO outputs. Type "off" to disable GPIO outputs. Type q to quit:\n')
    if user_input == 'on':
        print "Activating GPIO!"
        devicetest.EnableGPIO()
    elif user_input == 'off':
        print "Deactivating GPIO!"
        devicetest.DisableGPIO()
    else:
        print "Unknown command..."

import devicetest
import proxy_settings

#Setup script to use correct proxy unit
devicetest.local_device_callsign = proxy_settings.local_device_callsign
devicetest.local_device_node_id = proxy_settings.local_device_node_id

# MOSFET Test
user_input = ''

while user_input != 'q':
    user_input = raw_input('\nHit Enter to retrieve CC430 temperature. Type q to quit.')
    if user_input == '':
        telem = devicetest.GetTelem3()
        temp = devicetest.ReadTelemTemp(telem)
        #print temp

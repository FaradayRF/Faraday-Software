import devicetest
import proxy_settings

#Setup script to use correct proxy unit
devicetest.local_device_callsign = proxy_settings.local_device_callsign
devicetest.local_device_node_id = proxy_settings.local_device_node_id

# ECHO UART Test

status_echo_test = devicetest.TestEchoUart()
print "\n****** Results ******"
print status_echo_test
if status_echo_test['Fails'] <= 0:
    print "All tests PASSED!"
else:
    print "FAILURES DETECTED!"


raw_input("Press Enter to quit")
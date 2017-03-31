import devicetest
import proxy_settings

#Setup script to use correct proxy unit
devicetest.local_device_callsign = proxy_settings.local_device_callsign
devicetest.local_device_node_id = proxy_settings.local_device_node_id

#devicetest.TestGPIOLEDs() # Due to GPS use of LED's and boot sequence just use that.

#status_echo_test = devicetest.TestEchoUart()
#print status_echo_test

# #ResetDebugFlash()
# telem = GetTelem3()
# #print telem
# temp_test = ReadTelemTemp(telem)
#
# print ReadADCTelem(telem)
# print ReadVCCTelem(telem)
# ReadGPSTelem(telem)
# #ResetCONFIGFlash()
#
# #telem = GetTelem3()
# #print telem
#
# #EnableGPIO()
# #time.sleep(5)
# #DisableGPIO()
# #ActiveMOSFETCutdown() # Not working...
# print VerifyIdealDiodeBlock(telem)

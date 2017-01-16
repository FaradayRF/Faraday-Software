import devicetest

devicetest.local_device_callsign = "KB1LQD"
devicetest.local_device_node_id = 1

status_echo_test = devicetest.TestEchoUart()
print status_echo_test


# TestEchoUart()
# #ResetDebugFlash()
# #TestGPIOLEDs()
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

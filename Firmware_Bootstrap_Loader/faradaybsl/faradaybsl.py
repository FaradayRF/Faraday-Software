import createtiscripter
import sys
import subprocess
import os
import faradayftdi

filename = 'RF_Test_Firmware_1-17-17.txt'
comport = 'COM112'

filename = sys.argv[1]
comport = sys.argv[2]



test = createtiscripter.CreateTiBslScript(filename,comport)

test.createscript()

#
#Enable BSL Mode
device_bsl = faradayftdi.FtdiD2xxCbusControlObject()
#
device_bsl.EnableBslMode()
subprocess.call(['faradaybsl/bsl-scripter-windows.exe', 'FaradayFirmwareUpgradeScript.txt'])
device_bsl.DisableBslMode()


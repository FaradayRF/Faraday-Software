from faradaybsl import createtiscripter
import sys
import subprocess
import os
#import Faraday_BSL_FTDI_CBUS

filename = 'RF_Test_Firmware_1-17-17.txt'
comport = 'COM112'

filename = sys.argv[1]
comport = sys.argv[2]

print "Filename:", filename
print "Comport:", comport

test = createtiscripter.CreateTiBslScript(filename,comport)

test.createscript()


#
# #firmware_filename = sys.argv[1]
# firmware_filename = 'RF_Test_Firmware_1-17-17.txt'
# os.system("Create_TI-TXT_Parse.py " + firmware_filename)
#
# #Enable BSL Mode
# device_bsl = Faraday_BSL_FTDI_CBUS.FtdiD2xxCbusControlObject()
#
# device_bsl.EnableBslMode()
# subprocess.call(['bsl-scripter-windows.exe', 'FaradayFirmwareUpgradeScript.txt'])
# device_bsl.DisableBslMode()


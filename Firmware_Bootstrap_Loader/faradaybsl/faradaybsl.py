import createtiscripter
import sys
import subprocess
import faradayftdi

filename = sys.argv[1]
comport = sys.argv[2]


print "FILE:", filename
print "COMM:", comport

test = createtiscripter.CreateTiBslScript(filename,comport)

test.createscript()

#
#Enable BSL Mode
device_bsl = faradayftdi.FtdiD2xxCbusControlObject()
#
device_bsl.EnableBslMode()
subprocess.call(['faradaybsl/bsl-scripter-windows.exe', 'faradaybsl/FaradayFirmwareUpgradeScript.txt'])
device_bsl.DisableBslMode()

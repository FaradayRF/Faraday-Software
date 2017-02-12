from faradaybsl import createtiscripter

filename = 'RF_Test_Firmware_1-17-17.txt'
comport = 'COM112'

test = createtiscripter.CreateTiBslScript(filename,comport)

test.createscript()

from Basic_Proxy_IO import faradaybasicproxyio
from Basic_Proxy_IO import faradaycommands

UARTCMDPORT = 2

#Create faraday IO object
test = faradaybasicproxyio.proxyio()

#Create Faraday command tool object
faraday_cmd_object = faradaycommands.faraday_commands()

#Program frequency
freq = 914.5
command = faraday_cmd_object.CommandUpdateRFFreq(freq)
#test.POST('KB1LQC', 2, UARTCMDPORT, command)

#Get local telem
command = faraday_cmd_object.CommandUARTUpdateNow()
#test.POST('KB1LQC', 2, UARTCMDPORT, command)

#Transmit RF telemetry
command = faraday_cmd_object.CommandRFUpdateNow()
#test.POST('KB1LQC', 2, UARTCMDPORT, command)

#Transmit telem update interval
#command = faraday_cmd_object.CommandUpdateUARTTelemetryInterval(30)
#test.POST('KB1LQC', 2, UARTCMDPORT, command)
#command = faraday_cmd_object.CommandUpdateRFTelemetryInterval(30)
#test.POST('KB1LQC', 2, UARTCMDPORT, command)

#Command a GPIO
command = faraday_cmd_object.CommandGPIOLED1On()
test.POST('KB1LQC', 2, UARTCMDPORT, command)

#Update PA Power
command = faraday_cmd_object.CommandUpdatePATable(50)
test.POST('KB1LQC', 2, UARTCMDPORT, command)

#Device debug flash reset
command = faraday_cmd_object.CommandResetDeviceDebugFlash()
test.POST('KB1LQC', 2, UARTCMDPORT, command)

#Device debug flash telemetry
command = faraday_cmd_object.CommandSendTelemDeviceDebugFlash()

#Debug system settings
command = faraday_cmd_object.CommandSendTelemDeviceSystemSettings()

#HAB cutdown now
command = faraday_cmd_object.CommandHABActivateCutdownEvent()

#HAB reset cutdown timer
command = faraday_cmd_object.CommandHABResetAutoCutdownTimer()

#HAB disable auto-cutdown timer
command = faraday_cmd_object.CommandHABDisableAutoCutdownTimer()

#HAB reset cutdown state machine IDLE
command = faraday_cmd_object.CommandHABResetCutdownIdle()

#Experimental RF Packet Forward
command = faraday_cmd_object.CommandExperimentalRfPacketForward("This is a test")

test.POST('KB1LQC', 2, UARTCMDPORT, command)

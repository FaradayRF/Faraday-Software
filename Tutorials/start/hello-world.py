import os
import sys
import time
sys.path.append(os.path.join(os.path.dirname(__file__), "../../Faraday_Proxy_Tools")) #Append path to common tutorial FaradayIO module

from FaradayIO import faradaybasicproxyio
from FaradayIO import faradaycommands

#Setup a Faraday IO object
faraday_1 = faradaybasicproxyio.proxyio() #default proxy port
faraday_cmd = faradaycommands.faraday_commands()

while(1):
    #Turn LED 1 ON (GREEN)
    print "Turning LED 1 ON"
    command = faraday_cmd.CommandLocalGPIOLED1On()
    faraday_1.POST('REPLACEME', REPLACEME, faraday_1.CMD_UART_PORT, command)
    time.sleep(0.5)

    #Turn LED 1 OFF
    print "Turning LED 1 OFF"
    command = faraday_cmd.CommandLocalGPIOLED1Off()
    faraday_1.POST('REPLACEME', REPLACEME, faraday_1.CMD_UART_PORT, command)
    time.sleep(0.5)

#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Brent
#
# Created:     13/06/2016
# Copyright:   (c) Brent 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import message_application


while(1):
    msg = str(raw_input('Message:'))
    message_application.CreateFrags('kb1lqc', 3, 'kb1lqd', 1, msg)
    #print "Transmitted:", msg
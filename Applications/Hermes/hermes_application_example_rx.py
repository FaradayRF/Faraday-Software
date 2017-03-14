import os
import time
import hermesobject as hermesobject
import ConfigParser

#Open configuration INI
config = ConfigParser.RawConfigParser()
filename = os.path.abspath("hermes.ini")
config.read(filename)

#Definitions

receiver_device_callsign = config.get("DEVICES", "UNIT1CALL") # Should match the programmed callsign of the remote Faraday device to be commanded (receive)
receiver_device_node_id = config.getint("DEVICES", "UNIT1ID") # Should match the programmed callsign of the remote Faraday device to be commanded (receive)
receiver_device_callsign = str(receiver_device_callsign).upper()

# Create messaging unit objects with the two device connected to local proxy
receiver = hermesobject.MessageObject(receiver_device_callsign, receiver_device_node_id)



# # Check Queue receive sizes (should contain no messages)

while 1:
    # sleep to allow buffers to fill and release thread
    time.sleep(.1)

    #Check Queue size of Unit #2 and receive packet (if recieved due to non-ARQ protocol)
    queuesize_unit2 = receiver.receive.getqueuesize()
    if queuesize_unit2 > 0:
        print "\n *** Receiving Message ***"
        #print "Initialized Faraday Messaging Objects"
        #print "Receive Queue Size:", receiver.receive.getqueuesize()
        while receiver.receive.getqueuesize() > 0:
            try:
                received_item = receiver.receive.getqueueitem()
                print "From:", received_item['source_callsign']
                print "Received (Message):", received_item['message']
            except:
                print "No messages received."


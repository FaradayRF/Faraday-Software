import time
import msg_object

#Unit designation constants
# NOTE: Assumes proxy assignment is equal to the real unit programmed callsigns and IDs
unit_1_callsign = 'kb1lqd'
unit_1_callsign_id = 1
unit_2_callsign = 'kb1lqd'
unit_2_callsign_id = 2

# Create messaging unit objects with the two device connected to local proxy
unit_1 = msg_object.MessageObject(unit_1_callsign, unit_1_callsign_id)
unit_2 = msg_object.MessageObject(unit_2_callsign, unit_2_callsign_id)

print "Initialized Faraday Messaging Objects"

# Check Queue receive sizes (should contain no messages)
print "Unit 1 Queue Size:", unit_1.receive.getqueuesize()
print "Unit 2 Queue Size:", unit_2.receive.getqueuesize()

while True:
    print "\n *** Transmit Message ***"
    # Send user input from Unit #1 to Unit #2
    user_input = raw_input("Enter message: ")
    unit_1.transmit.send(unit_2_callsign, unit_2_callsign_id, str(user_input))

    # sleep to allow buffers to fill
    time.sleep(1)

    #Check Queue size of Unit #2 and receive packet (if recieved due to non-ARQ protocol)
    print "\n *** Receiving Message ***"
    queuesize_unit2 = unit_2.receive.getqueuesize()
    if queuesize_unit2 > 0:
        while unit_2.receive.getqueuesize() > 0:
            try:
                print "Unit 2 Queue Size:", unit_2.receive.getqueuesize()
                received_item = unit_2.receive.getqueueitem()
                print "From:", received_item['source_callsign']
                print "Received (Message):", received_item['message']
            except:
                print "No messages received."

#import tx
import threading
import time
import msg_object

#test = tx.transmit_object('KB1LQD', 1)
test_tx = msg_object.transmit_object('kb1lqd', 1)
test2_tx = msg_object.transmit_object('kb1lqd', 2)
test_rx = msg_object.receiver('kb1lqd', 1)
test_rx.start()
test2_rx = msg_object.receiver('kb1lqd', 2)
test2_rx.start()

time.sleep(1)
test_tx.send('kb1lqd', 2, "Hello World!")
time.sleep(0.25)
test2_tx.send('kb1lqd', 1, "Hello World!")
time.sleep(0.25)
test_tx.send('kb1lqd', 2, "Hello World!")
time.sleep(0.25)
test2_tx.send('kb1lqd', 1, "Hello World!")
time.sleep(0.25)
test_tx.send('kb1lqd', 2, "Hello World!")
time.sleep(0.25)
test2_tx.send('kb1lqd', 1, "Hello World!")
time.sleep(0.25)
test_tx.send('kb1lqd', 2, "Hello World!")
time.sleep(0.25)
test2_tx.send('kb1lqd', 1, "Hello World!")
time.sleep(0.25)
test_tx.send('kb1lqd', 2, "Hello World!")
time.sleep(0.25)
test2_tx.send('kb1lqd', 1, "Hello World!")

time.sleep(1)
print "Queue 1:", test_rx.GetQueueSize()
print "Queue 2:", test2_rx.GetQueueSize()



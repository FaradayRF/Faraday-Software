import tx
import threading
import time

test = tx.transmit_object('KB1LQD', 1)
#test2 = tx.transmit_object('KB1LQD', 2)

test.send('kb1lqd', 2, "Hello World!")



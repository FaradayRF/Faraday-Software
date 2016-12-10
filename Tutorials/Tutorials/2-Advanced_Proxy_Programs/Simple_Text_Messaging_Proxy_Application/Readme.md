
# Tutorial - Simple Text Messaging Class Object

The previous tutorial created a simple messaging application that utilized the Faraday  proxy interface and directly coupled a simple user interface. Proper applications should implement a more modular approach by separating the user interface from core application, ideally using a RESTful interface (FLASK). This tutorial presents an example program that utilizes a transmit/receive threaded class object providing a python interface and buffer, a useful step towards a fully FLASK interface!




#Running The Tutorial Example Script

## Start The Proxy Interface

Following the [Configuring Proxy](../../0-Welcome_To_Faraday/Configuring_Proxy/) tutorial configure, start, and ensure a successful connection to **BOTH** locally (USB) connected Faraday digital radios.



## Edit `message_application_example.py` Callsigns and IDs

Edit the example applications callsign and ID numbers with those of your Faraday devices and proxy application assignments.

> NOTE: This application assumes that the proxy assigned callsigns match those of the units. This is usually the case and hopefully in the future dynamic allocation will resolve this potential discrepensy.

The code block below shows the two Faraday devices `KB1LQD-1` and `KB1LQD-2` assigned. The variables are not case sensitive.

```python
#Unit designation constants
# NOTE: Assumes proxy assignent is equal to the real unit programmed callsigns and IDs
unit_1_callsign = 'kb1lqd'
unit_1_callsign_id = 1
unit_2_callsign = 'kb1lqd'
unit_2_callsign_id = 2
```




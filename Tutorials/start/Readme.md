
# Getting Started With Faraday

Thank you for purchasing a Faraday radio! We truly appreciate it. Staying true to open hardware we'd like to congratulate anyone who built up their own too.

**These tutorials and code are a work in progress, we encourage you to help identify and fix issues with us**. Simply create an issue ticket on GitHub or contact us at [Support@FaradayRF.com](mailto:support@faradayrf.com) if you find something wrong or think you can clarify anything.

## Getting Started Overview
 1. This page
 2. [Installing Faraday Software](installing-software.md)
 3. [Connecting Faraday](connecting-hardware.md)
 4. [Configuring Proxy](configuring-proxy.md)
 5. [Configuring Faraday](configuring-faraday.md)
 6. [Starting With Telemetry](telemetrystart.md)
 7. [Turn on The LED's](hello-world.md)
 8. [Configuring RF](configuring-rf-faraday.md)
 9. [RF Playground](rfplayground.md)

## Getting to Know Faraday
We want you to understand some basics about the radio before we move on. Faraday is sectioned off into areas of operation in the image below. Each area performs a necessary function. This design also helps seperate noisy circuits from sensitive ones which improves performance. For example, the ADC inputs are as far as possible from the DC/DC switching converter.

![Faraday Overview](images/RevD1Overview_1200w.jpg)

## Faraday Connectors

### SMA Antenna
Attaching an SMA antenna or SMA cable to Faraday is a simple task. Simply screw the antenna carefully into the SMA connector (P1) with a clockwise rotation. There should be no increase in resistance until the antenna or connector bottoms out. If so, stop and remove antenna to try again carefully.

![SMA Antenna Connector](images/FaradayTop_Ant_LowRes.jpg)

### Micro-USB Connector
Faraday uses a standard Micro-USB connector which means any Micro-USB cable will attach. Some are better than others and a quality USB cable will have shielding that runs the length of the cable. Simply insert the connector as you would any USB connector. Please be mindful of over-stressing the connector solder pads.

![Faraday USB Connection](/images/Faraday_USB_1500w_LowRes.jpg)

### External Power Connector
The external power connector and external MOSFET connectors are adjacent to each other and are the same keying. This means you can connect power to both so **be careful**. P3 (MOSFET) and P4 (External Power) are rotated 180 degrees from each other to help identify them.  We've [tested that no damage will be done](https://github.com/FaradayRF/FaradayRF-Hardware/issues/49) if you do incorrectly connect power thanks to careful design.

Connect your power connector to P4 as shown below. External Power, P4, is located closer to the top of the board.

![Faraday External Power Connector](images/FaradayTop_VCC_MOSFET_2_1500w_LowRes.jpg)

### External MOSFET Connector
This connector operates in exactly the same fashion as the external power connector P4. However, it is an "output" where the on-board MOSFET simply completes the conduction path when commanded. One wire is VCC which can short to anything referenced to Faraday ground.

>**Be careful**! Faraday's MOSFET connection is an [open-drain](https://en.wikipedia.org/wiki/Open_collector#MOSFET) and can used with any power source referenced to and returning power with Faraday's ground connection. There is no requirement to use VCC provided by Faraday, you could use an external battery for MOSFET control and USB power for Faraday. An external power source may be connected between VCC and Ground on P4 to conveniently use the MOSFET but this will power Faraday too. USB Power cannot be sourced externally from this connector.

# Preparing Your Computer
Now that you are aquainted with Faraday let's [get your computer setup](installing-software.md) to run Faraday software.

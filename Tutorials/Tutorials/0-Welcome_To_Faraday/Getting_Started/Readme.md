
# Getting Started With Faraday

Thank you for purchasing a Faraday radio from us. We truely appreciate it! If you did not buy one from FaradayRF and instead built up your own from our hardware files we'd like to say great job!

## Getting Starter Overview
 1. This page
 2. [Installing Faraday Software](installing-software.md)
 3. [Connecting Faraday](connecting-hardware.md)
 4. [Configuring Proxy](/Tutorials/Tutorials/0-Welcome_To_Faraday/Configuring_Proxy)
 5. [turn on the LED's](../../1-Basic_Proxy_Interactions_And_Programming/1-Commanding-Local/Readme.md)

## Getting to Know Faraday
We want you to understand some basics about the radio before we move on. Faraday is sectioned off into areas of operation. Each area performs a necessary function.

![Faraday Overview](images/Faraday_Overview_D1_Boxed_1000px.jpg)

### Orange
Micro USB jack with USB communication and power circuitry

### Red
External power and MOSFET control connectors

### Green
3.3V Switching regulator

### Blue
GPS unit with integrated GPS antenna (if installed)

### Yellow
RF power amplifier, low noise amplifier, SAW filter and SMA antenna jack

### Light Blue
CC430 microcontroller and support circuitry

## Connecting To Faraday

### SMA Antenna
Attaching an SMA antenna or SMA cable to Faraday is a simple task. Simply screw the antenna carefully into the SMA connector (P1) with a clockwise rotation. There should be no increase in resistance until the antenna or connector bottoms out. If so, stop and remove antenna to try again carefully.

![SMA Antenna Connector](FaradayRevBANT_1500w_LowRes.jpg)

### Micro-USB Connector
Faraday uses a standard Micro-USB connector which means any Micro-USB cable will attach. Some are better than others and a quality USB cable will have shielding that runs the length of the cable. Simply insert the connector as you would any USB connector. Please be mindful of over-stressing the connector solder pads.

<Insert Image>

### External Power Connector
The external power connector and external MOSFET connectors are adjacent to each other and are the same keying. This means you can connect power to both so be careful. P3 (MOSFET) and P4(External Power) are 180 degrees rotated from each other to help.  We've [tested that no damage will be done](https://github.com/FaradayRF/FaradayRF-Hardware/issues/49) if you do thanks to careful design.

Connect your power connector to P4 as shown below. External Power, P4, is located closer to the top of the board.

![Faraday External Power Connector](images/FaradayRevBVCC_1500w_LowRes.jpg)

### External MOSFET Connector
This connector operates in exactly the same fashion as the external power connector P3. However, it is an "output" where the on-board MOSFET simply completes the conduction path when commanded. Do not allow these wires to short to ground or other reference points.

# Preparing Your Computer
Now that you are aquainted with Faraday let's [get your computer setup](installing-software.md) to run Faraday software.
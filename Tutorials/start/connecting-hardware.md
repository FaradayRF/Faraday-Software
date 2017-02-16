# Connecting Faraday
In order to configure the software with appropriate information we need to plug Faraday into the USB port and obtain the the port associated with our hardware. *Each Faraday radio will have a different port so these steps apply to any radio being plugged into a computer*.

## Plugging in USB

> The LEDs may blink briefly after plugging Faraday in. This is OK.

 1. Connect Micro-USB cable to Faraday Micro-USB **P16**
 
 Insert Image Here

 2. Connect Micro-USB cable to computer USB port

 Insert Image Here
 
### Windows Drivers
 1. Allow necessary drivers to install from Windows Update, note COM port
 2. If you need to find the COM port of Faraday when plugged in at any time, simply check the *Device Manager* by searching for it in Windows Run.

 ![Device Manager COM Ports](https://faradayrf.com/wp-content/uploads/2017/01/Device-Manager-COMport-1.png)
 
 You will need the COM port to configure the Proxy application.
 
### Linux (Debian-based)
Debian 8 did not need to install any additional drivers when plugging Faraday in. The Following steps will ensure your computer has the correct drivers:

 1. In terminal ```ls /dev/ttyUSB*``` to see what USB serial ports are connected.
 2. Note the displayed filenames. This is the device dev path in Linux. If you have other serial devices plugged in you may want to remove Faraday and run the same command to see which file goes away. Faraday would be the file that disapeared.
 
Faraday will show up as ```/dev/ttyUSB0``` if only one is connected

# Configure Proxy
With the drivers installed and serial port addresses obtained it's time to [configure the Proxy application](configuring-proxy.md) for use.

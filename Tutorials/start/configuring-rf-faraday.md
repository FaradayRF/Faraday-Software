# Configuring Faraday for RF Operation
Congrats on powering through local telemetry viewing and LED commanding with Faraday! Having [configured Faraday](configuring-faraday.imd) for local USB connected use it's time to configure a second Faraday (or any) to transmit RF using `deviceconfiguration` again. By default the configuration disables the RF transmitter. So let's turn it on!

> Remember you need `proxy` properly configured and running to run `deviceconfiguration`.

A base station or remote node could be configured for RF transmissions. Base stations sending out telemetry to the remote nodes or other base stations is useful.

## Faraday Configuration

To program a unit for initial RF operation with default settings, the following values should be updated in `faraday_config.ini`:

 * `CALLSIGN=<Intended Callsign>`
 * `ID=<intended ID>`
 * `BOOT_RF_POWER=20`
 * `RF_TELEMETRY_BOOT_BIT=1`
 * `TELEMETRY_DEFAULT_RF_INTERVAL=10`

We suggest a RF power setting of 20 for desktop use and higher could easily desense the radio causing packets to be missed. RF power of about 140 seems to be the maximum output. Also, please make sure the "Callsign-NodeID" combination is unique for every radio!

A Faraday radio configured for RF use might look like this:

 * `CALLSIGN=KB1LQC`
 * `ID=2`
 * `BOOT_RF_POWER=140`
 * `RF_TELEMETRY_BOOT_BIT=1`
 * `TELEMETRY_DEFAULT_RF_INTERVAL=10`

It is also highly recommended to program default GPS location and altitudes in even if you have a GPS installed. Simply setting them to zero can be a good failsafe

 * `DEFAULT_LATITUDE=0000.0000`
 * `DEFAULT_LONGITUDE=00000.0000`
 * `DEFAULT_ALTITUDE=00000.00`

### Configuration Reference
 Below is a reference of the entire `faraday_config.ini` with an explanation of each setting.

`[BASIC]`
 * `CALLSIGN` Faraday radio callsign (9 characters)
 * `ID` Faraday radio node ID (0-255)
 * `GPIO_P3` Default CC430 P3 IO state, all considered outputs at this time
 * `GPIO_P4` Default CC430 P4 IO state, all considered outputs at this time
 * `GPIO_P5` Default CC430 P5 IO state, all considered outputs at this time

`[RF]`
 * `BOOT_FREQUENCY_MHZ` Faraday radio frequency after a reboot, 914.5 MHz is current default. Range is 902-928MHz
 * `BOOT_RF_POWER` Faraday RF power setting, 152 is maximum however not optimal, 20 is suggested for desktop use to prevent desensing

`[GPS]`
 * `DEFAULT_LATITUDE` Latitude to default to when no GPS is present or is not used
 * `DEFAULT_LATITUDE_DIRECTION` Latitude direction to default to when no GPS is present or is not used
 * `DEFAULT_LONGITUDE` Longitude to default to when no GPS is present or is not used
 * `DEFAULT_LONGITUDE_DIRECTION` Longitude direction to default to when no GPS is present or is not used
 * `DEFAULT_ALTITUDE` Altitude to default to when no GPS is present or is not used
 * `DEFAULT_ALTITUDE_UNITS`Altitude to default to when no GPS is present or is not used
 * `GPS_BOOT_BIT` ON/OFF to allow GPS to turn on at boot
 * `GPS_PRESENT_BIT` Boolean value to inform Faraday whether there is a GPS present or not

`[TELEMETRY]`
 * `UART_TELEMETRY_BOOT_BIT` ON/OFF sending telemetry over UART after boot
 * `RF_TELEMETRY_BOOT_BIT` ON/OFF sending telemetry over RF after boot
 * `TELEMETRY_DEFAULT_UART_INTERVAL` UART telemetry interval (seconds)
 * `TELEMETRY_DEFAULT_RF_INTERVAL` RF telemetry beacon interval (seconds)

## Configuring Hardware

We are almost there! Eventually this will be automated but for now this is what we have. The following steps will start the Device Configuration application server and then send a POST command to it in order to initiate programming. Please ensure Proxy is running prior to these steps.

1. Navigate to `deviceconfiguration` folder in Explorer or terminal
2. Run `deviceconfiguration.py`
  * Windows: double-click on `deviceconfiguration.py`
  * Linux: `python deviceconfiguration.py`
  * Mac OS X: `python deviceconfiguration.py`
3. Run `simpleconfig.py` to send configuration data to Faraday
4. Press `ctrl+c` to exit simpleconfig when complete after reviewing changes
5. Close `deviceconfiguration.py` window

Successful operation of `simpleconfig.py` will print out the Flash contents Faraday is programmed with. After successful programming, the script queries Faraday over UART to send its flash memory contents so we can confirm proper programming.

![Simpleconfig.py output](images/simpleconfig.png)

Note:
 * Some fields such as `BOOT_FREQUENCY_MHZ` and bitmasks return MSP430 specific values which differ from configuration values or bitmasks.

## Proxy Considerations
Once you configure your hardware it will report as the new callsign-nodeid. Proxy will operate regardless of the reported station credentials. We recommended keeping Proxy and all relevant Proxy configurations updated with the latest station credentials. This means your proxy will run just fine after programming even if callsign-nodeid are different and we suggest making the update when convenient.

# Let's Transmit (You probably already are)!
Now that Faraday has been configured to enable RF transmissions and automatically rebooted it is already transmitting at the `TELEMETRY_DEFAULT_RF_INTERVAL` it was programmed to. Let's [play with RF](rfplayground.md)!
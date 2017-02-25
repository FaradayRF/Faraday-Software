# Configuring Faraday for RF Operation

Having [configured Faraday](configuring-faraday.imd) for local USB connected telemetry and LED commanding you are now ready to configure Faraday for RF operation. The default configuration file does not enable the RF transmitter. Now we will enable and configure Faraday to transmit with your FCC Part 97 callsign on the 33cm ham band.

We will again be using the `deviceconfiguration` Application to configure Faraday
The application files are located:

 * `~/Applications/deviceconfiguration`

Proxy and deviceconfiguration should be configured to communicate with the Faraday being programmed. Therefore if you already programmed `KB1LQC-1` and are now programming a second radio `KB1LQC-2` then `proxy.ini` should be updated along with `deviceconfiguration.ini`

> NOTE: Device Configuration using the application tool in this tutorial is currently limited to programming a single device at a time. Also, this process will be automated in the future.

## Device Configuration Setup

First we should ensure the Device Configuration program can communicate with Proxy running in the background. For this we need to edit the `[DEVICES]` section of `deviceconfiguration.ini` to contain the same configuration Proxy is configured with in `proxy.ini`. Update `UNIT0CALL` and `UNIT0ID` to refer to the correct Faraday radio currently attached to Proxy.


## Faraday Configuration

Now you should update `faraday_config.ini` which will be used by `simpleconfig.py` to program Faraday. Simpleconfig will error with relevant information about what is wrong in your configuration if you made a mistake.

To program a unit for initial RF operation with default settings, the following values should be updated:

 * `CALLSIGN=<Intended Callsign>`
 * `ID=<intended ID>`
 * `BOOT_RF_POWER=<Power setting 0-152 (min-max)>`
 * `RF_TELEMETRY_BOOT_BIT=<Set to 1 for automatic RF telemetry transmissions ater boot-up>`
 * `TELEMETRY_DEFAULT_RF_INTERVAL=<Value in seconds for RF telemetry packet transmissions>`

 These are the absolute must-have configured items for RF transmission. We suggest a RF power setting of 20 for desktop use and higher could easily desense the radio causing packets to be missed. RF power of about 140 seems to be maximum output.

 Below is a reference of the entire `faraday_config.ini`. It should be taken into consideration if you would like to power on the GPS or program a default lat/lon.

`[BASIC]`
 * `CALLSIGN` Faraday radio callsign (9 characters)
 * `ID` Faraday radio node ID (0-255)
 * `GPIO_P3` Default CC430 P3 IO state, all considerd outputs at this time
 * `GPIO_P4` Default CC430 P4 IO state, all considerd outputs at this time
 * `GPIO_P5` Default CC430 P5 IO state, all considerd outputs at this time

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
3. Run `simpleconfig.py` to send configuration data to Faraday
4. Press `ctrl+c` to exit simpleconfig when complete after reviewing changes
5. Close `deviceconfiguration.py` window

Successful operation of `simpleconfig.py` will print out the Flash contents Faraday is programmed with. After successful programming the script queries Faraday over UART to send its Flash contents so we can confirm proper programming.

![Simpleconfig.py output](images/simpleconfig.png)

Note:
 * Some fields such as `BOOT_FREQUENCY_MHZ` and bitmasks return MSP430 specific values which differ from configuration values or bitmasks.

## Proxy Considerations
Once you configure your hardware it will report as the new callsign-nodeid. Proxy will operate regardless of the reported station credentials. We recommended keeping Proxy and all relevant Proxy configurations updated with the latest station credentials. This means your proxy will run just fine after programming even if callsign-nodeid are different and we suggest making the update when convenient.

# Using RF Telemetry

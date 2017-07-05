# Configuring Faraday for RF Operation
Congrats on powering through local telemetry viewing and LED commanding with Faraday! It's time to configure a second Faraday (or any) to transmit RF using `faraday-deviceconfiguration` again. By default the configuration disables the RF transmitter. So let's turn it on!

> Remember you need `faraday-proxy` properly configured and running

A base station or remote node could be configured for RF transmissions. Base stations sending out telemetry to the remote nodes or other base stations is useful.

## Faraday RF Configuration

To enable RF we program faraday with the standard [configuration](configuring-faraday.md) settings and add a few additional options. Below is an example for configuring `KB1LQC-2` for RF transmissions:

> All Faraday radios must have unique callsign-nodeid configurations!

```
faraday-deviceconfiguration --proxycallsign kb1lqc --proxynodeid 2 --callsign kb1lqc --nodeid 10 --rftelemetryenabled --rfinterval 2 --start
```

* `--rftelemetryenabled`: Enable RF telemetry transmissions.
* `--rfinterval RFINTERVAL`: Transmission interval in seconds (default 2 seconds).

If proxy callsign and nodeid are already configured for `faraday-deviceconfiguration` then those commands could be ommitted.

Additional options for RF operation include
* `--rftelemetrydisabled`: Disable RF telemetry transmissions.
* `--bootfrequency BOOTFREQUENCY`: Floating point transmission frequency in MHz.
* `--bootrrpower BOOTRFPOWER`: RF Power from 0 to 142. Default setting is 20.
* `--redledtxon`: Enable the red LED when RF Transmitted.
* `--redledtxoff`: Disable the red LED when RF Transmitted.

We suggest a RF power setting of 20 for desktop use and higher could easily desense the radio causing packets to be missed. RF power of about 140 seems to be the maximum output. Also, please make sure the "Callsign-NodeID" combination is unique for every radio!

## Configuring Hardware
Hardware is configured for RF use the same way we programmed the USB connected Faraday radio. With `faraday-proxy` running you must start the `faraday-deviceconfiguration` server with appropriate configuration settings and then kick-off the configuration with `faraday-simpleconfig`. Remember you can query the current configuration of the CC430 hardware with `faraday-simpleconfig --read`

Lastly, remember to include the `--start` option when running `faraday-deviceconfiguration`!

## Proxy Considerations
Once you configure your hardware it will report as the new callsign-nodeid. Proxy will operate regardless of the reported station credentials. We recommended keeping Proxy and all relevant Proxy configurations updated with the latest station credentials. This means your proxy will run just fine after programming even if callsign-nodeid are different and we suggest making the update when convenient.

# Let's Transmit (You probably already are)!
Now that Faraday has been configured to enable RF transmissions and automatically rebooted it is already transmitting at the `TELEMETRY_DEFAULT_RF_INTERVAL` it was programmed to. Let's [play with RF](rfplayground.md)!

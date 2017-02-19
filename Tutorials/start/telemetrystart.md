#Starting With Telemetry

Now that Faraday is configured and we know Proxy is running well we can view telemetry directly in the web browser for a quick diagnostic that everything is well. Also, if you're like us at FaradayRF we think data can be beautiful :) The [Telemetry](../../Applications/Telemetry) application is located in `Applications/Telemetry` is a Flask-based server application which saves data to a SQLite database. It then exposes a RESTful API to query the database.

Since [Telemetry](../../Applications/Telemetry) responds with JSON data we could use a web browser to print it to the screen, Python to interact with it, or an application specific to HTTP communications to interact.

## Configuring & Running Telemetry

The configuration guide in [Telemetry](../../Applications/Telemetry) documentation sums up how to get the application up and running. We suggest you head over to that documentation to step through configuration. Once setup, play around with the example queries using your web browser located on the bottom of the documentation. Report back here when complete!

When you are querying the [Telemetry](../../Applications/Telemetry) application you will see data printed directly to your web browser. Reloading the webpage will perform the query again and update the information on the screen. This is a handy way to quickly debug applications as you develop them!

![Telemetry output in web browser](images/WebBrowser_FullOutput.exe.png)

# Moving Forward
Now that you are obtaining telemetry from your Faraday radio it is time to command it. Turn on the LED in our [Hello World](hello-world.md) guide!
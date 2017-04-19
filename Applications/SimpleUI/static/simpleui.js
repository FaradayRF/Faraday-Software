function getTelemetry(){
    // Performs a request for data from the Faraday Telemetry application
    // followed by some local scaling and manipulation of values prior to
    // using JQuery to place updated values onto the webpage

    try{
        

        // Build URL for Telemetry db query, then retrieve data
        var url = "http://localhost:8001/?limit=1&callsign=" +
            callsign + // jshint ignore:line
            "&nodeid=" + 
            nodeid; // jshint ignore:line
            $.getJSON(url,function(data){
                try{
                    // Convert EPOCH from telemetry into date object
                    var epoch = data[0].EPOCH;
                    var d = new Date(0);
                    d.setUTCSeconds(epoch);
                    $(".EPOCH").text(d);

                    // Populate the GPS section
                    $(".CALLSIGN").text(data[0].SOURCECALLSIGN);
                    $(".NODEID").text(data[0].SOURCEID);
                    $(".GPSLATITUDE").text(data[0].GPSLATITUDE);
                    $(".GPSLATITUDEDIR").text(data[0].GPSLATITUDEDIR);
                    $(".GPSLONGITUDE").text(data[0].GPSLONGITUDE);
                    $(".GPSLONGITUDEDIR").text(data[0].GPSLONGITUDEDIR);
                    $(".ALTITUDE").text(data[0].GPSALTITUDE);
                    $(".SPEED").text(Math.round(data[0].GPSSPEED*0.514444*100)/100);
                    $(".GPSFIX").text(data[0].GPSFIX);

                    // Populate the ADC section
                    $(".BOARDTEMP").text(data[0].BOARDTEMP);
                    $(".ADC0").text(Math.round(data[0].ADC0*1000*(2.41/4096))/1000);
                    $(".ADC1").text(Math.round(data[0].ADC1*1000*(2.41/4096))/1000);
                    $(".ADC2").text(Math.round(data[0].ADC2*1000*(2.41/4096))/1000);
                    $(".ADC3").text(Math.round(data[0].ADC3*1000*(2.41/4096))/1000);
                    $(".ADC4").text(Math.round(data[0].ADC4*1000*(2.41/4096))/1000);
                    $(".ADC5").text(Math.round(data[0].ADC5*1000*(2.41/4096))/1000);

                    // Populate the High Altitude Balloon section
                    $(".HABTIMER").text(data[0].HABTIMER);
                    $(".HABTIMERSTATE").text(data[0].HABTIMERSTATE);
                    $(".HABTRIGGERTIME").text(data[0].HABTRIGGERTIME);
                    $(".HABCUTDOWNSTATE").text(data[0].HABCUTDOWNSTATE);

                    // Convert GPIO data into an array of GPIO values
                    var gpio = [];
                    gpio = ("000000000" + data[0].GPIOSTATE.toString(2)).substr(-8).split("");

                    // Convert IOSTATE data into array of binary values
                    var iostate = [];
                    iostate = ("000000000" + data[0].IOSTATE.toString(2)).substr(-8).split("");
                    iostate.reverse();

                    // Convert RFSTATE data to an array of values
                    var rfstate = [];
                    rfstate = ("000000000" + data[0].RFSTATE.toString(2)).substr(-8).split("");
                    rfstate.reverse();

                    // Populate GPIO data in IO section
                    $(".GPIO0").text(gpio[0]);
                    $(".GPIO1").text(gpio[1]);
                    $(".GPIO2").text(gpio[2]);
                    $(".GPIO3").text(gpio[3]);
                    $(".GPIO4").text(gpio[4]);
                    $(".GPIO5").text(gpio[5]);
                    $(".GPIO6").text(gpio[6]);
                    $(".GPIO7").text(gpio[7]);
                    $(".GPIO8").text(iostate[7]);

                    // Populate LED and button IO section
                    $(".LED2").text(iostate[3]);
                    $(".LED1").text(iostate[4]);
                    $(".BUTTON").text(iostate[0]);

                    // Populate RF data from IO section
                    $(".PAENABLE").text(rfstate[7]);
                    $(".LNAENABLE").text(rfstate[5]);
                    $(".HGMSELECT").text(rfstate[3]);

                    // Populate IOSTATE data in IO section
                    $(".GPSSTANDBY").text(iostate[1]);
                    $(".GPSRESET").text(iostate[2]);
                    $(".MOSFET").text(iostate[5]);

                    }
                    catch(err){
                        $(".warning").text(callsign + "-" + nodeid + " not found!");// jshint ignore:line
                    }
            }).fail(function(){
                console.log("Error");
                });
    }
    catch(err){
        console.log(err);
    }
}

/*jshint browser: true */
// Perform telemetry update periodically (time in ms)
setInterval(function(){ getTelemetry(); }, 1000);

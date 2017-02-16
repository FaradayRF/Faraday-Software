//Global Variables
var stationList = [];

function getLocalTelemetry(){
	$.ajax({url: "faraday/5/telemetry", success: function test(result){
		if(result){
			telemData = JSON.parse(result);
			updateTelemetryUI(telemData);
		}
	}});
};

function getStations(){
	$.ajax({url: "faraday/stations", success: function test(result){
		if(result){
			var stations = JSON.parse(result);
			//Do something here with station data JSON object
			//getScaling(stations);
			displayStations(stations);
		}
	}});
};

/* function getScaling(stations){
	$.each(stations,function(index, element){
		$.ajax({
				url: "faraday/scaling",
				data: {callsign: element.callsign, nodeid: element.id},
				success: function test(result){
					var scaling = JSON.parse(result);
					console.log(scaling);
			}});
		});
}; */

function checkStations(){
	$.ajax({url: "faraday/stations", success: function test(result){
		if(result){
			var stations = JSON.parse(result);
			//Do something here with station data JSON object
			updateStations(stations);
			
		}
	}});
}

//$("li#" + nodeKey).remove(); //remove from list
// $('ul#stations li.dropdown') to find all UL listed stations
// this needs work. I can't figure out tonight how to actually remove this cleanly.
function removeStations(stations){
	var stationListCopy = stationList.slice(0);
	var stationListCurrent = [];
	$.each(stations,function(index,element){
		stationListCurrent.push(element.callsign + element.id);
	});
	$.each(stationListCurrent,function(index,element){
		result = stationListCopy.indexOf(element);
		if(result >= 0){
			stationListCopy.splice(result);
		}
	});
	// The remaining items in the log are old
	$.each(stationListCopy,function(index,element){
		console.log("Removing Stale Station Data");
		//Remove station from stationlist sidebar
		$("li#" + element).remove();
		// Remove div content for station
		$("#basic-" + element).remove();
		$("#telemetry-" + element).remove();
		$("#messages-" + element).remove();
		$("#command-" + element).remove();
		$("#config-" + element).remove();
		$("#debug-" + element).remove();
		result = stationList.indexOf(element);
		stationList.splice(result,1); // remove station from global list
	});
	//stationListCopy = [];
	//console.log("new: " + stationListCopy);
	}


function updateStations(stations){
	$.each(stations,function(index, element){
		console.log(stationList);
		console.log("Updating data for " + element.callsign + "-" + element.id);
		//Add station to global list of stations... should eventually remove them as they get stale
		if(stationList.indexOf(element.callsign + element.id) < 0){
			stationList.push(element.callsign + element.id);
			$.ajax({
				url: "faraday/telemetry",
				data: {callsign: element.callsign, nodeid: element.id, limit: 1},
				success: function test(result){
					node = JSON.parse(result);
					addStation(node[0]);
			}});
		}
		try{
			updateStationData(element.callsign,element.id,index, 1);
			removeStations(stations);
		}
		catch(err){
			console.log("Error loading station data!");
		}
	});
}

function updateStationData(callsign,nodeid,index, limit){
	$.ajax({
				url: "faraday/telemetry",
				data: {callsign: callsign, nodeid: nodeid, limit: limit},
				success: function test(result){
					result = JSON.parse(result);
					//console.log(result);
					rawTelemetry = result[0];
					scaledTelemetry = result[1];
					debugTelemetry = result[2];
					systemTelemetry = result[3];
					var nodeKey = callsign + nodeid;
					var nodeTime = proxyEpochConverter(rawTelemetry.apepoch);
					var currentDate = new Date();
					var diff = Math.round((currentDate - nodeTime)/1000);
					var rtcTime = rtcConverter(rawTelemetry);
					
					// GPIO conversions
					gpio0Array = dec2bin8(node.gpio0);
					gpio1Array = dec2bin8(node.gpio1);// ****OK doesn't actually change with GPIO buton input changes...*****
					gpio2Array = dec2bin8(node.gpio2);
					
					$("#rtctime-" + nodeKey).html(rtcTime);
					$("#aptime-" + nodeKey).html(nodeTime);
					$("#boardtemp-" + nodeKey).html(Math.round(scaledTelemetry.adc7scaled));
					$("#diff-" + nodeKey).html(diff);
					$("#gpsfix-" + nodeKey).html(rawTelemetry.gpsfix);
					$("#latdeg-" + nodeKey).html(rawTelemetry.latdeg);
					$("#latdec-" + nodeKey).html(rawTelemetry.latdec);
					$("#latdir-" + nodeKey).html(rawTelemetry.latdir);
					$("#londeg-" + nodeKey).html(rawTelemetry.londeg);
					$("#londec-" + nodeKey).html(rawTelemetry.londec);
					$("#londir-" + nodeKey).html(rawTelemetry.londir);
					$("#altitude-" + nodeKey).html(rawTelemetry.altitude);
					$("#speed-" + nodeKey).html(rawTelemetry.speed);
					//don't do this math here...
					$("#vcc-" + nodeKey).html(Math.round(scaledTelemetry.adc6scaled*1000)/1000);
					// possibly want to add battery voltage and temp on basic info
					//Debug Telemetry
					$("#bootcount-" + nodeKey).html(debugTelemetry.bootcount);
					$("#resetcount-" + nodeKey).html(debugTelemetry.resetcount);
					$("#bor-" + nodeKey).html(debugTelemetry.bor);
					$("#rstnmi-" + nodeKey).html(debugTelemetry.rstnmi);
					$("#svsl-" + nodeKey).html(debugTelemetry.svsl);
					$("#svsh-" + nodeKey).html(debugTelemetry.svsh);
					$("#svmlovp-" + nodeKey).html(debugTelemetry.svmlovp);
					$("#svmhovp-" + nodeKey).html(debugTelemetry.svmhovp);
					$("#wdtto-" + nodeKey).html(debugTelemetry.wdtto);
					$("#flashkeyviolation-" + nodeKey).html(debugTelemetry.flashkeyviolation);
					$("#fllunlock-" + nodeKey).html(debugTelemetry.fllunlock);
					$("#peripheralconfigcnt-" + nodeKey).html(debugTelemetry.peripheralconfigcnt);
					$("#accessviolation-" + nodeKey).html(debugTelemetry.accessviolation);
					
					//System Telemetry
					$("#rffreq0-" + nodeKey).html(systemTelemetry.rffreq0);
					$("#rffreq1-" + nodeKey).html(systemTelemetry.rffreq1);
					$("#rffreq2-" + nodeKey).html(systemTelemetry.rffreq2);
					$("#rfpwr-" + nodeKey).html(systemTelemetry.rfpwr);
					$("#uChar_auto_cutdown_timer_state_status-" + nodeKey).html(rawTelemetry.uChar_auto_cutdown_timer_state_status);
					$("#uChar_cutdown_event_state_status-" + nodeKey).html(rawTelemetry.uChar_cutdown_event_state_status);
					$("#uInt_timer_set-" + nodeKey).html(rawTelemetry.uInt_timer_set);
					$("#uInt_timer_current-" + nodeKey).html(rawTelemetry.uInt_timer_current);
					
					var remote_location;
					var local_location;
					var distance;
					var rel_direction;
					
					local_location = DD2DDeg(rawTelemetry.aplatdeg, rawTelemetry.aplatdec, rawTelemetry.aplatdir, rawTelemetry.aplondeg, rawTelemetry.aplondec, rawTelemetry.aplondir);
					var locNodeGeoJSON = createGEOJSONLocation(local_location,rawTelemetry.apaltitude,rawTelemetry.apcallsign + rawTelemetry.apid);
					remote_location = DD2DDeg(rawTelemetry.latdeg, rawTelemetry.latdec, rawTelemetry.latdir, rawTelemetry.londeg, rawTelemetry.londec, rawTelemetry.londir);
					var remNodeGeoJSON = createGEOJSONLocation(remote_location,rawTelemetry.altitude,nodeKey);
					
					var nodeRelPos = relativePosition(locNodeGeoJSON,remNodeGeoJSON);
					var horizon = calculateHorizon(remNodeGeoJSON);
					
					$("#location-" + nodeKey).html(remote_location[0] + remote_location[1] + " " + remote_location[2] + remote_location[3]);
					$("#hab-gps-altitude-" + nodeKey).html(rawTelemetry.altitude + " Meters");
					$("#hab-gps-speed-" + nodeKey).html(knots2MetersPerSec(rawTelemetry.speed) + " m/s");
					$("#hab-distance-" + nodeKey).html(nodeRelPos[0] + " km");
					$("#hab-rel-bearing-" + nodeKey).html(nodeRelPos[1] + " Degrees");
					$("#hab-rel-elevation-" + nodeKey).html(nodeRelPos[2] + " Degrees");
					$("#hab-rem-horizon-" + nodeKey).html(horizon + " km");

					
					
					/*
					$("#debug-table-" + nodeKey).append('<tr>' + '<td>RF Frequency 0</td><td><span id="rffreq0-' + nodeKey + '"></span></td>' + '</tr>');
				$("#debug-table-" + nodeKey).append('<tr>' + '<td>RF Frequency 1</td><td><span id="rffreq1-' + nodeKey + '"></span></td>' + '</tr>');
				$("#debug-table-" + nodeKey).append('<tr>' + '<td>RF Frequency 2</td><td><span id="rffreq2-' + nodeKey + '"></span></td>' + '</tr>');
				$("#debug-table-" + nodeKey).append('<tr>' + '<td>RF Power</td><td><span id="rfpwr-' + nodeKey + '"></span></td>' + '</tr>');
				$("#debug-table-" + nodeKey).append('<tr>' + '<td>Boot Count</td><td><span id="bootcount-' + nodeKey + '"></span></td>' + '</tr>');
				$("#debug-table-" + nodeKey).append('<tr>' + '<td>Reset Count</td><td><span id="resetcount-' + nodeKey + '"></span></td>' + '</tr>');
				$("#debug-table-" + nodeKey).append('<tr>' + '<td>Brownout Reset Count</td><td><span id="bor-' + nodeKey + '"></span></td>' + '</tr>');
				$("#debug-table-" + nodeKey).append('<tr>' + '<td>Reset Interrupt Count</td><td><span id="rstnmi-' + nodeKey + '"></span></td>' + '</tr>');
				$("#debug-table-" + nodeKey).append('<tr>' + '<td>Supervisor Low Count</td><td><span id="svsl-' + nodeKey + '"></span></td>' + '</tr>');
				$("#debug-table-" + nodeKey).append('<tr>' + '<td>Supervisor High Count</td><td><span id="svsh-' + nodeKey + '"></span></td>' + '</tr>');
				$("#debug-table-" + nodeKey).append('<tr>' + '<td>Supervisor Low OVP Count</td><td><span id="svslovp-' + nodeKey + '"></span></td>' + '</tr>');
				$("#debug-table-" + nodeKey).append('<tr>' + '<td>Supervisor High OVP Count</td><td><span id="svshovp-' + nodeKey + '"></span></td>' + '</tr>');
				$("#debug-table-" + nodeKey).append('<tr>' + '<td>Watchdog Timeout Count</td><td><span id="wdtto-' + nodeKey + '"></span></td>' + '</tr>');
				$("#debug-table-" + nodeKey).append('<tr>' + '<td>Flash Key Violation Count</td><td><span id="flashkeyviolation-' + nodeKey + '"></span></td>' + '</tr>');
				$("#debug-table-" + nodeKey).append('<tr>' + '<td>FLL Unlock Count</td><td><span id="fllunlock-' + nodeKey + '"></span></td>' + '</tr>');
				$("#debug-table-" + nodeKey).append('<tr>' + '<td>Peripheral Config Count</td><td><span id="peripheralconfig-' + nodeKey + '"></span></td>' + '</tr>');
				$("#debug-table-" + nodeKey).append('<tr>' + '<td>Access Violation Count</td><td><span id="accessviolation-' + nodeKey + '"></span></td>' + '</tr>');
					*/
					// Plot ADC and GPIO data instead of listing it on a page
					updateCharts(rawTelemetry, scaledTelemetry);
					
					
	}});
}

function updateCharts(rawTelemetry, scaledTelemetry){
	nodeKey = rawTelemetry.callsign + rawTelemetry.id
	time = new Date(rawTelemetry.apepoch*1000);
	//timeString = time.getMonth() + "-" + time.getDate() + "-" + time.getFullYear() + " " + time.getHours() + ":" + time.getMinutes() + ":" + time.getSeconds();
	hours = ("0" + time.getHours()).slice(-2);
	mins = ("0" + time.getMinutes()).slice(-2);
	secs = ("0" + time.getSeconds()).slice(-2);
	timeString = hours + ":" + mins + ":" + secs;
	//console.log(((new Date).getTime()/1000)-(new Date(rawTelemetry.apepoch).getTime()));
	if (((new Date).getTime()/1000)-(new Date(rawTelemetry.apepoch).getTime()) < 10){
		for (i=0; i <= 8; i++){
			try{
				window['adc' + i + 'Graph' + nodeKey].config.options.animation = false;
				window['adc' + i + 'Graph' + nodeKey].data.datasets[0].data.push(scaledTelemetry["adc" + i + "scaled"]);
				window['adc' + i + 'Graph' + nodeKey].data.labels.push(timeString);
				window['adc' + i + 'Graph' + nodeKey].chart.config.data.datasets[0].pointBackgroundColor.push('#28B463');
				if (window['adc' + i + 'Graph' + nodeKey].data.datasets[0].data.length >=60){
					window['adc' + i + 'Graph' + nodeKey].data.datasets[0].data.shift();
					window['adc' + i + 'Graph' + nodeKey].data.labels.shift();
					window['adc' + i + 'Graph' + nodeKey].chart.config.data.datasets[0].pointBackgroundColor.shift();
				}
				
				window['adc' + i + 'Graph' + nodeKey].update();
			}
			catch(err){
				console.log("ADC graphing error " + nodeKey + ": " + err);
			}
		}
		
		for (i=0; i <= 2; i++){
			try{
				window['gpio' + i + 'Graph' + nodeKey].config.options.animation = false;
				window['gpio' + i + 'Graph' + nodeKey].data.datasets[0].data.push(rawTelemetry["gpio" + i]);
				window['gpio' + i + 'Graph' + nodeKey].chart.config.data.datasets[0].pointBackgroundColor.push('#28B463');
				window['gpio' + i + 'Graph' + nodeKey].data.labels.push(timeString);
				if (window['gpio' + i + 'Graph' + nodeKey].data.datasets[0].data.length >=60){
					window['gpio' + i + 'Graph' + nodeKey].data.datasets[0].data.shift();
					window['gpio' + i + 'Graph' + nodeKey].data.labels.shift();
					window['gpio' + i + 'Graph' + nodeKey].chart.config.data.datasets[0].pointBackgroundColor.shift();
				}
				window['gpio' + i + 'Graph' + nodeKey].update();
			}
			catch(err){
				console.log("GPIO graphing error " + nodeKey + ": " + err);
			}
		}
	} else {
		// Change color of points onto the graph if older than 10 seconds to indicate stale data
		for (i=0; i <= 8; i++){
			try{
				window['adc' + i + 'Graph' + nodeKey].config.options.animation = false;
				//myLineChart.datasets[0].points[4].fillColor =  "#FF0000";
				//window['adc' + i + 'Graph' + nodeKey].data.datasets[0].data.push(null);
				window['adc' + i + 'Graph' + nodeKey].data.datasets[0].data.push(scaledTelemetry["adc" + i + "scaled"]);
				//console.log(window['adc' + i + 'Graph' + nodeKey].chart.config.options.elements.point);
				window['adc' + i + 'Graph' + nodeKey].chart.config.data.datasets[0].pointBackgroundColor.push('#FF0000');
				window['adc' + i + 'Graph' + nodeKey].data.labels.push(timeString);
				
				if (window['adc' + i + 'Graph' + nodeKey].data.datasets[0].data.length >=60){
					window['adc' + i + 'Graph' + nodeKey].data.datasets[0].data.shift();
					window['adc' + i + 'Graph' + nodeKey].data.labels.shift();
					window['adc' + i + 'Graph' + nodeKey].chart.config.data.datasets[0].pointBackgroundColor.shift();
				}
				window['adc' + i + 'Graph' + nodeKey].update();
			}
			catch(err){
				console.log("ADC graphing error " + nodeKey + ": " + err);
			}
		}
		
		for (i=0; i <= 2; i++){
			try{
				//window['gpio' + i + 'Graph' + nodeKey].config.options.animation = false;
				window['gpio' + i + 'Graph' + nodeKey].data.datasets[0].data.push(rawTelemetry["gpio" + i]);
				window['gpio' + i + 'Graph' + nodeKey].chart.config.data.datasets[0].pointBackgroundColor.push('#FF0000');
				window['gpio' + i + 'Graph' + nodeKey].data.labels.push(timeString);
				if (window['gpio' + i + 'Graph' + nodeKey].data.datasets[0].data.length >=60){
					window['gpio' + i + 'Graph' + nodeKey].data.datasets[0].data.shift();
					window['gpio' + i + 'Graph' + nodeKey].data.labels.shift();
					window['gpio' + i + 'Graph' + nodeKey].chart.config.data.datasets[0].pointBackgroundColor.shift();
				}
				window['gpio' + i + 'Graph' + nodeKey].update();
			}
			catch(err){
				console.log("GPIO graphing error " + nodeKey + ": " + err);
			}
		}
	}	
}


function displayStations(stations){
	$.each(stations,function(index, element){
		
		//Get station data here before displaying
		getStationData(element.callsign,element.id,index);
		/* //Create chart.js charts (move?)
		console.log("Creating initial plot data: " + element.callsign + "-" + element.id);
		getPlotData(element.callsign,element.id,60,0,0); */
	});
}

function addStation(node){
	getStationData(node.callsign,node.id,1);
}
function createBasicTab(callsign,nodeid,index){
	
}
function getStationData(callsign,nodeid,index){
		$.ajax({
				url: "faraday/telemetry",
				data: {callsign: callsign, nodeid: nodeid, limit: 1},
				success: function test(result){
		if(result){
			console.log("Creating HTML for " + callsign + "-" + nodeid);
			var stations = JSON.parse(result);
			node = stations[0]
			//Do something here with station data JSON object
			//Add station to global list of stations... should eventually remove them as they get stale
			if(stationList.indexOf(node.callsign + node.id) < 0){
				stationList.push(node.callsign + node.id);
				//addStation(node);
				console.log(stationList);
			}
			var nodeKey = node.callsign + node.id;
			var nodeText = node.callsign + '-' + node.id;

//col-xs-2
		if(index == 0){
			$("#stations").append('<li class="active dropdown" id="' + nodeKey + '"></li>');
			$("li#" + nodeKey).append('<a class="dropdown-toggle" data-toggle="dropdown" href="#"' +  'id="' + nodeKey + '">' + node.callsign + '-' + node.id + '</a>');
			$("li#" + nodeKey).append('<ul class="dropdown-menu" id="' + nodeKey + '"></ul>');
			$("ul#" + nodeKey).append('<li><a href="#basic-' + nodeKey + '" data-toggle="tab"><span class="glyphicon glyphicon-th"></span> Basic Info</a></li>');
			$("ul#" + nodeKey).append('<li><a href="#telemetry-' + nodeKey + '" data-toggle="tab"><span class="glyphicon glyphicon-globe"></span> Telemetry</a></li>');
			$("ul#" + nodeKey).append('<li><a href="#messages-' + nodeKey + '" data-toggle="tab"><span class="glyphicon glyphicon-pencil"></span> Messages</a></li>');
			$("ul#" + nodeKey).append('<li><a href="#command-' + nodeKey + '" data-toggle="tab"><span class="glyphicon glyphicon-log-in"></span> Command</a></li>');
			$("ul#" + nodeKey).append('<li><a href="#config-' + nodeKey + '" data-toggle="tab"><span class="glyphicon glyphicon-wrench"></span> Config</a></li>');
			$("ul#" + nodeKey).append('<li><a href="#missions-' + nodeKey + '" data-toggle="tab"><span class="glyphicon glyphicon-plane"></span> Missions</a></li>');
			$("ul#" + nodeKey).append('<li><a href="#debug-' + nodeKey + '" data-toggle="tab"><span class="glyphicon glyphicon-cog"></span> Debug</a></li>');
			
			
			if(node.aprf == 0){
				$("a#" + nodeKey).append(' | <span class="glyphicon glyphicon-home"></span>');
			} else {
				$("a#" + nodeKey).append(' | <span class="glyphicon glyphicon-signal"></span>');
			}
			$(".tab-content").append('<div id="basic-' + nodeKey + '" class="tab-pane fade in active"></div>');
		} else {
			$("#stations").append('<li class="dropdown" id="' + nodeKey + '"></li>');
			$("li#" + nodeKey).append('<a class="dropdown-toggle" data-toggle="dropdown" href="#"' +  'id="' + nodeKey + '">' + node.callsign + '-' + node.id + '</a>');
			$("li#" + nodeKey).append('<ul class="dropdown-menu" id="' + nodeKey + '"></ul>');
			$("ul#" + nodeKey).append('<li><a href="#basic-' + nodeKey + '" data-toggle="tab"><span class="glyphicon glyphicon-th"></span> Basic Info</a></li>');
			$("ul#" + nodeKey).append('<li><a href="#telemetry-' + nodeKey + '" data-toggle="tab"><span class="glyphicon glyphicon-globe"></span> Telemetry</a></li>');
			$("ul#" + nodeKey).append('<li><a href="#messages-' + nodeKey + '" data-toggle="tab"><span class="glyphicon glyphicon-pencil"></span> Messages</a></li>');
			$("ul#" + nodeKey).append('<li><a href="#command-' + nodeKey + '" data-toggle="tab"><span class="glyphicon glyphicon-log-in"></span> Command</a></li>');
			$("ul#" + nodeKey).append('<li><a href="#config-' + nodeKey + '" data-toggle="tab"><span class="glyphicon glyphicon-wrench"></span> Config</a></li>');
			$("ul#" + nodeKey).append('<li><a href="#missions-' + nodeKey + '" data-toggle="tab"><span class="glyphicon glyphicon-plane"></span> Missions</a></li>');
			$("ul#" + nodeKey).append('<li><a href="#debug-' + nodeKey + '" data-toggle="tab"><span class="glyphicon glyphicon-cog"></span> Debug</a></li>');
			
			if(node.aprf == 0){
				$("a#" + nodeKey).append(' | <span class="glyphicon glyphicon-home"></span>');
			} else {
				$("a#" + nodeKey).append(' | <span class="glyphicon glyphicon-signal"></span>');
			}
		}
		// Create station content

		$(".tab-content").append('<div id="basic-' + nodeKey + '" class="tab-pane fade"></div>');
		$(".tab-content").append('<div id="telemetry-' + nodeKey + '" class="tab-pane fade"></div>');
		$(".tab-content").append('<div id="messages-' + nodeKey + '" class="tab-pane fade"></div>');
		$(".tab-content").append('<div id="command-' + nodeKey + '" class="tab-pane fade"></div>');
		$(".tab-content").append('<div id="config-' + nodeKey + '" class="tab-pane fade"></div>');
		$(".tab-content").append('<div id="missions-' + nodeKey + '" class="tab-pane fade"></div>');
		$(".tab-content").append('<div id="debug-' + nodeKey + '" class="tab-pane fade"></div>');
		// Add content to stations tab content
		//Basic
		$("#basic-" + nodeKey).append('<h2><span class="glyphicon glyphicon-th"></span> ' + nodeText + ' | Basic Info' + '</h2>');
		//Basic Panel
			$("#basic-" + nodeKey).append('<div id="basic-panel-' + nodeKey + '" class="panel panel-primary" style="width: 800px"></div>');
			$("#basic-panel-" + nodeKey).append('<div id="basic-panel-body-' + nodeKey + '" class="panel-body"></div>');
				//Basic table
				$("#basic-panel-body-" + nodeKey).append('<table class="table" id="basic-table-' + nodeKey + '"></table>');
				$("#basic-table-" + nodeKey).append('<thead id="basic-' + nodeKey + '"></thead>');
				$("thead#basic-" + nodeKey).append('<tr id="basic-header-' + nodeKey + '"></tr>');
				$("tr#basic-header-" + nodeKey).append('<th>Parameter</th>');
				$("tr#basic-header-" + nodeKey).append('<th>Value</th>');
				$("#basic-table-" + nodeKey).append('<tr>' + '<td>RTC Time</td><td><span id="rtctime-' + nodeKey + '"></span></td>' + '</tr>');
				$("#basic-table-" + nodeKey).append('<tr>' + '<td>Access Point Time</td><td><span id="aptime-' + nodeKey + '"></span></td>' + '</tr>');
				$("#basic-table-" + nodeKey).append('<tr>' + '<td>Time Since Last Heard</td><td><span id="diff-' + nodeKey + '"></span> Seconds</td>' + '</tr>');
				$("#basic-table-" + nodeKey).append('<tr>' + '<td>Board Temperature</td><td><span id="boardtemp-' + nodeKey + '"></span> &deg;C</td>' + '</tr>');
				$("#basic-table-" + nodeKey).append('<tr>' + '<td>GPS Fix</td><td><span id="gpsfix-' + nodeKey + '"></span></td>' + '</tr>');
				$("#basic-table-" + nodeKey).append('<tr>' + '<td>GPS Latitude</td><td><span id="latdeg-' + nodeKey + '"></span> <span id="latdec-' + nodeKey + '"></span> <span id="latdir-' + nodeKey + '"></span></td>' + '</tr>');
				$("#basic-table-" + nodeKey).append('<tr>' + '<td>GPS Longitude</td><td><span id="londeg-' + nodeKey + '"></span> <span id="londec-' + nodeKey + '"></span> <span id="londir-' + nodeKey + '"></span></td>' + '</tr>');
				$("#basic-table-" + nodeKey).append('<tr>' + '<td>GPS Altitude</td><td><span id="altitude-' + nodeKey + '"></span> Meters</td>' + '</tr>');
				$("#basic-table-" + nodeKey).append('<tr>' + '<td>GPS speed</td><td><span id="speed-' + nodeKey + '"></span> Knots</td>' + '</tr>');
				$("#basic-table-" + nodeKey).append('<tr>' + '<td>VCC Voltage</td><td><span id="vcc-' + nodeKey + '"></span> Volts</td>' + '</tr>');

			
		
		//Telemetry
		$("#telemetry-" + nodeKey).append('<h2><span class="glyphicon glyphicon-globe"></span> ' + nodeText + ' | Telemetry' + '</h2>');
		//Telemetry Panel
		$("#telemetry-" + nodeKey).append('<div id="telemetry-panel-graphs-' + nodeKey + '" class="panel panel-primary" style="width: 800px"></div>');
		$("#telemetry-panel-graphs-" + nodeKey).append('<canvas id="adc0-graph-' + nodeKey + '">');
		$("#telemetry-panel-graphs-" + nodeKey).append('<canvas id="adc1-graph-' + nodeKey + '">');
		$("#telemetry-panel-graphs-" + nodeKey).append('<canvas id="adc2-graph-' + nodeKey + '">');
		$("#telemetry-panel-graphs-" + nodeKey).append('<canvas id="adc3-graph-' + nodeKey + '">');
		$("#telemetry-panel-graphs-" + nodeKey).append('<canvas id="adc4-graph-' + nodeKey + '">');
		$("#telemetry-panel-graphs-" + nodeKey).append('<canvas id="adc5-graph-' + nodeKey + '">');
		$("#telemetry-panel-graphs-" + nodeKey).append('<canvas id="adc6-graph-' + nodeKey + '">');
		$("#telemetry-panel-graphs-" + nodeKey).append('<canvas id="adc7-graph-' + nodeKey + '">');
		$("#telemetry-panel-graphs-" + nodeKey).append('<canvas id="adc8-graph-' + nodeKey + '">');
		$("#telemetry-panel-graphs-" + nodeKey).append('<canvas id="gpio0-graph-' + nodeKey + '">');
		$("#telemetry-panel-graphs-" + nodeKey).append('<canvas id="gpio1-graph-' + nodeKey + '">');
		$("#telemetry-panel-graphs-" + nodeKey).append('<canvas id="gpio2-graph-' + nodeKey + '">');
		//Messages
		$("#messages-" + nodeKey).append('<h2><span class="glyphicon glyphicon-pencil"></span> ' + nodeText + ' | Messages' + '</h2>');
		//Messages Panel
			$("#messages-" + nodeKey).append('<div id="messages-panel-' + nodeKey + '" class="panel panel-primary" style="width: 800px"></div>');
			$("#messages-panel-" + nodeKey).append('<div id="messages-panel-body-' + nodeKey + '" class="panel-body"></div>');
				//Message display and forms
				$("#messages-panel-body-" + nodeKey).append('<div id="messages-display-' + nodeKey + '" class="panel panel-primary" style="width: 750px;background: #f2f2f2;"></div>'); // def fix this...
				$("#messages-display-" + nodeKey).append('<div id="messages-text-' + nodeKey + '"></div>');
				$("#messages-text-" + nodeKey).append('<p class="text-left"><b>KB1LQD</b>: Hey what\'s up?</p>');
				$("#messages-text-" + nodeKey).append('<p class="text-right"><b>KB1LQC</b>: Just testing the messaging functionality of FaradayRF!</p>');
				$("#messages-panel-body-" + nodeKey).append('<div class="form-group" id="messages-input-' + nodeKey + '"></div>');
				//can I have multiple form groups?
				$("#messages-input-" + nodeKey).append('<form class="form-inline" id="message-recipient-input-' + nodeKey + '"></form>');
				$("#message-recipient-input-" + nodeKey).append('<input type="text" class="input-mini" id="to-message-recipient-' + nodeKey + '" placeholder="Callsign">');
				$("#message-recipient-input-" + nodeKey).append('<input type="text" class="input-mini" id="to-message-recipient-id-' + nodeKey + '" placeholder="ID">');	
				//$("#messages-input-" + nodeKey).append('<br/>');
				$("#messages-input-" + nodeKey).append('<label for="messages-input-' + nodeKey + '">Message:</label>');
				$("#messages-input-" + nodeKey).append('<textarea class="form-control" id="messages-form-' + nodeKey + '" rows="2"></textarea>');
				$("#messages-input-" + nodeKey).append('<button type="button" class="btn btn-primary">Send</button>');

		//Command
		$("#command-" + nodeKey).append('<h2><span class="glyphicon glyphicon-log-in"></span> ' + nodeText + ' | Command' + '</h2>');
		//Command Panel
			$("#command-" + nodeKey).append('<div id="command-panel-' + nodeKey + '" class="panel panel-primary" style="width: 800px"></div>');
			$("#command-panel-" + nodeKey).append('<div id="command-panel-body-' + nodeKey + '" class="panel-body"></div>');
			//Command Forms
					$("#command-panel-body-" + nodeKey).append('<form id="command-form-' + nodeKey + '" action="http://127.0.0.1:' + config.port + '/command/" method="POST"></form>'); //UPDATE URL!
					// Callsign input
					$("#command-form-" + nodeKey).append('<fieldset class="form-group" id="command-callsign-' + nodeKey + '"></fieldset>');
					$("#command-callsign-" + nodeKey).append('<div class="col-lg-3" id="command-callsign-' + nodeKey + '"></div>');
					$("div#command-callsign-" + nodeKey).append('<label for="command-callsign-' + nodeKey + '">Callsign</label>');
					$("div#command-callsign-" + nodeKey).append('<input type="text" class="form-control" id="command-callsign-' + nodeKey + '" placeholder="' + node.callsign.toUpperCase() + '" name="callsign">');
					// Node ID input
					$("#command-form-" + nodeKey).append('<fieldset class="form-group" id="command-id-' + nodeKey + '"></fieldset>');
					$("#command-id-" + nodeKey).append('<div class="col-lg-3" id="command-id-' + nodeKey + '"></div>');
					$("div#command-id-" + nodeKey).append('<label for="command-id-' + nodeKey + '">ID</label>');
					$("div#command-id-" + nodeKey).append('<input type="text" class="form-control" id="command-id-' + nodeKey + '" placeholder="' + node.id + '" name="id">');
					// UART Telemetry Interval input
					$("#command-form-" + nodeKey).append('<fieldset class="form-group" id="command-uartinterval-' + nodeKey + '"></fieldset>');
					$("#command-uartinterval-" + nodeKey).append('<div class="col-lg-3" id="command-uartinterval-' + nodeKey + '"></div>');
					$("div#command-uartinterval-" + nodeKey).append('<label for="command-uartinterval-' + nodeKey + '">UART Telemetry Interval</label>');
					$("div#command-uartinterval-" + nodeKey).append('<input type="text" class="form-control" id="command-uartinterval-' + nodeKey + '" placeholder="1" name="uartinterval">');
					// RF Telemetry Interval input
					$("#command-form-" + nodeKey).append('<fieldset class="form-group" id="command-rfinterval-' + nodeKey + '"></fieldset>');
					$("#command-rfinterval-" + nodeKey).append('<div class="col-lg-3" id="command-rfinterval-' + nodeKey + '"></div>');
					$("div#command-rfinterval-" + nodeKey).append('<label for="command-rfinterval-' + nodeKey + '">ID</label>');
					$("div#command-rfinterval-" + nodeKey).append('<input type="text" class="form-control" id="command-rfinterval-' + nodeKey + '" placeholder="1" name="rfinterval">');
					$("#command-form-" + nodeKey).append('<button type="button" class="btn btn-primary">Send</button>');
					// Put something in for "send telemetry now"... maybe on front basic info page?

				$("#command-" + nodeKey).append('<div id="command-panel-control-' + nodeKey + '" class="panel panel-primary" style="width: 200px"></div>');
				$("#command-panel-control-" + nodeKey).append('<div id="command-panel-io-body-' + nodeKey + '" class="panel-body"></div>');
				//Command Control Forms
					$("#command-panel-io-body-" + nodeKey ).append('<form id="command-io-form-' + nodeKey + '" action="http://127.0.0.1:' + config.port + '/command/" method="POST"></form>');
					$("#command-io-form-" + nodeKey).append('<table class="table" id="command-io-table-' + nodeKey + '"></table>');
					
					$("#command-io-table-" + nodeKey).append('<thead id="command-io-' + nodeKey + '"></thead>');
					$("thead#command-io-" + nodeKey).append('<tr id="command-io-header-' + nodeKey + '"></tr>');
					$("tr#command-io-header-" + nodeKey).append('<th>Channel</th>');
					$("tr#command-io-header-" + nodeKey).append('<th>ON/OFF</th>');
					//LED1
						$("#command-io-table-" + nodeKey).append('<tr>' +
						'<td style="vertical-align: middle">LED 1</td><td style="vertical-align: middle"><span id="cmd-led1-' + nodeKey + '"></span></td>' + '</tr>');
						$("span#cmd-led1-" + nodeKey ).append('<label id="cmd-led1-' + nodeKey + '"><label>');
						$("label#cmd-led1-" + nodeKey ).append('<input id="led1-box-' + nodeKey + '" type="checkbox" value="ON" name="LED1"></input>');
						$("#led1-box-" + nodeKey ).append('<input id="led1-hidden-' + nodeKey + '" type="hidden" value="OFF" name="LED1">');
					//LED2
						$("#command-io-table-" + nodeKey).append('<tr>' +
						'<td style="vertical-align: middle">LED 2</td><td style="vertical-align: middle"><span id="cmd-led2-' + nodeKey + '"></span></td>' + '</tr>');
						$("span#cmd-led2-" + nodeKey ).append('<label id="cmd-led2-' + nodeKey + '"><label>');
						$("label#cmd-led2-" + nodeKey ).append('<input id="led2-box-' + nodeKey + '" type="checkbox" value="ON" name="LED2"></input>');
						$("#led2-box-" + nodeKey ).append('<input id="led2-hidden-' + nodeKey + '" type="hidden" value="OFF" name="LED2">');
					//MOSFET
						$("#command-io-table-" + nodeKey).append('<tr>' +
						'<td style="vertical-align: middle">MOSFET</td><td style="vertical-align: middle"><span id="cmd-mosfet-' + nodeKey + '"></span></td>' + '</tr>');
						$("span#cmd-mosfet-" + nodeKey ).append('<label id="cmd-mosfet-' + nodeKey + '"><label>');
						$("label#cmd-mosfet-" + nodeKey ).append('<input id="mosfet-box-' + nodeKey + '" type="checkbox" value="ON" name="MOSFET"></input>');
						$("#mosfet-box-" + nodeKey ).append('<input id="mosfet-hidden-' + nodeKey + '" type="hidden" value="OFF" name="MOSFET">');
					//GPIO0
						$("#command-io-table-" + nodeKey).append('<tr>' +
						'<td style="vertical-align: middle">GPIO 0</td><td style="vertical-align: middle"><span id="cmd-gpio0-' + nodeKey + '"></span></td>' + '</tr>');
						$("span#cmd-gpio0-" + nodeKey ).append('<label id="cmd-gpio0-' + nodeKey + '"><label>');
						$("label#cmd-gpio0-" + nodeKey ).append('<input id="gpio0-box-' + nodeKey + '" type="checkbox" value="ON" name="GPIO0"></input>');
						$("#gpio0-box-" + nodeKey ).append('<input id="gpio0-hidden-' + nodeKey + '" type="hidden" value="OFF" name="GPIO0">');
					//GPIO1
						$("#command-io-table-" + nodeKey).append('<tr>' +
						'<td style="vertical-align: middle">GPIO 1</td><td style="vertical-align: middle"><span id="cmd-gpio1-' + nodeKey + '"></span></td>' + '</tr>');
						$("span#cmd-gpio1-" + nodeKey ).append('<label id="cmd-gpio1-' + nodeKey + '"><label>');
						$("label#cmd-gpio1-" + nodeKey ).append('<input id="gpio1-box-' + nodeKey + '" type="checkbox" value="ON" name="GPIO1"></input>');
						$("#gpio1-box-" + nodeKey ).append('<input id="gpio1-hidden-' + nodeKey + '" type="hidden" value="OFF" name="GPIO1">');
					//GPIO2
						$("#command-io-table-" + nodeKey).append('<tr>' +
						'<td style="vertical-align: middle">GPIO 2</td><td style="vertical-align: middle"><span id="cmd-gpio2-' + nodeKey + '"></span></td>' + '</tr>');
						$("span#cmd-gpio2-" + nodeKey ).append('<label id="cmd-gpio2-' + nodeKey + '"><label>');
						$("label#cmd-gpio2-" + nodeKey ).append('<input id="gpio2-box-' + nodeKey + '" type="checkbox" value="ON" name="GPIO2"></input>');
						$("#gpio2-box-" + nodeKey ).append('<input id="gpio2-hidden-' + nodeKey + '" type="hidden" value="OFF" name="GPIO2">');
					//GPIO3
						$("#command-io-table-" + nodeKey).append('<tr>' +
						'<td style="vertical-align: middle">GPIO 3</td><td style="vertical-align: middle"><span id="cmd-gpio3-' + nodeKey + '"></span></td>' + '</tr>');
						$("span#cmd-gpio3-" + nodeKey ).append('<label id="cmd-gpio3-' + nodeKey + '"><label>');
						$("label#cmd-gpio3-" + nodeKey ).append('<input id="gpio3-box-' + nodeKey + '" type="checkbox" value="ON" name="GPIO3"></input>');
						$("#gpio3-box-" + nodeKey ).append('<input id="gpio3-hidden-' + nodeKey + '" type="hidden" value="OFF" name="GPIO3">');
					//GPIO4
						$("#command-io-table-" + nodeKey).append('<tr>' +
						'<td style="vertical-align: middle">GPIO 4</td><td style="vertical-align: middle"><span id="cmd-gpio4-' + nodeKey + '"></span></td>' + '</tr>');
						$("span#cmd-gpio4-" + nodeKey ).append('<label id="cmd-gpio4-' + nodeKey + '"><label>');
						$("label#cmd-gpio4-" + nodeKey ).append('<input id="gpio4-box-' + nodeKey + '" type="checkbox" value="ON" name="GPIO4"></input>');
						$("#gpio4-box-" + nodeKey ).append('<input id="gpio4-hidden-' + nodeKey + '" type="hidden" value="OFF" name="GPIO4">');
					//GPIO5
						$("#command-io-table-" + nodeKey).append('<tr>' +
						'<td style="vertical-align: middle">GPIO 5</td><td style="vertical-align: middle"><span id="cmd-gpio5-' + nodeKey + '"></span></td>' + '</tr>');
						$("span#cmd-gpio5-" + nodeKey ).append('<label id="cmd-gpio5-' + nodeKey + '"><label>');
						$("label#cmd-gpio5-" + nodeKey ).append('<input id="gpio5-box-' + nodeKey + '" type="checkbox" value="ON" name="GPIO5"></input>');
						$("#gpio5-box-" + nodeKey ).append('<input id="gpio5-hidden-' + nodeKey + '" type="hidden" value="OFF" name="GPIO5">');
					//GPIO6
						$("#command-io-table-" + nodeKey).append('<tr>' +
						'<td style="vertical-align: middle">GPIO 6</td><td style="vertical-align: middle"><span id="cmd-gpio6-' + nodeKey + '"></span></td>' + '</tr>');
						$("span#cmd-gpio6-" + nodeKey ).append('<label id="cmd-gpio6-' + nodeKey + '"><label>');
						$("label#cmd-gpio6-" + nodeKey ).append('<input id="gpio6-box-' + nodeKey + '" type="checkbox" value="ON" name="GPIO6"></input>');
						$("#gpio6-box-" + nodeKey ).append('<input id="gpio6-hidden-' + nodeKey + '" type="hidden" value="OFF" name="GPIO6">');
					//GPIO7
						$("#command-io-table-" + nodeKey).append('<tr>' +
						'<td style="vertical-align: middle">GPIO 7</td><td style="vertical-align: middle"><span id="cmd-gpio7-' + nodeKey + '"></span></td>' + '</tr>');
						$("span#cmd-gpio7-" + nodeKey ).append('<label id="cmd-gpio7-' + nodeKey + '"><label>');
						$("label#cmd-gpio7-" + nodeKey ).append('<input id="gpio7-box-' + nodeKey + '" type="checkbox" value="ON" name="GPIO7"></input>');
						$("#gpio7-box-" + nodeKey ).append('<input id="gpio7-hidden-' + nodeKey + '" type="hidden" value="OFF" name="GPIO7">');
					//GPIO8
						$("#command-io-table-" + nodeKey).append('<tr>' +
						'<td style="vertical-align: middle">GPIO 8</td><td style="vertical-align: middle"><span id="cmd-gpio8-' + nodeKey + '"></span></td>' + '</tr>');
						$("span#cmd-gpio8-" + nodeKey ).append('<label id="cmd-gpio8-' + nodeKey + '"><label>');
						$("label#cmd-gpio8-" + nodeKey ).append('<input id="gpio8-box-' + nodeKey + '" type="checkbox" value="ON" name="GPIO8"></input>');
						$("#gpio8-box-" + nodeKey ).append('<input id="gpio8-hidden-' + nodeKey + '" type="hidden" value="OFF" name="GPIO8">');
					//GPIO9
						$("#command-io-table-" + nodeKey).append('<tr>' +
						'<td style="vertical-align: middle">GPIO 9</td><td style="vertical-align: middle"><span id="cmd-gpio9-' + nodeKey + '"></span></td>' + '</tr>');
						$("span#cmd-gpio9-" + nodeKey ).append('<label id="cmd-gpio9-' + nodeKey + '"><label>');
						$("label#cmd-gpio9-" + nodeKey ).append('<input id="gpio9-box-' + nodeKey + '" type="checkbox" value="ON" name="GPIO9"></input>');
						$("#gpio9-box-" + nodeKey ).append('<input id="gpio9-hidden-' + nodeKey + '" type="hidden" value="OFF" name="GPIO9">');
					//FLASHDEBUG
						$("#command-io-table-" + nodeKey).append('<tr>' +
						'<td style="vertical-align: middle">Get Flash Debug</td><td style="vertical-align: middle"><span id="cmd-flashdebug-' + nodeKey + '"></span></td>' + '</tr>');
						$("span#cmd-flashdebug-" + nodeKey ).append('<label id="cmd-flashdebug-' + nodeKey + '"><label>');
						$("label#cmd-flashdebug-" + nodeKey ).append('<input id="flashdebug-box-' + nodeKey + '" type="checkbox" value="ON" name="GETFLASHDEBUG"></input>');
						$("#flashdebug-box-" + nodeKey ).append('<input id="flashdebug-hidden-' + nodeKey + '" type="hidden" value="OFF" name="GETFLASHDEBUG">');
					//RESETFLASHDEBUG
						$("#command-io-table-" + nodeKey).append('<tr>' +
						'<td style="vertical-align: middle">Reset Flash Debug</td><td style="vertical-align: middle"><span id="cmd-resetflashdebug-' + nodeKey + '"></span></td>' + '</tr>');
						$("span#cmd-resetflashdebug-" + nodeKey ).append('<label id="cmd-resetflashdebug-' + nodeKey + '"><label>');
						$("label#cmd-resetflashdebug-" + nodeKey ).append('<input id="resetflashdebug-box-' + nodeKey + '" type="checkbox" value="ON" name="RESETFLASHDEBUG"></input>');
						$("#resetflashdebug-box-" + nodeKey ).append('<input id="resetflashdebug-hidden-' + nodeKey + '" type="hidden" value="OFF" name="RESETFLASHDEBUG">');
					//SYSTEMSETTINGS
						$("#command-io-table-" + nodeKey).append('<tr>' +
						'<td style="vertical-align: middle">Get System Settings</td><td style="vertical-align: middle"><span id="cmd-systemsettings-' + nodeKey + '"></span></td>' + '</tr>');
						$("span#cmd-systemsettings-" + nodeKey ).append('<label id="cmd-systemsettings-' + nodeKey + '"><label>');
						$("label#cmd-systemsettings-" + nodeKey ).append('<input id="systemsettings-box-' + nodeKey + '" type="checkbox" value="ON" name="GETSYSTEMSETTINGS"></input>');
						$("#systemsettings-box-" + nodeKey ).append('<input id="systemsettings-hidden-' + nodeKey + '" type="hidden" value="OFF" name="GETSYSTEMSETTINGS">');

					//Button
/* 						if node.aprf == 0{
							$("#command-io-form-" + nodeKey).append('<input id="command-aprf-' + nodeKey + '" type="hidden" value="' + node.aprf + '" name="aprf">');
						} else {
							$("#command-io-form-" + nodeKey).append('<input id="command-aprf-' + nodeKey + '" type="hidden" value="' + node.aprf + '" name="aprf">');
						} */
						$("#command-io-form-" + nodeKey).append('<input id="command-aprf-' + nodeKey + '" type="hidden" value="' + node.aprf + '" name="aprf">');
						$("#command-io-form-" + nodeKey).append('<input id="command-callsign-' + nodeKey + '" type="hidden" value="' + node.callsign + '" name="callsign">');
						$("#command-io-form-" + nodeKey).append('<input id="command-id-' + nodeKey + '" type="hidden" value="' + node.id+ '" name="id">');
						$("#command-io-form-" + nodeKey).append('<button type="submit" class="btn btn-primary">Send</button>');
						
						$("#command-io-form-" + nodeKey).submit(function(){
							if(document.getElementById("led1-box-" + nodeKey).checked) {
								document.getElementById("led1-hidden-" + nodeKey).disabled = true;
								}
							if(document.getElementById("led2-box-" + nodeKey).checked) {
								document.getElementById("led2-hidden-" + nodeKey).disabled = true;
								}
							if(document.getElementById("gpio0-box-" + nodeKey).checked) {
								document.getElementById("gpio0-hidden-" + nodeKey).disabled = true;
								}
							if(document.getElementById("gpio1-box-" + nodeKey).checked) {
								document.getElementById("gpio1-hidden-" + nodeKey).disabled = true;
								}
							if(document.getElementById("gpio2-box-" + nodeKey).checked) {
								document.getElementById("gpio2-hidden-" + nodeKey).disabled = true;
								}
							if(document.getElementById("gpio3-box-" + nodeKey).checked) {
								document.getElementById("gpio3-hidden-" + nodeKey).disabled = true;
								}
							if(document.getElementById("gpio4-box-" + nodeKey).checked) {
								document.getElementById("gpio4-hidden-" + nodeKey).disabled = true;
								}
							if(document.getElementById("gpio5-box-" + nodeKey).checked) {
								document.getElementById("gpio5-hidden-" + nodeKey).disabled = true;
								}
							if(document.getElementById("gpio6-box-" + nodeKey).checked) {
								document.getElementById("gpio6-hidden-" + nodeKey).disabled = true;
								}
							if(document.getElementById("gpio7-box-" + nodeKey).checked) {
								document.getElementById("gpio7-hidden-" + nodeKey).disabled = true;
								}
							if(document.getElementById("gpio8-box-" + nodeKey).checked) {
								document.getElementById("gpio8-hidden-" + nodeKey).disabled = true;
								}
							if(document.getElementById("gpio9-box-" + nodeKey).checked) {
								document.getElementById("gpio9-hidden-" + nodeKey).disabled = true;
								}
							if(document.getElementById("mosfet-box-" + nodeKey).checked) {
								document.getElementById("mosfet-hidden-" + nodeKey).disabled = true;
								}						

							});
						
		//Config
		if( node.aprf == 0){
			$("#config-" + nodeKey).append('<h2><span class="glyphicon glyphicon-wrench"></span> ' + nodeText + ' | Configuration' + '</h2>');
			//Config Panel
				$("#config-" + nodeKey).append('<div id="config-panel-' + nodeKey + '" class="panel panel-primary" style="width: 800px"></div>');
				$("#config-panel-" + nodeKey).append('<div id="config-panel-body-' + nodeKey + '" class="panel-body"></div>');
				//Config Forms
					$("#config-panel-body-" + nodeKey).append('<form id="config-form-' + nodeKey + '" action="http://127.0.0.1/config/" method="POST"></form>');
					// Callsign input
					$("#config-form-" + nodeKey).append('<fieldset class="form-group" id="form-group-callsign-' + nodeKey + '"></fieldset>');
					$("#form-group-callsign-" + nodeKey).append('<label for="config-callsign-' + nodeKey + '">Callsign</label>');
					$("#form-group-callsign-" + nodeKey).append('<input type="text" class="form-control" id="config-callsign-' + nodeKey + '" value="' + node.callsign.toUpperCase() + '" name="callsign">');
					// Node ID input
					$("#config-form-" + nodeKey).append('<fieldset class="form-group" id="form-group-nodeid-' + nodeKey + '"></fieldset>');
					$("#form-group-nodeid-" + nodeKey).append('<label for="config-nodeid-' + nodeKey + '">ID</label>');
					$("#form-group-nodeid-" + nodeKey).append('<input type="text" class="form-control" id="config-nodeid-' + nodeKey + '" value="' + node.id + '" name="nodeid">');
					// Boot Frequency input
					$("#config-form-" + nodeKey).append('<fieldset class="form-group" id="form-group-bootfreq-' + nodeKey + '"></fieldset>');
					$("#form-group-bootfreq-" + nodeKey).append('<label for="config-bootfreq-' + nodeKey + '">Boot Frequency (MHz)</label>');
					$("#form-group-bootfreq-" + nodeKey).append('<input type="text" class="form-control" id="config-bootfreq-' + nodeKey + '" name="bootfreq" value="914.5">');//HARDCODED!!!!
					// RF Power Config input
					$("#config-form-" + nodeKey).append('<fieldset class="form-group" id="form-group-rfpower-' + nodeKey + '"></fieldset>');
					$("#form-group-rfpower-" + nodeKey).append('<label for="config-rfpower-' + nodeKey + '">RF Power</label>');
					$("#form-group-rfpower-" + nodeKey).append('<input type="text" class="form-control" id="config-rfpower-' + nodeKey + '" name="powerconf" value="100">');//HARDCODED!!!!
					// UART Telemetry Interval input
					$("#config-form-" + nodeKey).append('<fieldset class="form-group" id="form-group-uarttelem-' + nodeKey + '"></fieldset>');
					$("#form-group-uarttelem-" + nodeKey).append('<label for="config-uarttelem-' + nodeKey + '">UART Telemetry Interval</label>');
					$("#form-group-uarttelem-" + nodeKey).append('<input type="text" class="form-control" id="config-uarttelem-' + nodeKey + '" name="uartinterval" value="2">');//HARDCODED!!!!
					// RF Telemetry Interval input
					$("#config-form-" + nodeKey).append('<fieldset class="form-group" id="form-group-rftelem-' + nodeKey + '"></fieldset>');
					$("#form-group-rftelem-" + nodeKey).append('<label for="config-rftelem-' + nodeKey + '">RF Telemetry Boot Interval</label>');
					$("#form-group-rftelem-" + nodeKey).append('<input type="text" class="form-control" id="config-rftelem-' + nodeKey + '" name="rfinterval" value="2">');//HARDCODED!!!!
					// Latitude
					$("#config-form-" + nodeKey).append('<fieldset class="form-group" id="form-group-latitude-' + nodeKey + '"></fieldset>');
					$("#form-group-latitude-" + nodeKey).append('<label for="config-latitude-' + nodeKey + '">Latitude</label>');
					$("#form-group-latitude-" + nodeKey).append('<input type="text" class="form-control" id="config-latitude-' + nodeKey + '" value="' + node.latdeg + node.latdec + '" name="latitude">');//HARDCODED!!!!
					// Latitude Direction
					$("#config-form-" + nodeKey).append('<fieldset class="form-group" id="form-group-latitudedir-' + nodeKey + '"></fieldset>');
					$("#form-group-latitudedir-" + nodeKey).append('<label for="config-latitudedir-' + nodeKey + '">Latitude Direction</label>');
					$("#form-group-latitudedir-" + nodeKey).append('<input type="text" class="form-control" id="config-latitudedir-' + nodeKey + '" value="' + node.latdir + '" name="latdir">');
					// Longitude
					$("#config-form-" + nodeKey).append('<fieldset class="form-group" id="form-group-longitude-' + nodeKey + '"></fieldset>');
					$("#form-group-longitude-" + nodeKey).append('<label for="config-longitude-' + nodeKey + '">Longitude</label>');
					$("#form-group-longitude-" + nodeKey).append('<input type="text" class="form-control" id="config-longitude-' + nodeKey + '" value="' + node.londeg + node.londec + '" name="longitude">');//HARDCODED!!!!
					// Longitude Direction
					$("#config-form-" + nodeKey).append('<fieldset class="form-group" id="form-group-longitudedir-' + nodeKey + '"></fieldset>');
					$("#form-group-longitudedir-" + nodeKey).append('<label for="config-longitudedir-' + nodeKey + '">Longitude Direction</label>');
					$("#form-group-longitudedir-" + nodeKey).append('<input type="text" class="form-control" id="config-longitudedir-' + nodeKey + '" value="' + node.londir + '" name="londir">');
					// Altitude
					$("#config-form-" + nodeKey).append('<fieldset class="form-group" id="form-group-altitude-' + nodeKey + '"></fieldset>');
					$("#form-group-altitude-" + nodeKey).append('<label for="config-altitude-' + nodeKey + '">Altitude (m)</label>');
					$("#form-group-altitude-" + nodeKey).append('<input type="text" class="form-control" id="config-altitude-' + nodeKey + '" value="' + node.altitude + '" name="altitude">');
					// GPS Boot
					$("#config-form-" + nodeKey).append('<fieldset class="form-group" id="form-group-gpsboot-' + nodeKey + '"></fieldset>');
					$("#form-group-gpsboot-" + nodeKey).append('<label for="config-gpsboot-' + nodeKey + '">GPS Boot</label>');
					$("#form-group-gpsboot-" + nodeKey).append('<input type="text" class="form-control" id="config-gpsboot-' + nodeKey + '" name="gpsboot" value="1">');//HARDCODED!!!!
					// UART Telemetry Boot
					$("#config-form-" + nodeKey).append('<fieldset class="form-group" id="form-group-uarttelemboot-' + nodeKey + '"></fieldset>');
					$("#form-group-uarttelemboot-" + nodeKey).append('<label for="config-gpsboot-' + nodeKey + '">UART Telemetry Boot</label>');
					$("#form-group-uarttelemboot-" + nodeKey).append('<input type="text" class="form-control" id="config-uarttelemboot-' + nodeKey + '" name="uarttelemboot" value="1">');//HARDCODED!!!!
					// RF Telemetry Boot
					$("#config-form-" + nodeKey).append('<fieldset class="form-group" id="form-group-rftelemboot-' + nodeKey + '"></fieldset>');
					$("#form-group-rftelemboot-" + nodeKey).append('<label for="config-rftelemboot-' + nodeKey + '">RF Telemetry Boot</label>');
					$("#form-group-rftelemboot-" + nodeKey).append('<input type="text" class="form-control" id="config-rftelemboot-' + nodeKey + '" name="rftelemboot" value="1">');//HARDCODED!!!!


					/* // GPS Boot
					$("#config-form-" + nodeKey).append('<div class="checkbox" id="checkbox-gpsboot-' + nodeKey + '"></div>');
					$("#checkbox-gpsboot-" + nodeKey).append('<label><input type="checkbox" value="1" name="gpsboot">GPS Boot</label>');
					// UART Telemetry Boot
					$("#config-form-" + nodeKey).append('<div class="checkbox" id="checkbox-uarttelemboot-' + nodeKey + '"></div>');
					$("#checkbox-uarttelemboot-" + nodeKey).append('<label><input type="checkbox" value="1" name="uarttelemboot">UART Telemetry Boot</label>');
					// GPS Boot
					$("#config-form-" + nodeKey).append('<div class="checkbox" id="checkbox-rftelemboot-' + nodeKey + '"></div>');
					$("#checkbox-rftelemboot-" + nodeKey).append('<label><input type="checkbox" value="1" name="rftelemboot">RF Telemetry Boot</label>'); */
					//Submit Button
					$("#config-form-" + nodeKey).append('<button type="submit" class="btn btn-primary">Configure</button>');
		} else {
			$("#config-" + nodeKey).append('<h2><span class="glyphicon glyphicon-wrench"></span> ' + nodeText + ' | Configuration' + '</h2>');
			$("#config-" + nodeKey).append('<p class="text-warning">Configuration only available to local USB connected nodes!</p>');
		}

		//Debug
		$("#debug-" + nodeKey).append('<h2><span class="glyphicon glyphicon-cog"></span> ' + nodeText + ' | Debug' + '</h2>');
		//debug Panel
			$("#debug-" + nodeKey).append('<div id="debug-panel-' + nodeKey + '" class="panel panel-primary" style="width: 800px"></div>');
			$("#debug-panel-" + nodeKey).append('<div id="debug-panel-body-' + nodeKey + '" class="panel-body"></div>');
			//Debug table
				$("#debug-panel-body-" + nodeKey).append('<table class="table" id="debug-table-' + nodeKey + '"></table>');
				$("#debug-table-" + nodeKey).append('<thead id="debug-' + nodeKey + '"></thead>');
				$("thead#debug-" + nodeKey).append('<tr id="debug-header-' + nodeKey + '"></tr>');
				$("tr#debug-header-" + nodeKey).append('<th>Parameter</th>');
				$("tr#debug-header-" + nodeKey).append('<th>Value</th>');
				$("#debug-table-" + nodeKey).append('<tr>' + '<td>RF Frequency 0</td><td><span id="rffreq0-' + nodeKey + '"></span></td>' + '</tr>');
				$("#debug-table-" + nodeKey).append('<tr>' + '<td>RF Frequency 1</td><td><span id="rffreq1-' + nodeKey + '"></span></td>' + '</tr>');
				$("#debug-table-" + nodeKey).append('<tr>' + '<td>RF Frequency 2</td><td><span id="rffreq2-' + nodeKey + '"></span></td>' + '</tr>');
				$("#debug-table-" + nodeKey).append('<tr>' + '<td>RF Power</td><td><span id="rfpwr-' + nodeKey + '"></span></td>' + '</tr>');
				$("#debug-table-" + nodeKey).append('<tr>' + '<td>Boot Count</td><td><span id="bootcount-' + nodeKey + '"></span></td>' + '</tr>');
				$("#debug-table-" + nodeKey).append('<tr>' + '<td>Reset Count</td><td><span id="resetcount-' + nodeKey + '"></span></td>' + '</tr>');
				$("#debug-table-" + nodeKey).append('<tr>' + '<td>Brownout Reset Count</td><td><span id="bor-' + nodeKey + '"></span></td>' + '</tr>');
				$("#debug-table-" + nodeKey).append('<tr>' + '<td>Reset Interrupt Count</td><td><span id="rstnmi-' + nodeKey + '"></span></td>' + '</tr>');
				$("#debug-table-" + nodeKey).append('<tr>' + '<td>Supervisor Low Count</td><td><span id="svsl-' + nodeKey + '"></span></td>' + '</tr>');
				$("#debug-table-" + nodeKey).append('<tr>' + '<td>Supervisor High Count</td><td><span id="svsh-' + nodeKey + '"></span></td>' + '</tr>');
				$("#debug-table-" + nodeKey).append('<tr>' + '<td>Supervisor Low OVP Count</td><td><span id="svmlovp-' + nodeKey + '"></span></td>' + '</tr>');
				$("#debug-table-" + nodeKey).append('<tr>' + '<td>Supervisor High OVP Count</td><td><span id="svmhovp-' + nodeKey + '"></span></td>' + '</tr>');
				$("#debug-table-" + nodeKey).append('<tr>' + '<td>Watchdog Timeout Count</td><td><span id="wdtto-' + nodeKey + '"></span></td>' + '</tr>');
				$("#debug-table-" + nodeKey).append('<tr>' + '<td>Flash Key Violation Count</td><td><span id="flashkeyviolation-' + nodeKey + '"></span></td>' + '</tr>');
				$("#debug-table-" + nodeKey).append('<tr>' + '<td>FLL Unlock Count</td><td><span id="fllunlock-' + nodeKey + '"></span></td>' + '</tr>');
				$("#debug-table-" + nodeKey).append('<tr>' + '<td>Peripheral Config Count</td><td><span id="peripheralconfigcnt-' + nodeKey + '"></span></td>' + '</tr>');
				$("#debug-table-" + nodeKey).append('<tr>' + '<td>Access Violation Count</td><td><span id="accessviolation-' + nodeKey + '"></span></td>' + '</tr>');
		//Missions
		$("#missions-" + nodeKey).append('<h2><span class="glyphicon glyphicon-plane"></span> ' + nodeText + ' | Missions' + '</h2>');
		//debug Panel
			$("#missions-" + nodeKey).append('<div id="missions-panel-' + nodeKey + '" class="panel panel-primary" style="width: 800px"></div>');
			$("#missions-panel-" + nodeKey).append('<div id="missions-panel-body-' + nodeKey + '" class="panel-body"></div>');
			//Debug table
				$("#missions-panel-body-" + nodeKey).append("<h1>High Altitude Balloon</h1>");
				$("#missions-panel-body-" + nodeKey).append('<table class="table" id="missions-table-' + nodeKey + '"></table>');
				$("#missions-table-" + nodeKey).append('<thead id="missions-' + nodeKey + '"></thead>');
				$("thead#missions-" + nodeKey).append('<tr id="missions-header-' + nodeKey + '"></tr>');
				$("tr#missions-header-" + nodeKey).append('<th>Parameter</th>');
				$("tr#missions-header-" + nodeKey).append('<th>Value</th>');
				$("#missions-table-" + nodeKey).append('<tr>' + '<td>GPS Location</td><td><span id="location-' + nodeKey + '"></span><span id="location-button-' + nodeKey + '"></span></td>' + '</tr>');
				$("#location-button-" + nodeKey).append(' <button class="button" id="location" data-clipboard-target="#location-' + nodeKey + '"><span class="glyphicon glyphicon-copy" alt="Copy to clipboard"></span></button>');
				$("#location-button-" + nodeKey).attr('title', 'Copy to clipboard');
				$("#missions-table-" + nodeKey).append('<tr>' + '<td>GPS Altitude</td><td><span id="hab-gps-altitude-' + nodeKey + '"></span></td>' + '</tr>');
				$("#missions-table-" + nodeKey).append('<tr>' + '<td>GPS Speed</td><td><span id="hab-gps-speed-' + nodeKey + '"></span></td>' + '</tr>');
				$("#missions-table-" + nodeKey).append('<tr>' + '<td>Distance</td><td><span id="hab-distance-' + nodeKey + '"></span></td>' + '</tr>');
				$("#missions-table-" + nodeKey).append('<tr>' + '<td>Relative Direction</td><td><span id="hab-rel-bearing-' + nodeKey + '"></span></td>' + '</tr>');
				$("#missions-table-" + nodeKey).append('<tr>' + '<td>Elevation Above Horizon</td><td><span id="hab-rel-elevation-' + nodeKey + '"></span></td>' + '</tr>');
				$("#missions-table-" + nodeKey).append('<tr>' + '<td>Remote Node Radio Horizon</td><td><span id="hab-rem-horizon-' + nodeKey + '"></span></td>' + '</tr>');
				$("#missions-table-" + nodeKey).append('<tr>' + '<td>Cutdown Timer State</td><td><span id="uChar_auto_cutdown_timer_state_status-' + nodeKey + '"></span></td>' + '</tr>');
				$("#missions-table-" + nodeKey).append('<tr>' + '<td>Cutdown Event State</td><td><span id="uChar_cutdown_event_state_status-' + nodeKey + '"></span></td>' + '</tr>');
				$("#missions-table-" + nodeKey).append('<tr>' + '<td>Automatic Cutdown Timer Set</td><td><span id="uInt_timer_set-' + nodeKey + '"></span></td>' + '</tr>');
				$("#missions-table-" + nodeKey).append('<tr>' + '<td>Timer Current Value</td><td><span id="uInt_timer_current-' + nodeKey + '"></span></td>' + '</tr>');
				//SendCommand_HAB_Reset_Auto_Cutdown_Timer();
				//$("#missions-table-" + nodeKey).append('<tr>' + '<td>Cutdown Timer State</td><td><span id="uChar_auto_cutdown_timer_state_status-' + nodeKey + '"></span></td>' + '</tr>');
			$("#missions-" + nodeKey).append('<div id="missions-hab-control-panel-' + nodeKey + '" class="panel panel-primary" style="width: 800px"></div>');
			$("#missions-hab-control-panel-" + nodeKey).append('<div id="missions-hab-control-panel-body-' + nodeKey + '" class="panel-body"></div>');
			$("#missions-hab-control-panel-body-" + nodeKey ).append('<form id="hab-io-form-' + nodeKey + '" action="http://127.0.0.1:' + config.port + '/command/missions" method="POST"></form>');
					$("#hab-io-form-" + nodeKey).append('<table class="table" id="hab-io-table-' + nodeKey + '"></table>');
					// This is pretty crappy code and even display UI
					$("#hab-io-table-" + nodeKey).append('<thead id="hab-io-' + nodeKey + '"></thead>');
					$("thead#hab-io-" + nodeKey).append('<tr id="hab-io-header-' + nodeKey + '"></tr>');
					$("tr#hab-io-header-" + nodeKey).append('<th>Action</th>');
					$("tr#hab-io-header-" + nodeKey).append('<th>ON/OFF</th>');
					//Reset Timer
						$("#hab-io-table-" + nodeKey).append('<tr>' +
						'<td style="vertical-align: middle">Reset Countdown Timer</td><td style="vertical-align: middle"><span id="cmd-hab-timer-rst-' + nodeKey + '"></span></td>' + '</tr>');
						$("span#cmd-hab-timer-rst-" + nodeKey ).append('<label id="cmd-hab-timer-rst-' + nodeKey + '"><label>');
						$("label#cmd-hab-timer-rst-" + nodeKey ).append('<input id="hab-rst-timer-box-' + nodeKey + '" type="checkbox" value="ON" name="RESETHABTIMER"></input>');
						$("#hab-rst-timer-box-" + nodeKey ).append('<input id="hab-rst-timer-box-hidden-' + nodeKey + '" type="hidden" value="OFF" name="RESETHABTIMER">');
					//Set Cutdown Event Idle
						$("#hab-io-table-" + nodeKey).append('<tr>' +
						'<td style="vertical-align: middle">Set Cutdown Event Idle</td><td style="vertical-align: middle"><span id="cmd-hab-set-cutdown-idle-' + nodeKey + '"></span></td>' + '</tr>');
						$("span#cmd-hab-set-cutdown-idle-" + nodeKey ).append('<label id="cmd-hab-set-cutdown-idle-' + nodeKey + '"><label>');
						$("label#cmd-hab-set-cutdown-idle-" + nodeKey ).append('<input id="hab-set-cutdown-idle-box-' + nodeKey + '" type="checkbox" value="ON" name="SETHABCUTDOWNEVENTIDLE"></input>');
						$("#hab-set-cutdown-idle-box-" + nodeKey ).append('<input id="hab-set-cutdown-idle-box-hidden-' + nodeKey + '" type="hidden" value="OFF" name="SETHABCUTDOWNEVENTIDLE">');
					//Disable Automatic Cutdown Timer
						$("#hab-io-table-" + nodeKey).append('<tr>' +
						'<td style="vertical-align: middle">Disable Countdown Timer</td><td style="vertical-align: middle"><span id="cmd-hab-timer-disable-' + nodeKey + '"></span></td>' + '</tr>');
						$("span#cmd-hab-timer-disable-" + nodeKey ).append('<label id="cmd-hab-timer-disable-' + nodeKey + '"><label>');
						$("label#cmd-hab-timer-disable-" + nodeKey ).append('<input id="hab-disable-timer-box-' + nodeKey + '" type="checkbox" value="ON" name="DISABLEHABTIMER"></input>');
						$("#hab-disable-timer-box-" + nodeKey ).append('<input id="hab-disable-timer-box-hidden-' + nodeKey + '" type="hidden" value="OFF" name="DISABLEHABTIMER">');
						$("span#cmd-hab-timer-disable-" + nodeKey ).append(' <span class="glyphicon glyphicon-alert" style="color:red;font-size:1.5em"></span>');
					//Activate Cutdown
						$("#hab-io-table-" + nodeKey).append('<tr>' +
						'<td style="vertical-align: middle">Countdown Now</td><td style="vertical-align: middle"><span id="cmd-hab-cutdown-' + nodeKey + '"></span></td>' + '</tr>');
						$("span#cmd-hab-cutdown-" + nodeKey ).append('<label id="cmd-hab-cutdown-' + nodeKey + '"><label>');
						$("label#cmd-hab-cutdown-" + nodeKey ).append('<input id="hab-cutdown-box-' + nodeKey + '" type="checkbox" value="ON" name="CUTDOWN"></input>');
						$("#hab-cutdown-box-" + nodeKey ).append('<input id="hab-cutdown-box-hidden-' + nodeKey + '" type="hidden" value="OFF" name="CUTDOWN">');
						$("span#cmd-hab-cutdown-" + nodeKey ).append(' <span class="glyphicon glyphicon-alert" style="color:red;font-size:1.5em"></span>');
						
					$("#hab-io-form-" + nodeKey).append('<input id="hab-aprf-' + nodeKey + '" type="hidden" value="' + node.aprf + '" name="aprf">');
						$("#hab-io-form-" + nodeKey).append('<input id="hab-callsign-' + nodeKey + '" type="hidden" value="' + node.callsign + '" name="callsign">');
						$("#hab-io-form-" + nodeKey).append('<input id="hab-id-' + nodeKey + '" type="hidden" value="' + node.id+ '" name="id">');
						$("#hab-io-form-" + nodeKey).append('<button type="submit" class="btn btn-primary">Send</button>');
						// Button javascript to suppress or enable hidden elements for checkboxes
						$("#hab-io-form-" + nodeKey).submit(function(){
							if(document.getElementById("hab-rst-timer-box-" + nodeKey).checked) {
								document.getElementById("hab-rst-timer-box-hidden-" + nodeKey).disabled = true;
								}
							if(document.getElementById("hab-disable-timer-box-" + nodeKey).checked) {
								document.getElementById("hab-disable-timer-box-hidden-" + nodeKey).disabled = true;
								}
							if(document.getElementById("hab-cutdown-box-" + nodeKey).checked) {
								document.getElementById("hab-cutdown-box-hidden-" + nodeKey).disabled = true;
								}
							});
				
			
		// Misc
		
		//Create chart.js charts
		console.log("Creating initial plot data: " + callsign + "-" + nodeid);
		getPlotData(callsign,nodeid,60,0,0);
	}
	}});
};

function validateConfiguration(){
	var inpObj = document.getElementById("nodeid");
	if(inpObj.checkValidity() == false){
		document.getElementById("nodeidtext").innerHTML = inpObj.validationMessage;
	} else {
		document.getElementById("nodeidtext").innerHTML = "Input OK";
	}
}

function dec2bin8(dec){
	var pad = "00000000";
	var num;
	try{
		num = dec.toString(2);
		ans = ('00000000' + num).substring(num.length).split("");
	}
	catch(err){
		//console.log("DECIMAL CANNOT BE CONVERTED TO BINARY ARRAY");
		ans = 0;
	}
	
	return ans;
}
function rtcConverter(data){
	//rtcSec,rtcMin,rtcHour,rtcDay,rtcDOW,rtcMon,rtcYear
	var nodeDate
	var sec = data.rtcsec;
	var min = data.rtcmin;
	var hour = data.rtchour;
	var day = data.rtcday;
	var dow = data.rtcdow;
	var mon = data.rtcmon;
	var year = data.rtcyear;
	//var str = year + "-" + mon + "-" + day + "T" + hour + ":" + min + ":" +
	//sec;
	//nodeDate = new Date(str);
	// Javascript month is 0 indexed...
	nodeDate = new Date(Date.UTC(year,mon - 1,day,hour,min,sec));
	return  nodeDate;
}

function proxyEpochConverter(epoch){
	nodeDate = new Date(epoch*1000);
	return nodeDate;
}

function checkboxState(gpio0,gpio1,gpio2){

	if(gpio1[3] != $("#LED1").prop('checked')){
		$("#LED1-TEXT").css({"color": "red"});
	} else {
		$("#LED1-TEXT").css({"color": "black"});
	}
	if(gpio1[4] != $("#LED2").prop('checked')){
		$("#LED2-TEXT").css({"color": "red"});
	} else {
		$("#LED2-TEXT").css({"color": "black"});
	}
	if(gpio0[0] != $("#GPIO0").prop('checked')){
		$("#GPIO0-TEXT").css({"color": "red"});
	} else {
		$("#GPIO0-TEXT").css({"color": "black"});
	}
	if(gpio0[1] != $("#GPIO1").prop('checked')){
		$("#GPIO1-TEXT").css({"color": "red"});
	} else {
		$("#GPIO1-TEXT").css({"color": "black"});
	}
	if(gpio0[2] != $("#GPIO2").prop('checked')){
		$("#GPIO2-TEXT").css({"color": "red"});
	} else {
		$("#GPIO2-TEXT").css({"color": "black"});
	}
	if(gpio0[3] != $("#GPIO3").prop('checked')){
		$("#GPIO3-TEXT").css({"color": "red"});
	} else {
		$("#GPIO3-TEXT").css({"color": "black"});
	}
	if(gpio0[4] != $("#GPIO4").prop('checked')){
		$("#GPIO4-TEXT").css({"color": "red"});
	} else {
		$("#GPIO4-TEXT").css({"color": "black"});
	}
	if(gpio0[5] != $("#GPIO5").prop('checked')){
		$("#GPIO5-TEXT").css({"color": "red"});
	} else {
		$("#GPIO5-TEXT").css({"color": "black"});
	}
	if(gpio0[6] != $("#GPIO6").prop('checked')){
		$("#GPIO6-TEXT").css({"color": "red"});
	} else {
		$("#GPIO6-TEXT").css({"color": "black"});
	}
	if(gpio0[7] != $("#GPIO7").prop('checked')){
		$("#GPIO7-TEXT").css({"color": "red"});
	} else {
		$("#GPIO7-TEXT").css({"color": "black"});
	}
	if(gpio1[0] != $("#GPIO8").prop('checked')){
		$("#GPIO8-TEXT").css({"color": "red"});
	} else {
		$("#GPIO8-TEXT").css({"color": "black"});
	}
	if(gpio1[1] != $("#GPIO9").prop('checked')){
		$("#GPIO9-TEXT").css({"color": "red"});
	} else {
		$("#GPIO9-TEXT").css({"color": "black"});
	}
	if(gpio1[2] != $("#MOSFET").prop('checked')){
		$("#MOSFET-TEXT").css({"color": "red"});
	} else {
		$("#MOSFET-TEXT").css({"color": "black"});
	}

}

function setIOCheckboxes(){
	var LEDState = $("#LEDState").data();
	var GPIOState = $("#GPIOState").data();

	if(LEDState.led1 == 1){
		$("#LED1").prop('checked',true);
	}
	if(LEDState.led2 == 1){
		$("#LED2").prop('checked',true);
	}
	if(GPIOState.gpio0 == 1){
		$("#GPIO0").prop('checked',true);
	}
	if(GPIOState.gpio1 == 1){
		$("#GPIO1").prop('checked',true);
	}
	if(GPIOState.gpio2 == 1){
		$("#GPIO2").prop('checked',true);
	}
	if(GPIOState.gpio3 == 1){
		$("#GPIO3").prop('checked',true);
	}
	if(GPIOState.gpio4 == 1){
		$("#GPIO4").prop('checked',true);
	}
	if(GPIOState.gpio5 == 1){
		$("#GPIO5").prop('checked',true);
	}
	if(GPIOState.gpio6 == 1){
		$("#GPIO6").prop('checked',true);
	}
	if(GPIOState.gpio7 == 1){
		$("#GPIO7").prop('checked',true);
	}
	if(GPIOState.gpio8 == 1){
		$("#GPIO8").prop('checked',true);
	}
	if(GPIOState.gpio9 == 1){
		$("#GPIO9").prop('checked',true);
	}
	if(GPIOState.mosfet == 1){
		$("#MOSFET").prop('checked',true);
	}

}
/* 
function test(){
	// probably doesn't work, just copy pasted from html script calls to save this
	
		alert("test!");
					if(document.getElementById("LED1").checked) {
						document.getElementById('LED1HIDDEN').disabled = true;
						}
					if(document.getElementById("LED2").checked) {
						document.getElementById('LED2HIDDEN').disabled = true;
						}
					if(document.getElementById("GPIO0").checked) {
						document.getElementById('GPIO0HIDDEN').disabled = true;
						}
					if(document.getElementById("GPIO1").checked) {
						document.getElementById('GPIO1HIDDEN').disabled = true;
						}
					if(document.getElementById("GPIO2").checked) {
						document.getElementById('GPIO2HIDDEN').disabled = true;
						}
					if(document.getElementById("GPIO3").checked) {
						document.getElementById('GPIO3HIDDEN').disabled = true;
						}
					if(document.getElementById("GPIO4").checked) {
						document.getElementById('GPIO4HIDDEN').disabled = true;
						}
					if(document.getElementById("GPIO5").checked) {
						document.getElementById('GPIO5HIDDEN').disabled = true;
						}
					if(document.getElementById("GPIO6").checked) {
						document.getElementById('GPIO6HIDDEN').disabled = true;
						}
					if(document.getElementById("GPIO7").checked) {
						document.getElementById('GPIO7HIDDEN').disabled = true;
						}
					if(document.getElementById("GPIO8").checked) {
						document.getElementById('GPIO8HIDDEN').disabled = true;
						}
					if(document.getElementById("GPIO9").checked) {
						document.getElementById('GPIO9HIDDEN').disabled = true;
						}
					if(document.getElementById("MOSFET").checked) {
						document.getElementById('MOSFETHIDDEN').disabled = true;
						}						

					});
	
} */

function addStationManually(callsign,nodeid, aprf){
	$.post('faraday/addstation', {callsign: callsign, nodeid: nodeid, aprf: aprf}, 
    function(returnedData){
         console.log(returnedData);
	});
	/* $.ajax({
				method: 'POST',
				data: {callsign: callsign, nodeid: nodeid},
				url: "faraday/addstation",
				success: function test(result){
					console.log("posted");
	}}); */
	//'/faraday/<int:port>'
}

function getPlotData(callsign,nodeid,limit,epochstart,epochend){
	// implement epoch search later
	//console.log(callsign,nodeid,limit);
	$.ajax({
		url: "faraday/telemetry",
		data: {callsign: callsign, nodeid: nodeid, limit: limit},
		success: function test(result){
			data = JSON.parse(result);
			plotChart(data, callsign, nodeid);

	}});
}

// not done
function drawADCChart(callsign,nodeid,data,yAxis){
	nodeKey = callsign + nodeid;
	chartData = assembleChartData(data,yAxis);
	createADCCharts(callsign, nodeid, chartData);
}

//not done
function createADCCharts(callsign,nodeid,chartData){
	var nodeKey = callsign + nodeid;
	var chart0 = $("#adc0-graph-" + nodeKey);
	var chartADC0 = new Chart(chart0,{
		type: 'line',
		data: chartData[0].datasets[0].data,
		options: {
			title: {
				display: true,
				text: callsign + '-' + nodeid + ' | ADC 0',
				fontSize: 24
			},
			legend: {
				display: false,
			}
		}
	});
}

/* //not done
function assembleChartData(data,yAxis){
	var dataADC0 = {
		labels: yAxis,
		datasets: [
			{
				label: "ADC 0",
				fill: false,
				data: data[0],
			}
		]
	}
	var dataADC1 = {
		labels: yAxis,
		datasets: [
			{
				label: "ADC 1",
				fill: false,
				data: data[1],
			}
		]
	}
	var dataADC2 = {
		labels: yAxis,
		datasets: [
			{
				label: "ADC 2",
				fill: false,
				data: data[2],
			}
		]
	}
	var dataADC3 = {
		labels: yAxis,
		datasets: [
			{
				label: "ADC 3",
				fill: false,
				data: data[3],
			}
		]
	}
	var dataADC4 = {
		labels: yAxis,
		datasets: [
			{
				label: "ADC 4",
				fill: false,
				data: data[4],
			}
		]
	}
	var dataADC5 = {
		labels: yAxis,
		datasets: [
			{
				label: "ADC 5",
				fill: false,
				data: data[5],
			}
		]
	}
	var dataADC6 = {
		labels: yAxis,
		datasets: [
			{
				label: "ADC 6",
				fill: false,
				data: data[6],
			}
		]
	}
	var dataADC7 = {
		labels: yAxis,
		datasets: [
			{
				label: "ADC 7",
				fill: false,
				data: data[7],
			}
		]
	}
	var dataADC8 = {
		labels: yAxis,
		datasets: [
			{
				label: "ADC 8",
				fill: false,
				data: data[8],
			}
		]
	}
	return [dataADC0,dataADC1,dataADC2,dataADC3,dataADC4,dataADC5,dataADC6,dataADC7,dataADC8];
} */

function plotChart(data,callsign,nodeid){
	nodeKey = callsign + nodeid;
	var canvasADC0 = $("#adc0-graph-" + nodeKey);
	var canvasADC1 = $("#adc1-graph-" + nodeKey);
	var canvasADC2 = $("#adc2-graph-" + nodeKey);
	var canvasADC3 = $("#adc3-graph-" + nodeKey);
	var canvasADC4 = $("#adc4-graph-" + nodeKey);
	var canvasADC5 = $("#adc5-graph-" + nodeKey);
	var canvasADC6 = $("#adc6-graph-" + nodeKey);
	var canvasADC7 = $("#adc7-graph-" + nodeKey);
	var canvasADC8 = $("#adc8-graph-" + nodeKey);
	var canvasGPIO0 = $("#gpio0-graph-" + nodeKey);
	var canvasGPIO1 = $("#gpio1-graph-" + nodeKey);
	var canvasGPIO2 = $("#gpio2-graph-" + nodeKey);
	
	var adc0Data = [], adc1Data = [], adc2Data = [], adc3Data = [], adc4Data = [];
	var adc5Data = [], adc6Data = [], adc7Data = [], adc8Data = [];
	var gpio0Data = [], gpio1Data=[],gpio2Data=[];
	var graphXaxisADC0 = [], graphXaxisADC1 = [], graphXaxisADC2 = [], graphXaxisADC3 = [];
	var graphXaxisADC4 = [], graphXaxisADC5 = [], graphXaxisADC6 = [], graphXaxisADC7 = [];
	var graphXaxisADC8 = [], graphXaxisGPIO0 = [], graphXaxisGPIO1 = [], graphXaxisGPIO2 = [];
	var time, timeString, hours, mins,secs;
	
	//window['adc' + i + 'Graph' + nodeKey].chart.config.options.elements.point.backgroundColor.push('#CB4335');
	var adc0DataPoint = [], adc1DataPoint = [], adc2DataPoint = [], adc3DataPoint = [], adc4DataPoint = [];
	var adc5DataPoint = [], adc6DataPoint = [], adc7DataPoint = [], adc8DataPoint = [];
	var gpio0DataPoint = [], gpio1DataPoint=[],gpio2DataPoint=[];
	//var adcData = [[],[],[],[],[],[],[],[],[]];
	///adc0
	$.each(data.reverse(),function(index, element){
		//Get station data here before displaying
		//console.log(element.keyid,element.adc0);
		//adc0Data.push({x:element.adc0,y:element.keyid});
		//adcData[index] = [element.adc0,element.adc1,element.adc2,element.adc3,element.adc4,element.adc5,element.adc6,element.adc7,element.adc8];
		/* adcData[0].push(element.adc0);
		adcData[1].push(element.adc1);
		adcData[2].push(element.adc2);
		adcData[3].push(element.adc3);
		adcData[4].push(element.adc4);
		adcData[5].push(element.adc5);
		adcData[6].push(element.adc6);
		adcData[7].push(element.adc7);
		adcData[8].push(element.adc8); */
		adc0DataPoint.push('#28B463');
		adc1DataPoint.push('#28B463');
		adc2DataPoint.push('#28B463');
		adc3DataPoint.push('#28B463');
		adc4DataPoint.push('#28B463');
		adc5DataPoint.push('#28B463');
		adc6DataPoint.push('#28B463');
		adc7DataPoint.push('#28B463');
		adc8DataPoint.push('#28B463');
		gpio0DataPoint.push('#28B463');
		gpio1DataPoint.push('#28B463');
		gpio2DataPoint.push('#28B463');
		/*
		adc0Data.push(element.adc0);
		adc1Data.push(element.adc1);
		adc2Data.push(element.adc2);
		adc3Data.push(element.adc3);
		adc4Data.push(element.adc4);
		adc5Data.push(element.adc5);
		adc6Data.push(element.adc6);
		adc7Data.push(element.adc7);
		adc8Data.push(element.adc8); */
		adc0Data.push(null);
		adc1Data.push(null);
		adc2Data.push(null);
		adc3Data.push(null);
		adc4Data.push(null);
		adc5Data.push(null);
		adc6Data.push(null);
		adc7Data.push(null);
		adc8Data.push(null);
		gpio0Data.push(element.gpio0);
		gpio1Data.push(element.gpio1);
		gpio2Data.push(element.gpio2);
		time = new Date(element.apepoch*1000);
		//timeString = time.getMonth() + "-" + time.getDate() + "-" + time.getFullYear() + " " + time.getHours() + ":" + time.getMinutes() + ":" + time.getSeconds();
		hours = ("0" + time.getHours()).slice(-2);
		mins = ("0" + time.getMinutes()).slice(-2);
		secs = ("0" + time.getSeconds()).slice(-2);
		timeString = hours + ":" + mins + ":" + secs;
		graphXaxisADC0.push(timeString);
		graphXaxisADC1.push(timeString);
		graphXaxisADC2.push(timeString);
		graphXaxisADC3.push(timeString);
		graphXaxisADC4.push(timeString);
		graphXaxisADC5.push(timeString);
		graphXaxisADC6.push(timeString);
		graphXaxisADC7.push(timeString);
		graphXaxisADC8.push(timeString);
		graphXaxisGPIO0.push(timeString);
		graphXaxisGPIO1.push(timeString);
		graphXaxisGPIO2.push(timeString);
		//yAxis.push(element.apepoch);
		
	});
	
/* 	for (var i = 60; i >= 0; i--){
		graphYaxis.push(i);
	} */
	
	//drawADCChart(callsign,nodeid,adcData,yAxis);
	// I should do this pragmatically. for now, brute force!
	var dataADC0 = {
		labels: graphXaxisADC0,
		datasets: [
			{
				label: "ADC 0",
				data: adc0Data,
				pointBackgroundColor: adc0DataPoint,
			}
		]
	}
	
	var dataADC1 = {
		labels: graphXaxisADC1,
		datasets: [
			{
				label: "ADC1",
				data: adc1Data,
				pointBackgroundColor: adc1DataPoint,
			}
		]
	}
	
	var dataADC2 = {
		labels: graphXaxisADC2,
		datasets: [
			{
				label: "ADC2",
				data: adc2Data,
				pointBackgroundColor: adc2DataPoint,
			}
		]
	}
	var dataADC3 = {
		labels: graphXaxisADC3,
		datasets: [
			{
				label: "ADC3",
				data: adc3Data,
				pointBackgroundColor: adc3DataPoint,
			}
		]
	}
	var dataADC4 = {
		labels: graphXaxisADC4,
		datasets: [
			{
				label: "ADC4",
				data: adc4Data,
				pointBackgroundColor: adc4DataPoint,
			}
		]
	}
	var dataADC5 = {
		labels: graphXaxisADC5,
		datasets: [
			{
				label: "ADC5",
				data: adc5Data,
				pointBackgroundColor: adc5DataPoint,
			}
		]
	}
	var dataADC6 = {
		labels: graphXaxisADC6,
		datasets: [
			{
				label: "ADC6",
				data: adc6Data,
				pointBackgroundColor: adc6DataPoint,
			}
		]
	}
	var dataADC7 = {
		labels: graphXaxisADC7,
		datasets: [
			{
				label: "ADC7",
				data: adc7Data,
				pointBackgroundColor: adc7DataPoint,
			}
		]
	}
	var dataADC8 = {
		labels: graphXaxisADC8,
		datasets: [
			{
				label: "ADC8",
				data: adc8Data,
				pointBackgroundColor: adc8DataPoint,
			}
		]
	}
	var dataGPIO0 = {
		labels: graphXaxisGPIO0,
		datasets: [
			{
				label: "GPIO 0",
				data: gpio0Data,
				pointBackgroundColor: gpio0DataPoint,
			}
		]
	}
	var dataGPIO1 = {
		labels: graphXaxisGPIO1,
		datasets: [
			{
				label: "GPIO 1",
				data: gpio1Data,
				pointBackgroundColor: gpio1DataPoint,
			}
		]
	}
	var dataGPIO2 = {
		labels: graphXaxisGPIO2,
		datasets: [
			{
				label: "GPIO2",
				data: gpio2Data,
				pointBackgroundColor: gpio1DataPoint,
			}
		]
	}
	window['adc0Graph' + nodeKey] = new Chart(canvasADC0,{
		type: 'line',
		data: dataADC0,
		options: {
			scales: {
				yAxes: [{
					ticks: {
						max:2.5,
						min: 0,
						stepsize: 1
					}
				}]
			},
			title: {
				display: true,
				text: callsign + '-' + nodeid + ' | ADC 0',
				fontSize: 24
			},
			legend: {
				display: false,
			}
		}
	});
	
	window['adc1Graph' + nodeKey] = new Chart(canvasADC1,{
		type: 'line',
		data: dataADC1,
		options: {
 			scales: {
				yAxes: [{
					ticks: {
						max:2.5,
						min: 0,
						stepsize: 1
					}
				}]
			},
			animation: false,
			title: {
				display: true,
				text: callsign + '-' + nodeid + ' | ADC 1',
				fontSize: 24
			},
			legend: {
				display: false,
			}
		}
	});
	window['adc2Graph' + nodeKey] = new Chart(canvasADC2,{
		type: 'line',
		data: dataADC2,
		options: {
			scales: {
				yAxes: [{
					ticks: {
						max: 2.5,
						min: 0,
						stepsize: 1
					}
				}]
			},
			title: {
				display: true,
				text: callsign + '-' + nodeid + ' | ADC 2',
				fontSize: 24
			},
			legend: {
				display: false,
			}
		}
	});
	window['adc3Graph' + nodeKey] = new Chart(canvasADC3,{
		type: 'line',
		data: dataADC3,
		options: {
			scales: {
				yAxes: [{
					ticks: {
						max:2.5,
						min: 0,
						stepsize: 1
					}
				}]
			},
			title: {
				display: true,
				text: callsign + '-' + nodeid + ' | ADC 3',
				fontSize: 24
			},
			legend: {
				display: false,
			}
		}
	});
	window['adc4Graph' + nodeKey] = new Chart(canvasADC4,{
		type: 'line',
		data: dataADC4,
		options: {
			scales: {
				yAxes: [{
					ticks: {
						max: 2.5,
						min: 0,
						stepsize: 1
					}
				}]
			},
			title: {
				display: true,
				text: callsign + '-' + nodeid + ' | ADC 4',
				fontSize: 24
			},
			legend: {
				display: false,
			}
		}
	});
	window['adc5Graph' + nodeKey] = new Chart(canvasADC5,{
		type: 'line',
		data: dataADC5,
		options: {
			scales: {
				yAxes: [{
					ticks: {
						max: 2.5,
						min: 0,
						stepsize: 1
					}
				}]
			},
			title: {
				display: true,
				text: callsign + '-' + nodeid + ' | ADC 5',
				fontSize: 24
			},
			legend: {
				display: false,
			}
		}
	});
	window['adc6Graph' + nodeKey] = new Chart(canvasADC6,{
		type: 'line',
		data: dataADC6,
		options: {
			scales: {
				yAxes: [{
					ticks: {
						max:27,
						min: 0,
						stepsize: 1
					}
				}]
			},
			title: {
				display: true,
				text: callsign + '-' + nodeid + ' | VCC',
				fontSize: 24
			},
			legend: {
				display: false,
			}
		}
	});
	window['adc7Graph' + nodeKey] = new Chart(canvasADC7,{
		type: 'line',
		data: dataADC7,
		options: {
			scales: {
				yAxes: [{
					ticks: {
						max:90,
						min: 0,
						stepsize: 1
					}
				}]
			},
			title: {
				display: true,
				text: callsign + '-' + nodeid + ' | CC430 Temperature',
				fontSize: 24
			},
			legend: {
				display: false,
			}
		}
	});
	window['adc8Graph' + nodeKey] = new Chart(canvasADC8,{
		type: 'line',
		data: dataADC8,
		options: {
			scales: {
				yAxes: [{
					ticks: {
						max:3.5,
						min: 0,
						stepsize: 1
					}
				}]
			},
			title: {
				display: true,
				text: callsign + '-' + nodeid + ' | 3.3V',
				fontSize: 24
			},
			legend: {
				display: false,
			}
		}
	});
	window['gpio0Graph' + nodeKey] = new Chart(canvasGPIO0,{
		type: 'line',
		data: dataGPIO0,
		options: {
			title: {
				display: true,
				text: callsign + '-' + nodeid + ' | GPIO 0',
				fontSize: 24
			},
			legend: {
				display: false,
			}
		}
	});
	window['gpio1Graph' + nodeKey] = new Chart(canvasGPIO1,{
		type: 'line',
		data: dataGPIO1,
		options: {
			title: {
				display: true,
				text: callsign + '-' + nodeid + ' | GPIO 1',
				fontSize: 24
			},
			legend: {
				display: false,
			}
		}
	});
	window['gpio2Graph' + nodeKey] = new Chart(canvasGPIO2,{
		type: 'line',
		data: dataGPIO2,
		options: {
			title: {
				display: true,
				text: callsign + '-' + nodeid + ' | GPIO 2',
				fontSize: 24
			},
			legend: {
				display: false,
			}
		}
	});
	
}

function DD2DDeg(latdeg, latdec, latdir, londeg, londec, londir){
	// Should probably round values
	var latitude;
	var longitude;
	latitude = (Math.round((latdeg + latdec/60)*10000)/10000).toFixed(4);
	longitude = (Math.round((londeg + londec/60)*10000)/10000).toFixed(4);
	//console.log([latitude,latdir,longitude,londir]);
	return [latitude,latdir,longitude,londir];
}

function knots2MetersPerSec(knots){
	var result;
	result = (Math.round((knots*0.514444)*100)/100).toFixed(2);
	return result	
}

function relativePosition(locNodeGeoJSON,remNodeGeoJSON){
	var elevation;
	
	// Calculate distance to node from receiving node
	var distance = turf.distance(locNodeGeoJSON, remNodeGeoJSON, "kilometers");
	distance = Math.round(distance*100)/100;
	
	// Calculate bearing to node from receiving node
	var bearing = turf.bearing(locNodeGeoJSON, remNodeGeoJSON);
	if(bearing < 0){
		bearing = 360 + bearing; // since bearing is negative, subract by adding for 0-360
	}
	bearing = Math.round(bearing*10)/10;
	
	// Calculate remote node elevation above horizon relative to receiving node
	var elevRemote = remNodeGeoJSON.geometry.coordinates[2];
	var elevLocal = locNodeGeoJSON.geometry.coordinates[2];
	var elevation = Math.atan((elevRemote - elevLocal)/distance)*(180/Math.PI); // straight line
	elevation = Math.round(elevation*10)/10;
	
	return [distance,bearing, elevation];
}

function calculateHorizon(GeoJSON){
	//calculate the horizon, altitude in meters, distance in km
	var radiusEarth = 6371; // km along a perfesctly spherical Earth
	var altitude = GeoJSON.geometry.coordinates[2];
	altitude = altitude/1000; // convert meters to km
	var horizon = Math.sqrt(altitude*(2*radiusEarth+altitude)); // km
	horizon = Math.round(horizon*100)/100;
	
	return horizon;
}

function createGEOJSONLocation(location,altitude,name){
	
	// Create float values for coordinates based on direction
	if(location[1] == "S"){
		latitude = parseFloat(location[0] * -1);
	} else {
		latitude = parseFloat(location[0]);
	}
	if(location[3] == "W"){
		longitude = parseFloat(location[2] * -1);
	} else {
		longitude = parseFloat(location[2]);
	}
	
	//Ensure altitude is a float
	altitude = parseFloat(altitude);
	var geoJSON = {
		"type": 'Feature',
		"properties": {'name': name},
		"geometry":{
			"type": 'Point',
			"coordinates": [longitude,latitude,altitude]	
		}
	};
	return geoJSON;
}
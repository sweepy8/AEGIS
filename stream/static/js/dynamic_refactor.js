// Trips Page Tools
// Created: 7/30/2025
// Updated: 8/30/2025

/**
 * TODO:
 *      Dynamically get json file name from trip
 *      On trip change, reset dropdown menus
 *      CSS changes
 *      Fetch videos!
 *      Add window resize event listener to relayout each active plot
 */

const telPlotLabels = {
    "Raspberry Pi Uptime":              ".rpi.uptime_s",
    "Raspberry Pi CPU Utilization":     ".rpi.cpu_util_pct",
    "Raspberry Pi Memory Utilization":  ".rpi.mem_util_pct",
    "Raspberry Pi Available Storage":   ".rpi.storage_available_mb",
    "Raspberry Pi Temperature":         ".rpi.temp_c",
    "Raspberry Pi Core Current":        ".rpi.vdd_core_a",
    "Raspberry Pi Core Voltage":        ".rpi.vdd_core_v",

    "Arduino Uptime":                   ".arduino.uptime_s",

    "LiDAR Connected":                  ".lidar.connected",
    "LiDAR Scanning":                   ".lidar.scanning",
    "LiDAR Scan Percentage":            ".lidar.scan_pct",
    "LiDAR Saving File":                ".lidar.saving_file",
    "LiDAR Motor Position":             ".lidar.motor_pos_deg",

    "Camera Connected":                 ".camera.connected",
    "Camera Recording":                 ".camera.recording",
    "Camera Streaming":                 ".camera.streaming",
    "Last Camera File":                 ".camera.last_file",

    "Front Left Motor Voltage":         ".motors.front_left.voltage_v",
    "Front Left Motor Current":         ".motors.front_left.current_a",
    "Front Left Motor RPM":             ".motors.front_left.rpm",
    "Mid Left Motor Voltage":           ".motors.mid_left.voltage_v",
    "Mid Left Motor Current":           ".motors.mid_left.current_a",
    "Mid Left Motor RPM":               ".motors.mid_left.rpm",
    "Rear Left Motor Voltage":          ".motors.rear_left.voltage_v",
    "Rear Left Motor Current":          ".motors.rear_left.current_a",
    "Rear Left Motor RPM":              ".motors.rear_left.rpm",
    "Front Right Motor Voltage":        ".motors.front_right.voltage_v",
    "Front Right Motor Current":        ".motors.front_right.current_a",
    "Front Right Motor RPM":            ".motors.front_right.rpm",
    "Mid Right Motor Voltage":          ".motors.mid_right.voltage_v",
    "Mid Right Motor Current":          ".motors.mid_right.current_a",
    "Mid Right Motor RPM":              ".motors.mid_right.rpm",
    "Rear Right Motor Voltage":         ".motors.rear_right.voltage_v",
    "Rear Right Motor Current":         ".motors.rear_right.current_a",
    "Rear Right Motor RPM":             ".motors.rear_right.rpm",

    "LiDAR Ultrasonic Distance":        ".ultrasonics.lidar_cm",
    "Left Ultrasonic Distance":         ".ultrasonics.left_cm",
    "Center Ultrasonic Distance":       ".ultrasonics.center_cm",
    "Right Ultrasonic Distance":        ".ultrasonics.right_cm",
    "Rear Ultrasonic Distance":         ".ultrasonics.rear_cm",

    "UGV Battery Remaining":            ".ugv.battery.capacity_pct",
    "UGV Battery Voltage":              ".ugv.battery.voltage_v",
    "UGV Battery Current":              ".ugv.battery.current_a",
    "Headlights":                       ".ugv.headlights",
    "Ambient Temperature":              ".ugv.ambient_temp_c",
    "Earth Relative Humidity":          ".ugv.relative_hum_pct",
    "Ambient Visible Light":            ".ugv.ambient_light_l",
    "Ambient Infrared Light":           ".ugv.ambient_infrared_l"
}

// I'm too lazy to reverse telPlotLabels, if you do that you can pull this
const telPlotLabelsReversed = Object.fromEntries(
    Object.entries(telPlotLabels).map(([key, value]) => [value, key])
);

const telPlotMaps = {
    "Raspberry Pi Util + Temp": [
        ".rpi.uptime_s",
        ".rpi.cpu_util_pct",
        ".rpi.mem_util_pct",
        ".rpi.storage_available_mb",
        ".rpi.temp_c",
        ".rpi.vdd_core_a",
        ".rpi.vdd_core_v",
    ],
    "Ultrasonic Sensor Distances": [
        ".ultrasonics.lidar_cm",
        ".ultrasonics.left_cm",
        ".ultrasonics.center_cm",
        ".ultrasonics.right_cm",
        ".ultrasonics.rear_cm",
    ],
    // "LiDAR Scan Information": [
    //     ".lidar.connected",
    //     ".lidar.scanning",
    //     ".lidar.scan_pct",
    //     ".lidar.saving_file",
    //     ".lidar.motor_pos_deg",
    // ],
    // "Camera Information": [
    //     ".camera.connected",
    //     ".camera.recording",
    //     ".camera.streaming",
    // ],
    "Motor Voltages": [
        ".motors.front_left.voltage_v",
        ".motors.mid_left.voltage_v",
        ".motors.rear_left.voltage_v",
        ".motors.front_right.voltage_v",
        ".motors.mid_right.voltage_v",
        ".motors.rear_right.voltage_v",
    ],
    "Motor Currents": [
        ".motors.front_left.current_a",
        ".motors.mid_left.current_a",
        ".motors.rear_left.current_a",
        ".motors.front_right.current_a",
        ".motors.mid_right.current_a",
        ".motors.rear_right.current_a",
    ],
    "Motor RPMs": [
        ".motors.front_left.rpm",
        ".motors.mid_left.rpm",
        ".motors.rear_left.rpm",
        ".motors.front_right.rpm",
        ".motors.mid_right.rpm",
        ".motors.rear_right.rpm",
    ],
    "Battery Information": [
        ".ugv.battery.capacity_pct",
        ".ugv.battery.voltage_v",
        ".ugv.battery.current_a",
    ],
    "Ambient Temp + ERH": [
        ".ugv.ambient_temp_c",
        ".ugv.relative_hum_pct",
    ],
    "Ambient Light + Headlights": [
        ".ugv.headlights",
        ".ugv.ambient_light_l",
        ".ugv.ambient_infrared_l",
    ]
}

var telemetry = '';
var trip = '';
var scanNames = '';

async function fetchTrips() {
    /**
     * Pulls all Trip folder directories to be added as selections
     * 
     * @throws Potential Errors: Failed to retrieve folders for Trips, 
     *      failed to retrieve select tag to put trip selections in, 
     *      error adding trips to selection.
     */

    const response = await fetch('/trips'); // fetchs data from python as json
    if (!response.ok) throw new Error(`HTTP error ${response.status}`);

    const folders = await response.json(); // data from json return

    // Sort trip folders by length first then by alphabet
    // if done just alphabetically Trip_19 would go between Trip_1 and Trip_2
    folders.sort((a, b) => {
        if (a.length !== b.length) {
            return a.length - b.length;
        }
        return a.localeCompare(b);
    });
    console.log('Fetched trips: ', folders);

    // gets the list by referencing its id in html
    const list_trips = document.getElementById('trip_select');
    if (!list_trips) {
        console.error('trip_select <select> not found');
        return;
    }

    // creates new list with updated trips
    if(Array.isArray(folders)) {
        folders.forEach(trip => {
            const option = document.createElement('option'); // creates option element
            option.textContent = trip;
            list_trips.appendChild(option); // adds option element to select tag
        });
    } else {
        list_trips.innerHTML = `<option>Error loading trips</option>`; // error message
    }
}

async function fetchTelemetry(trip_name) {
    /**
     * Attempts to retrieve JSON file containing a trips telemetry data
     * 
     * @param {string} trip_name - Name of the trip
     * @returns Global telemetry data and LiDAR points
     * @throws Potential Errors: JSON file fetch failure console log, error fetching json and lidar points console error.
     */

    trip = trip_name;
    try {
        const response = await fetch(`/static/trips/${trip_name}/tel_20250830_111603.json`);
        if (!response.ok) {
            console.warn('Failed to load telemetry!');
        }
        telemetry = await response.json();
    } catch (error) {
        console.error('Fetch error:', error);
    }

    scanNames = await getScanNames(trip_name);

    return telemetry;
}

async function getScanNames(trip_name) {
    try {
        const response = await fetch(`/scanFiles?trip=${encodeURIComponent(trip_name)}`);
        const data = await response.json();
        if (Array.isArray(data)) {
            return data; // This is the returned array of scan file names
        } else {
            console.error("Error from server:", data.error);
            return [];
        }
    } catch (err) {
        console.error("Fetch error:", err);
        return [];
    }
}

// Plot Selection and call Section
function populateSubmenu(type, submenu) {
    /**
     * Creates plot div selections once a type is selected.
     * 
     * @param {string} type - Type or category of plots for selection.
     * @param {node} submenu - Node or element that is the selection tag where options will be added.
     */

    switch (type) {
        case "Video":
            // THIS SHOULD GET VIDEOS AND APPEND THEM, SAME AS LiDAR BELOW
            break;
        case "LiDAR":
            scanNames.forEach(name => {
                const cloud = document.createElement("option");
                cloud.textContent = name;
                submenu.appendChild(cloud);
            });
            break;
        case "Graph":
            Object.keys(telPlotMaps).forEach(label => {
                submenu.appendChild(new Option(label));
            });
            break;
    }
}

function purgePlot(plotName) {
    /**
     * Removes all plots or elements that might be in a plot div.
     * 
     * @param {string} plotName - Div Id that refers to one of the 3 plot locations.
     */

    const plot = document.getElementById(plotName);

    if (plot) {
        const video_img = document.getElementById(`video_${plotName}`);

        // Removes video or image if one is there
        if (video_img) {
            plot.removeChild(video_img);
        }
        // Removes plot if one is there
        Plotly.purge(plot);

        plot.style.backgroundImage = "url('../static/images/CSUN_logo.png')";
        plot.style.backgroundSize = "contain";
        plot.style.backgroundRepeat = "no-repeat";
        plot.style.backgroundPosition = "center center";
    }
}

// This can be made anonymous, only used for generatePlot
function coerceToNumeric(val) {
    if (val === undefined || val === null) return null; // let Plotly skip
    if (typeof val === 'boolean') return val ? 1 : 0;   // map booleans
    if (typeof val === 'number') return val;            // keep numbers
    const n = Number(val);                              // string → number
    return Number.isFinite(n) ? n : null;               // else skip
}

async function generatePlot(plotId, plotLabel) {
    /**
     * Plots a function in one of the 3 plot divs.
     * 
     * @param {string} plotLabel - Label of plot to be displayed.
     * @param {string} plotId - Id of the div that will display the plot.
     */

    if (telPlotMaps.hasOwnProperty(plotLabel)) {
        var traces = [];

        telPlotMaps[plotLabel].forEach(field => {
            let trace = {
                x: [],
                y: [],
                type: 'scatter',
                mode: 'lines',
                name: telPlotLabelsReversed[field]
            };

            for (let i = 0; i < telemetry.telemetry.length; i++) {
                trace.x.push(i);
                val = JSON.stringify(eval(`telemetry.telemetry[${i}]` + field));
                trace.y.push(coerceToNumeric(val));
            }
            traces.push(trace);
        });

        const layout = {
            margin: {t: 20, b: 20, l: 20, r: 0},
            yaxis: {rangemode: 'tozero'}
        };

        Plotly.newPlot(plotId, traces, layout);
    }
}

async function pointCloudPlot(plotName, pc_name) {
    /**
     * Creates a Plotly plot containing the LiDAR point cloud or '3D scatter plot'.
     * 
     * @param {string} plotName - Id of the div to display the Plotly point cloud.
     */

    var ptsArr = '';
    try {
        ptsArr = await getPoints(`/static/trips/${trip}/${pc_name}.txt`);
    } catch (error) {
        console.error('Fetch error point cloud:', error);
    }

    var intensity = getDimFromPoints(ptsArr,3);
    var points = {
    x:getDimFromPoints(ptsArr, 0),
    y:getDimFromPoints(ptsArr, 1),
    z:getDimFromPoints(ptsArr, 2),
    mode: 'markers',
    marker: {
        size: 1,
        color: intensity,
        colorscale: 'Jet',
        showscale: true,
    },
    type: 'scatter3d',
    hoverinfo: 'none',
    };

    var data = [points];
    var layout = {
        margin: { l: 0, r: 0, b: 0, t: 0 },
        scene: {
            aspectratio: { x: 1, y: 1, z: 1 },
            camera: {
                eye: {x: 1, y: 1, z: 0.5},   // Camera position
                center: {x: 0, y: 0, z: 0}, // Point the camera looks at
                up: {x: 0, y: 0, z: 1}      // Up direction
            }
        },
        paper_bgcolor: 'black'};

    Plotly.newPlot(plotName, data, layout);
}

async function getPoints(filename) {
    /**
     * Gets all the point cloud data points and separates them into organized 
     * x y z intensity columns.
     * 
     * @param {string} filename - filepath to the text file with all the point 
     *      data.
     * @returns {float32array} points - All data points organized into columns 
     *      of x y z intensity.
     */

    let points = [];

    const response = await fetch(filename);
    if (!response.ok) {
        throw new Error(`Response status; ${response.status}`);
    }
    const data = await response.text() + '';
    const lines = data.split('\n');

    lines.forEach(line => {
    if (!(line.match(".[A-Z]."))) {  // If string line doesn't have any letters
        const dimStrs = line.split(' ');

        let point = [];
        for (let i = 0; i < 4; i++) {
            point.push(parseFloat(dimStrs[i]));
        }

        points.push(point);
    }
    });

    return points;
}

function getDimFromPoints(points, index) {
    /**
     * Creates a single array for one of the columns x y z intensity from getPoints.
     * 
     * @param {Float32Array} points - All of the point data for a point cloud .
     * @param {int} index - Index for the column to extract.
     * @returns {float32array} 1 dimensional float array containing one of the following: x y z intensity.
     */

    let dim = [];
    points.forEach(point => {
        dim.push(point[index]);
    });

    return dim;
}

function toggleFullScreen(plotId) {
    /**
     * Toggles full screen plot on click (from HTML)
     * 
     * @param {string} plotId - Plot to toggle
     */
    const plot = document.getElementById(plotId);
    plot.classList.toggle('fullscreen_div');
    Plotly.relayout(plot, {autosize: true});
}

document.addEventListener("DOMContentLoaded", async function() {

    // Refresh plots and fetch telemetry when user selects a trip
    const tripSelector = document.getElementById("trip_select");
    tripSelector.addEventListener("change", async function() {
        purgePlot("plot1"); 
        purgePlot("plot2"); 
        purgePlot("plot3");
        telemetry = await fetchTelemetry(tripSelector.value);
    });
    
    let plotTypeSelectors = [];
    plotTypeSelectors.push(document.getElementById("plot_1_type"));
    plotTypeSelectors.push(document.getElementById("plot_2_type"));
    plotTypeSelectors.push(document.getElementById("plot_2_type"));

    let plotDataSelectors = [];
    plotDataSelectors.push(document.getElementById("plot_select_1"));
    plotDataSelectors.push(document.getElementById("plot_select_2"));
    plotDataSelectors.push(document.getElementById("plot_select_3"));

    for (let i = 0; i < plotTypeSelectors.length; i++) {
        let typeSelector = plotTypeSelectors[i];
        let dataSelector = plotDataSelectors[i];

        // When users select a new type of plot, clear plot and refresh submenu
        typeSelector.addEventListener("change", function() {
            purgePlot(`plot${i+1}`);
            const submenu = document.getElementById(`plot_select_${i+1}`);
            submenu.innerHTML = '';
            const submenuOption = document.createElement("option");
            submenuOption.textContent = "Choose a Plot";
            submenu.appendChild(submenuOption); 
            populateSubmenu(typeSelector.value, submenu);
        });
        // When users select new data to plot, refresh plot
        dataSelector.addEventListener("change", function() {
            purgePlot(`plot${i+1}`);
            switch (typeSelector.value) {
                case "LiDAR":
                    pointCloudPlot(`plot${i+1}`, dataSelector.value);
                    break;
                case "Video":
                    // camera spot for mp4 select
                    break;
                case "Graph":
                    generatePlot(`plot${i+1}`, dataSelector.value);
                    break;
            }
        });
    }
});

fetchTrips(); // runs on page load
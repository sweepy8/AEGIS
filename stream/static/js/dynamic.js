// Trips Page Tools
// Created: 7/30/2025
// Updated: 8/30/2025

/**
 * TODO:
 *      CSS changes
 *      Fetch videos!
 *      Change rpi available storage to a percentage so it fits
 *      Add option to change colormap?
 *      Why does the comms lab need a z compression of 3x???
 */

const TRIPS_FOLDER = '/static/trips';

let tripName = '';
let telemetry = '';
let scanNames = '';
let videoNames = '';

const telPlotLabels = {
    ".rpi.uptime_s":                    "Raspberry Pi Uptime [s]",
    ".rpi.cpu_util_pct":                "Raspberry Pi CPU Utilization [%]",
    ".rpi.mem_util_pct":                "Raspberry Pi Memory Utilization [%]",
    ".rpi.storage_available_mb":        "Raspberry Pi Available Storage",
    ".rpi.temp_c":                      "Raspberry Pi Temperature [C]",
    ".rpi.vdd_core_a":                  "Raspberry Pi Core Current [A]",
    ".rpi.vdd_core_v":                  "Raspberry Pi Core Voltage [V]",

    ".arduino.uptime_s":                "Arduino Uptime [s]",

    ".lidar.connected":                 "LiDAR Connected",
    ".lidar.scanning":                  "LiDAR Scanning",
    ".lidar.scan_pct":                  "LiDAR Scan Percentage [%]",
    ".lidar.saving_file":               "LiDAR Saving File",
    ".lidar.motor_pos_deg":             "LiDAR Motor Position [deg]",

    ".camera.connected":                "Camera Connected",
    ".camera.recording":                "Camera Recording",
    ".camera.streaming":                "Camera Streaming",
    ".camera.last_file":                "Last Camera File",

    ".motors.front_left.voltage_v":     "Front Left Motor Voltage [V]",
    ".motors.front_left.current_a":     "Front Left Motor Current [A]",
    ".motors.front_left.rpm":           "Front Left Motor Speed [RPM]",
    ".motors.mid_left.voltage_v":       "Mid Left Motor Voltage [V]",
    ".motors.mid_left.current_a":       "Mid Left Motor Current [A]",
    ".motors.mid_left.rpm":             "Mid Left Motor Speed [RPM]",
    ".motors.rear_left.voltage_v":      "Rear Left Motor Voltage [V]",
    ".motors.rear_left.current_a":      "Rear Left Motor Current [A]",
    ".motors.rear_left.rpm":            "Rear Left Motor Speed [RPM]",
    ".motors.front_right.voltage_v":    "Front Right Motor Voltage [V]",
    ".motors.front_right.current_a":    "Front Right Motor Current [A]",
    ".motors.front_right.rpm":          "Front Right Motor Speed [RPM]",
    ".motors.mid_right.voltage_v":      "Mid Right Motor Voltage [V]",
    ".motors.mid_right.current_a":      "Mid Right Motor Current [A]",
    ".motors.mid_right.rpm":            "Mid Right Motor Speed [RPM]",
    ".motors.rear_right.voltage_v":     "Rear Right Motor Voltage [V]",
    ".motors.rear_right.current_a":     "Rear Right Motor Current [A]",
    ".motors.rear_right.rpm":           "Rear Right Motor Speed [RPM]",

    ".ultrasonics.lidar_cm":            "LiDAR Ultrasonic Distance [cm]",
    ".ultrasonics.left_cm":             "Left Ultrasonic Distance [cm]",
    ".ultrasonics.center_cm":           "Center Ultrasonic Distance [cm]",
    ".ultrasonics.right_cm":            "Right Ultrasonic Distance [cm]",
    ".ultrasonics.rear_cm":             "Rear Ultrasonic Distance [cm]",

    ".ugv.battery.capacity_pct":        "UGV Battery Remaining [%]",
    ".ugv.battery.voltage_v":           "UGV Battery Voltage [V]",
    ".ugv.battery.current_a":           "UGV Battery Current [A]",
    ".ugv.headlights":                  "Headlights",
    ".ugv.ambient_temp_c":              "Ambient Temperature [C]",
    ".ugv.relative_hum_pct":            "Earth Relative Humidity [%]",
    ".ugv.ambient_light_l":             "Ambient Visible Light [lm]",
    ".ugv.ambient_infrared_l":          "Ambient Infrared Light [lm]"
};

// Map of submenu plot and all traces that it will show. To make a new option,
// just add a title with an array containing all traces
const telPlotMaps = {
    "Raspberry Pi Util + Temp": [
        //".rpi.uptime_s",
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
    "Motor Speeds": [
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

async function getTrips() {
    /**
     * Pulls all trip folder directories and adds them to trip selector
     * 
     * @throws Potential Errors: Failed to retrieve folders for Trips.
     */

    // Flask route to retrieve JSON object containing all trip folder paths
    const response = await fetch('/getTripFolders');
    if (!response.ok) throw new Error(`HTTP error ${response.status}`);
    const folders = await response.json();

    folders.sort((a, b) => {
        return a.length !== b.length ? a.length - b.length : a.localeCompare(b);
    });

    // Populates trip selector with found trips
    const tripSelector = document.getElementById('trip_select');
    if (Array.isArray(folders)) {
        folders.forEach(tripName => {
            const option = document.createElement('option');
            option.textContent = tripName;
            tripSelector.appendChild(option);
        });
    } else {
        tripSelector.innerHTML = '<option> Error Loading Trips </option>';
    }
}

async function getVideoNames(tripFolder) {
    try {
        const response = await fetch(`/getVideoFiles?trip=${encodeURIComponent(tripFolder)}`);
        const videoNames = await response.json();
        if (Array.isArray(videoNames)) {
            return videoNames;
        } else {
            console.error("Error from server:", videoNames.error);
            return [];
        }
    } catch (err) {
        console.error("Fetch error:", err);
        return [];
    }
}

async function getScanNames(tripFolder) {
    try {
        const response = await fetch(`/getScanFiles?trip=${encodeURIComponent(tripFolder)}`);
        const scanNames = await response.json();
        if (Array.isArray(scanNames)) {
            console.log(scanNames);
            return scanNames;
        } else {
            console.error("Error from server:", scanNames.error);
            return [];
        }
    } catch (err) {
        console.error("Fetch error:", err);
        return [];
    }
}

async function getTelemetryJSON(tripFolder) {
    /**
     * Pulls telemetry data from JSON file inside current trip folder
     * 
     * @param {string} tripFolder - Name of the trip folder
     * @returns Global telemetry data and LiDAR points
     * @throws Potential Errors: JSON file fetch failure console log, 
     *          error fetching json and lidar points console error.
     */

    try {
        // Flask route to retrieve JSON object containing JSON files in folder
        const fileResponse = await fetch(
            `/getTelemetryFile?trip=${encodeURIComponent(tripFolder)}`);
        if (!fileResponse.ok) {
            console.warn('Failed to fetch telemetry!');
            return {};
        }
        const telFile = (await fileResponse.json())[0];

        // Get telemetry data
        const dataResponse = await fetch(
            `${TRIPS_FOLDER}/${tripFolder}/${telFile}`);
        if (!dataResponse.ok) {
            console.warn('Failed to load telemetry!');
            return {};
        }
        telemetry = await dataResponse.json();
    } catch (error) {
        console.error('Fetch error:', error);
        return {};
    }

    return telemetry;
}

function populateSubmenu(category, submenuId, options) {
    /**
     * Populates plot submenu with options depending on plot category (Video, 
     * LiDAR, Graph).
     * 
     * @param {string} category - Category of plots for selection.
     * @param {node} submenu - Element to which options will be added.
     */

    // Flush submenu first
    const submenu = document.getElementById(submenuId);
    submenu.replaceChildren();

    switch (category) {
        case "Video":
            if (Array.isArray(options) && options.length > 0) {
                options.forEach(label => {
                    submenu.appendChild(new Option(label));
                });
            } else submenu.appendChild(new Option("No Videos to Display"));
            break;
        case "LiDAR":
            if (Array.isArray(options) && options.length > 0) {
                options.forEach(label => {
                    submenu.appendChild(new Option(label));
                });
            } else submenu.appendChild(new Option("No Scans to Display"));
            break;
        case "Graph":
            if (Object.keys(telemetry).length > 0) {
                Object.keys(telPlotMaps).forEach(label => {
                    submenu.appendChild(new Option(label));
                });
            }
            else submenu.appendChild(new Option("No Telemetry to Display"));
            break;
    }
}

function purgePlot(plotId) {
    /**
     * Removes all plots or elements that might be in a plot div.
     * 
     * @param {string} plotId - Div Id that refers to one of the 3 plot locations.
     */

    const plot = document.getElementById(plotId);

    // Removes video or image if one is there
    plot.replaceChildren();
}

function addFullscreenButton(plotId) {
    const plot = document.getElementById(plotId);

    const fullscreenButton = document.createElement("button");
    fullscreenButton.style.position = "absolute";
    fullscreenButton.style.left = "0";
    fullscreenButton.style.top = "10px";
    fullscreenButton.style.margin = "5px";

    const icon = document.createElement("i");
    icon.className = "fa-regular fa-square-plus fa-2xl";
    icon.style.filter = "invert(100%)";

    fullscreenButton.appendChild(icon);

    fullscreenButton.addEventListener("click", () => {
        plot.classList.toggle('fullscreen_div');
        Plotly.relayout(plot, {autosize: true});
    });

    plot.append(fullscreenButton);
}

async function makeVideoPlot(plotId, videoName) {

    if (!videoNames.includes(videoName)) return;

    const plot = document.getElementById(plotId);

    const video = document.createElement("video");
    video.src = `${TRIPS_FOLDER}/${tripName}/${videoName}`;
    video.controls = true;
    video.muted = true;
    video.autoplay = true;

    video.style.width = "100%";
    video.style.height = "100%";
    video.style.objectFit = "contain";
    video.style.background = "black";

    plot.append(video);
}

async function makeScanPlot(plotId, scanName) {
    const start = performance.now();

    let scanData;
    try {
        const result = await fetch(`${TRIPS_FOLDER}/${tripName}/${scanName}`);
        if (!result.ok) throw new Error(`Error from server: ${result.status}`);
        scanData = await result.text();
    } catch (err) {
        console.error("Fetch error: ", err);
        return;
    }

    const xVals = [], yVals = [], zVals = [], iVals = [];

    let cloud = scanData.split('\n');

    // Downsample large clouds
    /**
     *  250k (home PC, chrome): 1-1.5 s
     *  500k (home PC, chrome): 2-2.5 s (some WebGL context lost issues)
     *  500k (home PC, firefox): 3-4.5 s
     * 
     */
    const targetSize = 250000;
    if (cloud.length > targetSize) {
        cloud = cloud.filter(() => Math.random() < targetSize/cloud.length);
    }

    for (let i = 0; i < cloud.length; i++) {
        const pt = cloud[i];
        if (!pt) continue;

        const ptArr = pt.split(' ');

        xVals.push(ptArr[0]);
        yVals.push(ptArr[1]);
        zVals.push(ptArr[2]);
        iVals.push(ptArr[3]);
    }

    // Should provide optimization for WebGL --> Plotly
    const x = new Float32Array(xVals);
    const y = new Float32Array(yVals);
    const z = new Float32Array(zVals);
    const i = new Float32Array(iVals);

    const trace = {
        type: 'scatter3d',
        mode: 'markers',
        x, y, z,
        marker: {
            size: 1,
            color: i,
            colorscale: 'Jet',
            showscale: false,
        },
        hoverinfo: 'none',
    };

    const layout = {
        paper_bgcolor: "black",
        margin: { l: 0, r: 0, t: 0, b: 0 },
        scene: {
        aspectratio: { x: 1, y: 1, z: 1},
        camera: {
            eye: { x: 1, y: 1, z: 0.5 },
            center: { x: 0, y: 0, z: 0 },
            up: { x: 0, y: 0, z: 1 }
        },
        xaxis: { visible: false },
        yaxis: { visible: false },
        zaxis: { visible: false }
        }
    };

    Plotly.newPlot(plotId, [trace], layout, {responsive: true});
    
    addFullscreenButton(plotId);

    const end = performance.now();
    const elapsed = Math.round(end-start);
    console.log(`Displayed ${scanName} in ${elapsed} ms`);
}

/**
 * Plots a function in one of the 3 plot divs. 
 * 
 * Gets all grouped traces associated with the plotLabel in the telPlotMaps 
 * object and builds them, then generates Plotly plot for them.
 * 
 * @param {string} plotLabel - Label of plot to be displayed.
 * @param {string} plotId - Id of the div that will display the plot.
 */
async function makeTelemetryPlot(plotId, plotLabel) {
    // Validates JSON string as number
    const toNum = val => {
        if (val == null) return null;
        const n = Number(val);      // Strings, undefined become NaN
        return Number.isFinite(n) ? n : null;
    };

    // Fucking wizardry
    const getAtPath = (obj, dotPath) =>
        dotPath.replace(/^\./, '').split('.').reduce((o, k) => o[k], obj);

    const traces = [];

    // X [time] should be same for all traces, so just make it once
    let x = Array.from({length: telemetry.telemetry.length}, (_, i) => i);

    telPlotMaps[plotLabel].forEach(field => {
        const y = telemetry.telemetry.map(row => toNum(getAtPath(row, field)));

        let trace = {
            x, y,
            type: 'scatter', mode: 'lines', connectgaps: false,
            name: telPlotLabels[field],
        };

        let traceName = telPlotLabels[field].split(" ");
        let hoverLabel = null;
        switch (plotLabel) {
            case "Raspberry Pi Util + Temp":
                hoverLabel = traceName.slice(2).join(" ");
                hoverLabel += ": %{y} <extra></extra>";
                trace.hovertemplate = hoverLabel;
                break;
            case "Ultrasonic Sensor Distances":
                hoverLabel = traceName[0];
                hoverLabel += ": %{y} cm <extra></extra>";
                trace.hovertemplate = hoverLabel;
                break;
            case "Motor Voltages":
            case "Motor Currents":
            case "Motor Speeds":
                hoverLabel = traceName.slice(0,2).join(" ");
                hoverLabel += ": %{y} <extra></extra>";
                trace.hovertemplate = hoverLabel;
                break;

        };

        traces.push(trace);
    });

    const layout = {
        plot_bgcolor: 'black',
        paper_bgcolor: 'black',
        font: {color: 'white'},
        margin: {t: 0, b: 20, l: 20, r: 0},
        hovermode: "x unified",
        hoverlabel: {bgcolor: 'black'},
        xaxis: {title: "Time [s]"},
        yaxis: {rangemode: 'tozero'},
        legend: {
            x: 0.5, y: -0.07, 
            xanchor: 'center', orientation: 'h', 
            font: {size: 10}
        }
    };

    Plotly.newPlot(plotId, traces, layout, {responsive: true});

    addFullscreenButton(plotId);
}

document.addEventListener("DOMContentLoaded", async function() {
    
    let plotTypeSelectors = [];
    plotTypeSelectors.push(document.getElementById("plot_1_type"));
    plotTypeSelectors.push(document.getElementById("plot_2_type"));
    plotTypeSelectors.push(document.getElementById("plot_3_type"));

    let plotDataSelectors = [];
    plotDataSelectors.push(document.getElementById("plot_select_1"));
    plotDataSelectors.push(document.getElementById("plot_select_2"));
    plotDataSelectors.push(document.getElementById("plot_select_3"));

    // Refresh plots and fetch telemetry and scans when user selects a trip
    const tripSelector = document.getElementById("trip_select");
    tripSelector.addEventListener("change", async function() {
        purgePlot("plot1"); purgePlot("plot2"); purgePlot("plot3");

        tripName = tripSelector.value;
        videoNames = await getVideoNames(tripSelector.value);
        scanNames = await getScanNames(tripSelector.value);
        telemetry = await getTelemetryJSON(tripSelector.value);

        plotTypeSelectors[0].dispatchEvent(new Event("change"));
        plotTypeSelectors[1].dispatchEvent(new Event("change"));
        plotTypeSelectors[2].dispatchEvent(new Event("change"));

    });

    for (let i = 0; i < plotTypeSelectors.length; i++) {
        let typeSelector = plotTypeSelectors[i];
        let dataSelector = plotDataSelectors[i];

        // When users select a new type of plot, clear plot and refresh submenu
        typeSelector.addEventListener("change", function() {
            const submenu = document.getElementById(`plot_select_${i+1}`);
            purgePlot(`plot${i+1}`); submenu.replaceChildren();
            
            let choices;
            if (typeSelector.value == "Video") choices = videoNames;
            if (typeSelector.value == "LiDAR") choices = scanNames;
            if (typeSelector.value == "Graph") choices = undefined;
            populateSubmenu(typeSelector.value, `plot_select_${i+1}`, choices);

            dataSelector.dispatchEvent(new Event("change"));
        });

        // When users select new data to plot, do what they tell you
        dataSelector.addEventListener("change", function() {
            purgePlot(`plot${i+1}`);
            switch (typeSelector.value) {
                case "LiDAR":
                    if (dataSelector.value == "No Scans to Display") return;
                    makeScanPlot(`plot${i+1}`, dataSelector.value);
                    break;
                case "Video":
                    if (dataSelector.value == "No Videos to Display") return;
                    makeVideoPlot(`plot${i+1}`, dataSelector.value);
                    break;
                case "Graph":
                    if (dataSelector.value == "No Data to Display") return;
                    makeTelemetryPlot(`plot${i+1}`, dataSelector.value);
                    break;
            }
        });
    }
});

getTrips(); // runs on page load
// Telemetry Viewer Data/Visual
// Created: 7/30/2025

// Adding a new plot or video instructions
// Step 1: Add a function that either creates a Plotly plot or video tag, examples of both in the plot section.
// Step 2: Add the selected option call for that new plot in the plotFunction() and add its function call, examples in plotFunction().
//              Doing this will add a call to make the plot when its option is selected.
// Step 3: Add the option to select in the plotTypeOptions() function.
//              Doing this will add the option as a possible plot to make in each plot header.

async function fetchTrips() {
    /**
     * Pulls all Trip folder directories to be added as selections
     * 
     * @throws Potential Errors: Failed to retrieve folders for Trips, failed to retrieve select tag to put trip selections in, error adding trips to selection.
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
    // console.log('Fetched trips: ', folders);

    // gets the list by referencing its id in html
    const list_trips = document.getElementById('trip_select');
    if (!list_trips) {
        console.error('trip_select <select> not found');
        return;
    }

    // creates new list with updates trips
    if(Array.isArray(folders)) {
        folders.forEach(trip => {
            const option = document.createElement('option'); // creates option element
            option.textContent = trip;
            list_trips.appendChild(option); // adds option element to select tag
        });
    } else {
        list_trips.innerHTML = `<option>Error loading trips</option>`; // error message
    }

    // Set default plot images
    selectPlot1("--Please choose a plot--");
    selectPlot2("--Please choose a plot--");
    selectPlot3("--Please choose a plot--");
}

var telemetry = '';
var ptsArr = '';
var trip = '';
async function fetchTelemetry(trip_name) {
    /**
     * Attemps to retrieve JSON file containing a trips telemetry data
     * 
     * @param {string} trip_name - Name of the trip
     * @returns Global telemetry data and LiDAR points
     * @throws Potential Errors: JSON file fetch failure console log, error fetching json and lidar points console error.
     */

    telemetry = '';
    ptsArr = '';
    trip = trip_name;
    try {
        const response = await fetch(`/static/trips/${trip_name}/sample_telemetry.json`);
        if (!response.ok) {
            console.log('Failed to load telemetry');
        }
        telemetry = await response.json();
        ptsArr = await getPoints(`/static/trips/${trip_name}/scan_${trip_name}.txt`);
        console.log(telemetry);
    } catch (error) {
        console.error('Fetch error:', error);
    }
}

// Plot Selection and call Section
function plotTypeOptions(type, select_filler) {
    /**
     * Creates plot div selections once a type is selected.
     * 
     * @param {string} type - Type or category of plots for selection.
     * @param {node} select_filler - Node or element that is the selection tag where options will be added.
     */

    if (type == "Camera"){
        const video = document.createElement("option");
        video.textContent = "Video";
        select_filler.appendChild(video);
        const tf = document.createElement("option");
        tf.textContent = "Cam True/False";
        select_filler.appendChild(tf);
    }
    if (type == "LiDAR"){
        const lidar = document.createElement("option");
        lidar.textContent = "Point Cloud";
        select_filler.appendChild(lidar);
        const m_pos = document.createElement("option");
        m_pos.textContent = "Motor Position";
        select_filler.appendChild(m_pos);
        const scan_pct = document.createElement("option");
        scan_pct.textContent = "Scan Percentage";
        select_filler.appendChild(scan_pct);
        const tf = document.createElement("option");
        tf.textContent = "True/False";
        select_filler.appendChild(tf);
    }
    if (type == "Plots"){
        const motor_v = document.createElement("option");
        motor_v.textContent = "Motor Voltage";
        select_filler.appendChild(motor_v);
        const motor_a = document.createElement("option");
        motor_a.textContent = "Motor Current";
        select_filler.appendChild(motor_a);
        const motor_rpm = document.createElement("option");
        motor_rpm.textContent = "Motor RPM";
        select_filler.appendChild(motor_rpm);
        const rpi_util = document.createElement("option");
        rpi_util.textContent = "Raspberry Pi Util";
        select_filler.appendChild(rpi_util);
        const rpi_temp = document.createElement("option");
        rpi_temp.textContent = "Raspberry Pi Temp";
        select_filler.appendChild(rpi_temp);
        const rpi_uptime = document.createElement("option");
        rpi_uptime.textContent = "Raspberry Uptime";
        select_filler.appendChild(rpi_uptime);
        const us_distance = document.createElement("option");
        us_distance.textContent = "Ultrasonic Distances";
        select_filler.appendChild(us_distance);
        const imu_angles = document.createElement("option");
        imu_angles.textContent = "IMU Angles";
        select_filler.appendChild(imu_angles);
        const imu_accel = document.createElement("option");
        imu_accel.textContent = "IMU Acceleration";
        select_filler.appendChild(imu_accel);
        const bat_cap = document.createElement("option");
        bat_cap.textContent = "Battery Capacity";
        select_filler.appendChild(bat_cap);
        const bat_va = document.createElement("option");
        bat_va.textContent = "Battery V/A";
        select_filler.appendChild(bat_va);
        const amb_temp = document.createElement("option");
        amb_temp.textContent = "Ambient Temp";
        select_filler.appendChild(amb_temp);
        const amb_light = document.createElement("option");
        amb_light.textContent = "Ambient Light";
        select_filler.appendChild(amb_light);
        const hdlghts = document.createElement("option");
        hdlghts.textContent = "Headlights";
        select_filler.appendChild(hdlghts);
    }
}
function purgePlot(plot_name) {
    /**
     * Removes all plots or elements that might be in a plot div.
     * 
     * @param {string} plot_name - Div Id that refers to one of the 3 plot locations.
     */

    const plot = document.getElementById(plot_name);
    if(plot){
            const video_img = document.getElementById(`video_${plot_name}`);
        // Removes video or image if one is there
        if(video_img){
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
function plotFunction(plot_type, plot_name) {
    /**
     * Plots a function in one of the 3 plot divs.
     * 
     * @param {string} plot_type - Selected plot or video to be displayed in the plot div.
     * @param {string} plot_name - Id of the div that will display the selected plot.
     */

    if(plot_type == "Motor Voltage") {
        motorPlotV(plot_name);
    }
    if(plot_type == "Motor Current") {
        motorPlotA(plot_name);
    }
    if(plot_type == "Motor RPM") {
        motorPlotRPM(plot_name);
    }
    if(plot_type == "Raspberry Pi Util") {
        rpiUtilPlot(plot_name);
    }
    if(plot_type == "Raspberry Pi Temp") {
        rpiTempPlot(plot_name);
    }
    if(plot_type == "Raspberry Uptime") {
        rpiUptimePlot(plot_name);
    }
    if(plot_type == "Ultrasonic Distances") {
        usDistancePlot(plot_name);
    }
    if(plot_type == "IMU Angles") {
        imuRPYPlot(plot_name);
    }
    if(plot_type == "IMU Acceleration") {
        imuXYZPlot(plot_name);
    }
    if(plot_type == "Battery Capacity") {
        batCapPlot(plot_name);
    }
    if(plot_type == "Battery V/A") {
        batVAPlot(plot_name);
    }
    if(plot_type == "Ambient Temp") {
        ambTempPlot(plot_name);
    }
    if(plot_type == "Ambient Light") {
        ambLightPlot(plot_name);
    }
    if(plot_type == "Headlights") {
        headlightsPlot(plot_name);
    }
    if(plot_type == "Video") {
        videoPlot(plot_name);
    }
    if(plot_type == "Cam True/False") {
        cameraTFPlot(plot_name);
    }
    if(plot_type == "Point Cloud") {
        pointCloudPlot(plot_name);
    }
    if(plot_type == "Motor Position") {
        lidarMPosPlot(plot_name);
    }
    if(plot_type == "Scan Percentage") {
        lidarScanPlot(plot_name);
    }
    if(plot_type == "True/False") {
        lidarTFPlot(plot_name);
    }
}

// Plot Function Section
function motorPlotV(plot_name) {
    /**
     * Creates a Plotly plot containing all motor voltages.
     * 
     * @param {string} plot_name - Id of the div to display the Plotly plot.
     */

    console.log("motorPlotV()");
    const time = [];
    const left_front_v = []; const right_front_v = [];
    const left_middle_v = []; const right_middle_v = [];
    const left_rear_v = []; const right_rear_v = [];

    for(let i = 0; i < telemetry.duration_s; i++) {
        time[i] = i;
        left_front_v[i] = JSON.stringify(telemetry.telemetry[i].motors.front_left.voltage_v);
        left_middle_v[i] = JSON.stringify(telemetry.telemetry[i].motors.mid_left.voltage_v);
        left_rear_v[i] = JSON.stringify(telemetry.telemetry[i].motors.rear_left.voltage_v);

        right_front_v[i] = JSON.stringify(telemetry.telemetry[i].motors.front_right.voltage_v);
        right_middle_v[i] = JSON.stringify(telemetry.telemetry[i].motors.mid_right.voltage_v);
        right_rear_v[i] = JSON.stringify(telemetry.telemetry[i].motors.rear_right.voltage_v);
    }

    // Plot using plotly
    var lf_v = {
        x: time,
        y: left_front_v,
        type: 'scatter',
        name: 'LFront_V',
    }
    var lm_v = {
        x: time,
        y: left_middle_v,
        type: 'scatter',
        name: 'LMiddle_V',
    }
    var lr_v = {
        x: time,
        y: left_rear_v,
        type: 'scatter',
        name: 'LRear_V',
    }
    var rf_v = {
        x: time,
        y: right_front_v,
        type: 'scatter',
        name: 'RFront_V'
    }
    var rm_v = {
        x: time,
        y: right_middle_v,
        type: 'scatter',
        name: 'RMiddle_V',
    }
    var rr_v = {
        x: time,
        y: right_rear_v,
        type: 'scatter',
        name: 'RRear_V',
    }

    var plot_trace = [lf_v, lm_v, lr_v, rf_v, rm_v, rr_v];
    var layout = {
        margin: {
            t: 20,
            b: 20,
            l: 20,
            r: 0,
        },
    }
    Plotly.newPlot(plot_name, plot_trace, layout);
}
function motorPlotA(plot_name) {
    /**
     * Creates a Plotly plot containing all motor currents.
     * 
     * @param {string} plot_name - Id of the div to display the Plotly plot.
     */

    console.log("motorPlotA()");
    const time = [];
    const left_front_a = []; const right_front_a = [];
    const left_middle_a = []; const right_middle_a = [];
    const left_rear_a = []; const right_rear_a = [];

    for(let i = 0; i < telemetry.duration_s; i++) {
        time[i] = i;
        left_front_a[i] = JSON.stringify(telemetry.telemetry[i].motors.front_left.current_a);
        left_middle_a[i] = JSON.stringify(telemetry.telemetry[i].motors.mid_left.current_a);
        left_rear_a[i] = JSON.stringify(telemetry.telemetry[i].motors.rear_left.current_a);

        right_front_a[i] = JSON.stringify(telemetry.telemetry[i].motors.front_right.current_a);
        right_middle_a[i] = JSON.stringify(telemetry.telemetry[i].motors.mid_right.current_a);
        right_rear_a[i] = JSON.stringify(telemetry.telemetry[i].motors.rear_right.current_a);
    }

    // Plot using plotly
    var lf_a = {
        x: time,
        y: left_front_a,
        type: 'scatter',
        name: 'LFront_A',
    }
    var lm_a = {
        x: time,
        y: left_middle_a,
        type: 'scatter',
        name: 'LMiddle_A',
    }
    var lr_a = {
        x: time,
        y: left_rear_a,
        type: 'scatter',
        name: 'LRear_A',
    }
    var rf_a = {
        x: time,
        y: right_front_a,
        type: 'scatter',
        name: 'RFront_A',
    }
    var rm_a = {
        x: time,
        y: right_middle_a,
        type: 'scatter',
        name: 'RMiddle_A',
    }
    var rr_a = {
        x: time,
        y: right_rear_a,
        type: 'scatter',
        name: 'RRear_A',
    }

    var plot = [lf_a, lm_a, lr_a, rf_a, rm_a, rr_a];
    var layout = {
        margin: {
            t: 20,
            b: 20,
            l: 20,
            r: 0,
        },
    }
    Plotly.newPlot(plot_name, plot, layout);
}
function motorPlotRPM(plot_name) {
    /**
     * Creates a Plotly plot containing all motor rpms.
     * 
     * @param {string} plot_name - Id of the div to display the Plotly plot.
     */

    console.log("motorPlotRPM()");
    const time = [];
    const left_front_rpm = []; const right_front_rpm = [];
    const left_middle_rpm = []; const right_middle_rpm = [];
    const left_rear_rpm = []; const right_rear_rpm = [];

    for(let i = 0; i < telemetry.duration_s; i++) {
        time[i] = i;
        left_front_rpm[i] = JSON.stringify(telemetry.telemetry[i].motors.front_left.rpm);
        left_middle_rpm[i] = JSON.stringify(telemetry.telemetry[i].motors.mid_left.rpm);
        left_rear_rpm[i] = JSON.stringify(telemetry.telemetry[i].motors.rear_left.rpm);

        right_front_rpm[i] = JSON.stringify(telemetry.telemetry[i].motors.front_right.rpm);
        right_middle_rpm[i] = JSON.stringify(telemetry.telemetry[i].motors.mid_right.rpm);
        right_rear_rpm[i] = JSON.stringify(telemetry.telemetry[i].motors.rear_right.rpm);
    }

    // Plot using plotly
    var lf_rpm = {
        x: time,
        y: left_front_rpm,
        type: 'scatter',
        name: 'LFront_RPM',
    }
    var rf_rpm = {
        x: time,
        y: right_front_rpm,
        type: 'scatter',
        name: 'RFront_RPM',
    }
    var lm_rpm = {
        x: time,
        y: left_middle_rpm,
        type: 'scatter',
        name: 'LMiddle_RPM',
    }
    var rm_rpm = {
        x: time,
        y: right_middle_rpm,
        type: 'scatter',
        name: 'RMiddle_RPM',
    }
    var lr_rpm = {
        x: time,
        y: left_rear_rpm,
        type: 'scatter',
        name: 'LRear_RPM',
    }
    var rr_rpm = {
        x: time,
        y: right_rear_rpm,
        type: 'scatter',
        name: 'RRear_RPM',
    }

    var plot = [lf_rpm, rf_rpm, lm_rpm, rm_rpm, lr_rpm, rr_rpm];
    var layout = {
        margin: {
            t: 20,
            b: 20,
            l: 35,
            r: 20,
        },
    }
    Plotly.newPlot(plot_name, plot, layout);
}
function rpiUtilPlot(plot_name) {
    /**
     * Creates a Plotly plot containing Raspberry Pi 5 cpu and memory utilization percentage.
     * 
     * @param {string} plot_name - Id of the div to display the Plotly plot.
     */

    console.log("rpiUtilPlot()");
    const time = [];
    const rpi_mem = []; 
    const rpi_cpu = [];

    for(let i = 0; i < telemetry.duration_s; i++) {
        time[i] = i;
        rpi_mem[i] = JSON.stringify(telemetry.telemetry[i].rpi.mem_util_pct);
        rpi_cpu[i] = JSON.stringify(telemetry.telemetry[i].rpi.cpu_util_pct);
    }

    // Plot using plotly
    var mem = {
        x: time,
        y: rpi_mem,
        type: 'scatter',
        name: 'Memory Util %',
    }
    var cpu = {
        x: time,
        y: rpi_cpu,
        type: 'scatter',
        name: 'CPU Util %',
    }

    var plot = [mem, cpu];
    var layout = {
        margin: {
            t: 20,
            b: 20,
            l: 35,
            r: 20,
        },
    }
    Plotly.newPlot(plot_name, plot, layout);
}
function rpiTempPlot(plot_name) {
    /**
     * Creates a Plotly plot containing Raspberry Pi 5 temperature
     * 
     * @param {string} plot_name - Id of the div to display the Plotly plot.
     */

    console.log("rpiTempPlot()");
    const time = [];
    const rpi_temp = []; 

    for(let i = 0; i < telemetry.duration_s; i++) {
        time[i] = i;
        rpi_temp[i] = JSON.stringify(telemetry.telemetry[i].rpi.temp_c);
    }

    // Plot using plotly
    var temp = {
        x: time,
        y: rpi_temp,
        type: 'scatter',
        name: 'Temp C',
    }

    var plot = [temp];
    var layout = {
        margin: {
            t: 20,
            b: 20,
            l: 35,
            r: 20,
        },
    }
    Plotly.newPlot(plot_name, plot, layout);
}
function rpiUptimePlot(plot_name) {
    /**
     * Creates a Plotly plot containing Raspberry Pi uptime.
     * 
     * @param {string} plot_name - Id of the div to display the Plotly plot.
     */

    console.log("rpiUptimePlot()");
    const time = [];
    const uptime_sec = []; 

    for(let i = 0; i < telemetry.duration_s; i++) {
        time[i] = i;
        uptime_sec[i] = JSON.stringify(telemetry.telemetry[i].rpi.uptime_s);
    }

    // Plot using plotly
    var seconds = {
        x: time,
        y: uptime_sec,
        type: 'scatter',
        name: 'Uptime seconds',
    }

    var plot = [seconds];
    var layout = {
        margin: {
            t: 20,
            b: 20,
            l: 35,
            r: 20,
        },
    }
    Plotly.newPlot(plot_name, plot, layout);
}
function usDistancePlot(plot_name) {
    /**
     * Creates a Plotly plot containing all ultrasonic distances.
     * 
     * @param {string} plot_name - Id of the div to display the Plotly plot.
     */

    console.log("usDistancePlot()");
    const time = [];
    const lidar_us = []; const rear_us = [];
    const left_us = []; const center_us = [];
    const right_us = [];

    for(let i = 0; i < telemetry.duration_s; i++) {
        time[i] = i;
        lidar_us[i] = JSON.stringify(telemetry.telemetry[i].ultrasonics.lidar_cm);
        rear_us[i] = JSON.stringify(telemetry.telemetry[i].ultrasonics.rear_cm);
        left_us[i] = JSON.stringify(telemetry.telemetry[i].ultrasonics.left_cm);
        center_us[i] = JSON.stringify(telemetry.telemetry[i].ultrasonics.center_cm);
        right_us[i] = JSON.stringify(telemetry.telemetry[i].ultrasonics.right_cm);
    }

    // Plot using plotly
    var lidar = {
        x: time,
        y: lidar_us,
        type: 'scatter',
        name: 'LiDAR US',
    }
    var rear = {
        x: time,
        y: rear_us,
        type: 'scatter',
        name: 'Rear US',
    }
    var left = {
        x: time,
        y: left_us,
        type: 'scatter',
        name: 'Front Left US',
    }
    var center = {
        x: time,
        y: center_us,
        type: 'scatter',
        name: 'Front Center US',
    }
    var right = {
        x: time,
        y: right_us,
        type: 'scatter',
        name: 'Front Right US',
    }

    var plot = [lidar, rear, left, center, right];
    var layout = {
        margin: {
            t: 20,
            b: 20,
            l: 35,
            r: 20,
        },
    }
    Plotly.newPlot(plot_name, plot, layout);
}
function imuRPYPlot(plot_name) {
    /**
     * Creates a Plotly plot containing all IMU roll, pitch, yaw.
     * 
     * @param {string} plot_name - Id of the div to display the Plotly plot.
     */

    console.log("imuRPYPlot()");
    const time = [];
    const roll_imu = []; const pitch_imu = [];
    const yaw_imu = [];

    for(let i = 0; i < telemetry.duration_s; i++) {
        time[i] = i;
        roll_imu[i] = JSON.stringify(telemetry.telemetry[i].imu.roll_dps);
        pitch_imu[i] = JSON.stringify(telemetry.telemetry[i].imu.pitch_dps);
        yaw_imu[i] = JSON.stringify(telemetry.telemetry[i].imu.yaw_dps);
    }

    // Plot using plotly
    var roll = {
        x: time,
        y: roll_imu,
        type: 'scatter',
        name: 'Roll IMU',
    }
    var pitch = {
        x: time,
        y: pitch_imu,
        type: 'scatter',
        name: 'Pitch IMU',
    }
    var yaw = {
        x: time,
        y: yaw_imu,
        type: 'scatter',
        name: 'Yaw IMU',
    }

    var plot = [roll, pitch, yaw];
    var layout = {
        margin: {
            t: 20,
            b: 20,
            l: 35,
            r: 20,
        },
    }
    Plotly.newPlot(plot_name, plot, layout);
}
function imuXYZPlot(plot_name) {
    /**
     * Creates a Plotly plot containing all IMU accelerations, X Y Z.
     * 
     * @param {string} plot_name - Id of the div to display the Plotly plot.
     */

    console.log("imuXYZPlot()");
    const time = [];
    const accel_x = []; const accel_y = [];
    const accel_z = [];

    for(let i = 0; i < telemetry.duration_s; i++) {
        time[i] = i;
        accel_x[i] = JSON.stringify(telemetry.telemetry[i].imu.accel_x_mps2);
        accel_y[i] = JSON.stringify(telemetry.telemetry[i].imu.accel_y_mps2);
        accel_z[i] = JSON.stringify(telemetry.telemetry[i].imu.accel_z_mps2);
    }

    // Plot using plotly
    var x = {
        x: time,
        y: accel_x,
        type: 'scatter',
        name: 'Acceleration X',
    }
    var y = {
        x: time,
        y: accel_y,
        type: 'scatter',
        name: 'Acceleration Y',
    }
    var z = {
        x: time,
        y: accel_z,
        type: 'scatter',
        name: 'Acceleration Z',
    }

    var plot = [x, y, z];
    var layout = {
        margin: {
            t: 20,
            b: 20,
            l: 35,
            r: 20,
        },
    }
    Plotly.newPlot(plot_name, plot, layout);
}
function batCapPlot(plot_name) {
    /**
     * Creates a Plotly plot containing battery life capacity as a percentage.
     * 
     * @param {string} plot_name - Id of the div to display the Plotly plot.
     */

    console.log("batCapPlot()");
    const time = [];
    const bat_capacity = []; 

    for(let i = 0; i < telemetry.duration_s; i++) {
        time[i] = i;
        bat_capacity[i] = JSON.stringify(telemetry.telemetry[i].ugv.battery.capacity_pct);
    }

    // Plot using plotly
    var cap = {
        x: time,
        y: bat_capacity,
        type: 'scatter',
        name: 'Capacity %',
    }

    var plot = [cap];
    var layout = {
        margin: {
            t: 20,
            b: 20,
            l: 35,
            r: 20,
        },
    }
    Plotly.newPlot(plot_name, plot, layout);
}
function batVAPlot(plot_name) {
    /**
     * Creates a Plotly plot containing battery voltage and current output.
     * 
     * @param {string} plot_name - Id of the div to display the Plotly plot.
     */

    console.log("batVAPlot()");
    const time = [];
    const bat_voltage = []; 
    const bat_amps = []; 

    for(let i = 0; i < telemetry.duration_s; i++) {
        time[i] = i;
        bat_voltage[i] = JSON.stringify(telemetry.telemetry[i].ugv.battery.voltage_v);
        bat_amps[i] = JSON.stringify(telemetry.telemetry[i].ugv.battery.current_a);
    }

    // Plot using plotly
    var bat_v = {
        x: time,
        y: bat_voltage,
        type: 'scatter',
        name: 'Voltage',
    }
    var bat_a = {
        x: time,
        y: bat_amps,
        type: 'scatter',
        name: 'Amps',
    }

    var plot = [bat_v, bat_a];
    var layout = {
        margin: {
            t: 20,
            b: 20,
            l: 35,
            r: 20,
        },
    }
    Plotly.newPlot(plot_name, plot, layout);
}
function ambTempPlot(plot_name) {
    /**
     * Creates a Plotly plot containing ambient temperature.
     * 
     * @param {string} plot_name - Id of the div to display the Plotly plot.
     */

    console.log("ambTempPlot()");
    const time = [];
    const amb_temp = []; 

    for(let i = 0; i < telemetry.duration_s; i++) {
        time[i] = i;
        amb_temp[i] = JSON.stringify(telemetry.telemetry[i].ugv.ambient_temp_c);
    }

    // Plot using plotly
    var temp = {
        x: time,
        y: amb_temp,
        type: 'scatter',
        name: 'Temp C',
    }

    var plot = [temp];
    var layout = {
        margin: {
            t: 20,
            b: 20,
            l: 35,
            r: 20,
        },
    }
    Plotly.newPlot(plot_name, plot, layout);
}
function ambLightPlot(plot_name) {
    /**
     * Creates a Plotly plot containing ambient light seen from the UGV.
     * 
     * @param {string} plot_name - Id of the div to display the Plotly plot.
     */

    console.log("ambLightPlot()");
    const time = [];
    const amb_light = []; 

    for(let i = 0; i < telemetry.duration_s; i++) {
        time[i] = i;
        amb_light[i] = JSON.stringify(telemetry.telemetry[i].ugv.ambient_light_wpm2);
    }

    // Plot using plotly
    var light = {
        x: time,
        y: amb_light,
        type: 'scatter',
        name: 'Light wpm^2',
    }

    var plot = [light];
    var layout = {
        margin: {
            t: 20,
            b: 20,
            l: 35,
            r: 20,
        },
    }
    Plotly.newPlot(plot_name, plot, layout);
}
function headlightsPlot(plot_name) {
    /**
     * Creates a Plotly plot showing if headlights are on or off.
     * 
     * @param {string} plot_name - Id of the div to display the Plotly plot.
     */

    console.log("headlightsPlot()");
    const time = [];
    const headlights = []; 

    for(let i = 0; i < telemetry.duration_s; i++) {
        time[i] = i;
        headlights[i] = JSON.stringify(telemetry.telemetry[i].ugv.headlights);
        if(headlights[i] == "true"){
            headlights[i] = 1;
        } else {
            headlights[i] = 0;
        }
    }

    // Plot using plotly
    var hl = {
        x: time,
        y: headlights,
        type: 'bar',
        name: 'Bool',
    }

    var plot = [hl];
    var layout = {
        margin: {
            t: 20,
            b: 20,
            l: 35,
            r: 20,
        },
        yaxis: {
            showticklabels: false,
        },
    }
    Plotly.newPlot(plot_name, plot, layout);
}
async function videoPlot(plot_name) {
    /**
     * Creates a video element that is then appended to a div.
     * 
     * @param {string} plot_name - Id of the div to display the video.
     */

    console.log("videoPlot()");
    let video_url = `../static/trips/${trip}/video_${trip}.mp4`;
    const plot = document.getElementById(plot_name);

    if ((await fetch(video_url)).ok) {
        var video = document.createElement('video');
        video.innerText = "Loading video...";
        video.id = `video_${plot_name}`;
        video.src = video_url;
        video.type = "video/mp4";
        video.autoplay = true;
        video.playsInline = true;
        video.style.height = '100%';
        video.style.width = '100%';

        plot.appendChild(video);
    }
    else {
        var video = fragment.appendChild(document.createElement('img'));
        video.id = `video_${plot_name}`;
        video.src = "static/images/no_video.gif";

        plot.appendChild(video);
    }
}
function cameraTFPlot(plot_name) {
    /**
     * Creates a Plotly plot showing if camera is connected, recording or streaming.
     * 
     * @param {string} plot_name - Id of the div to display the Plotly plot.
     */

    console.log("cameraTFPlot()");
    const time = [];
    const connected = []; const recording = [];
    const streaming = [];

    for(let i = 0; i < telemetry.duration_s; i++) {
        time[i] = i;
        connected[i] = JSON.stringify(telemetry.telemetry[i].camera.connected);
        recording[i] = JSON.stringify(telemetry.telemetry[i].camera.recording);
        streaming[i] = JSON.stringify(telemetry.telemetry[i].camera.streaming);
        if(connected[i] == "true"){
            connected[i] = 1;
        } else {
            connected[i] = 0;
        }
        if(recording[i] == "true"){
            recording[i] = 1;
        } else {
            recording[i] = 0;
        }
        if(streaming[i] == "true"){
            streaming[i] = 1;
        } else {
            streaming[i] = 0;
        }
    }

    // Plot using plotly
    var con = {
        x: time,
        y: connected,
        type: 'bar',
        name: 'Connected',
    }
    var rec = {
        x: time,
        y: recording,
        type: 'bar',
        name: 'Scanning',
    }
    var stream = {
        x: time,
        y: streaming,
        type: 'bar',
        name: 'Streaming',
    }

    var plot = [con,rec,stream,];
    var layout = {
        barmode: 'group',
        margin: {
            t: 20,
            b: 20,
            l: 35,
            r: 20,
        },
        yaxis: {
            showticklabels: false,
        },
    }
    Plotly.newPlot(plot_name, plot, layout);
}
function pointCloudPlot(plot_name) {
    /**
     * Creates a Plotly plot containing the LiDAR point cloud or '3D scatter plot'.
     * 
     * @param {string} plot_name - Id of the div to display the Plotly point cloud.
     */

    console.log("pointCloudPlot()");
    var intensity = getDimFromPoints(ptsArr,3);
    //console.log(ptsArr);
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
        scene:{
            aspectratio: { x: 1, y: 1, z: 1 },
            camera: {
                eye: {x: 2, y: 2, z: 1},    // Camera position
                center: {x: 0, y: 0, z: 0}, // Point the camera looks at
                up: {x: 0, y: 0, z: 1}      // Up direction
            }
        },
        paper_bgcolor: 'black'};

    Plotly.newPlot(plot_name, data, layout);
}
function lidarMPosPlot(plot_name) {
    /**
     * Creates a Plotly plot containing the LiDAR stepper motor position in degrees.
     * 
     * @param {string} plot_name - Id of the div to display the Plotly plot.
     */

    console.log("lidarMPosPlot()");
    const time = [];
    const motor_pos = []; 

    for(let i = 0; i < telemetry.duration_s; i++) {
        time[i] = i;
        motor_pos[i] = JSON.stringify(telemetry.telemetry[i].lidar.motor_pos_deg);
    }

    // Plot using plotly
    var mpos = {
        x: time,
        y: motor_pos,
        type: 'scatter',
        name: 'Position deg',
    }

    var plot = [mpos];
    var layout = {
        margin: {
            t: 20,
            b: 20,
            l: 35,
            r: 20,
        },
    }
    Plotly.newPlot(plot_name, plot, layout);
}
function lidarScanPlot(plot_name) {
    /**
     * Creates a Plotly plot containing the LiDAR scan percentage.
     * 
     * @param {string} plot_name - Id of the div to display the Plotly plot.
     */

    console.log("lidarScanPlot()");
    const time = [];
    const scan_pct = []; 

    for(let i = 0; i < telemetry.duration_s; i++) {
        time[i] = i;
        scan_pct[i] = JSON.stringify(telemetry.telemetry[i].lidar.scan_pct);
    }

    // Plot using plotly
    var scan = {
        x: time,
        y: scan_pct,
        type: 'scatter',
        name: 'Scan %',
    }

    var plot = [scan];
    var layout = {
        margin: {
            t: 20,
            b: 20,
            l: 35,
            r: 20,
        },
    }
    Plotly.newPlot(plot_name, plot, layout);
}
function lidarTFPlot(plot_name) {
    /**
     * Creates a Plotly plot showing if lidar is connected, scanning, saving file, or in fixed mode.
     * 
     * @param {string} plot_name - Id of the div to display the Plotly plot.
     */

    console.log("lidarTFPlot()");
    const time = [];
    const connected = []; const scanning = [];
    const saved_file = []; const fixed_mode = []; 

    for(let i = 0; i < telemetry.duration_s; i++) {
        time[i] = i;
        connected[i] = JSON.stringify(telemetry.telemetry[i].lidar.connected);
        scanning[i] = JSON.stringify(telemetry.telemetry[i].lidar.scanning);
        saved_file[i] = JSON.stringify(telemetry.telemetry[i].lidar.saving_file);
        fixed_mode[i] = JSON.stringify(telemetry.telemetry[i].lidar.fixed_mode);
        if(connected[i] == "true"){
            connected[i] = 1;
        } else {
            connected[i] = 0;
        }
        if(scanning[i] == "true"){
            scanning[i] = 1;
        } else {
            scanning[i] = 0;
        }
        if(saved_file[i] == "true"){
            saved_file[i] = 1;
        } else {
            saved_file[i] = 0;
        }
        if(fixed_mode[i] == "true"){
            fixed_mode[i] = 1;
        } else {
            fixed_mode[i] = 0;
        }
    }

    // Plot using plotly
    var con = {
        x: time,
        y: connected,
        type: 'bar',
        name: 'Connected',
    }
    var scan = {
        x: time,
        y: scanning,
        type: 'bar',
        name: 'Scanning',
    }
    var file = {
        x: time,
        y: saved_file,
        type: 'bar',
        name: 'Saved File',
    }
    var fix = {
        x: time,
        y: fixed_mode,
        type: 'bar',
        name: 'Fixed Mode',
    }


    var plot = [con,scan,file,fix];
    var layout = {
        barmode: 'group',
        margin: {
            t: 20,
            b: 20,
            l: 35,
            r: 20,
        },
        yaxis: {
            showticklabels: false,
        },
    }
    Plotly.newPlot(plot_name, plot, layout);
}

// LiDAR 3D Scatter Plot Functions
async function getPoints(filename) {
    /**
     * Gets all the point cloud data points and separates them into organized x y z intensity columns.
     * 
     * @param {string} filename - filepath to the text file with all the point data.
     * @returns {float32array} points All data points organized into columns of x y z intensity.
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

// Toggle Fullscreen
function toggleFullScreen1() {
    /**
     * Toggles the plot 1 div into a fullscreen div
     */

    const plot1 = document.getElementById('plot1');
    plot1.classList.toggle('fullscreen_div');

    Plotly.relayout(plot1, {autosize: true});
}
function toggleFullScreen2() {
    /**
     * Toggles the plot 2 div into a fullscreen div
     */

    const plot2 = document.getElementById('plot2');
    plot2.classList.toggle('fullscreen_div');

    Plotly.relayout(plot2, {autosize: true});
}
function toggleFullScreen3() {
    /**
     * Toggles the plot 3 div into a fullscreen div
     */

    const plot3 = document.getElementById('plot3');
    plot3.classList.toggle('fullscreen_div');

    Plotly.relayout(plot3, {autosize: true});
}

// Adds event listener for a change in selection option in the all select tags
document.addEventListener("DOMContentLoaded", async function() {
    const select_Trip = document.getElementById("trip_select");
    select_Trip.addEventListener("change", async function() {
        const trip = select_Trip.value;
        console.log("Selected trip: " + trip);
        // Set default plot images
        purgePlot("plot1");
        purgePlot("plot2");
        purgePlot("plot3");

        await fetchTelemetry(trip);
    });
    
    // event listener for plot 1 type
    const select_plot1_type = document.getElementById("plot_1_type");
    select_plot1_type.addEventListener("change", function() {
        var type = select_plot1_type.value;
        console.log("Selected plot1 type: " + type);
        const select_filler = document.getElementById("plot_select_1");
        select_filler.innerHTML = '';
        const choose = document.createElement("option")
        choose.textContent = "--Please choose a plot--";
        select_filler.appendChild(choose); 
        purgePlot("plot1");
        plotTypeOptions(type,select_filler);
    });
    // event listener for plot 1
    const select_Plot1 = document.getElementById("plot_select_1");
    select_Plot1.addEventListener("change", function() {
        var plot = select_Plot1.value;
        console.log("Selected plot1 plot: " + plot);
        purgePlot("plot1");
        plotFunction(plot, "plot1");
    });

    // event listener for plot 2 type
    const select_plot2_type = document.getElementById("plot_2_type");
    select_plot2_type.addEventListener("change", function() {
        var type = select_plot2_type.value;
        console.log("Selected plot2 type: " + type);
        const select_filler = document.getElementById("plot_select_2");
        select_filler.innerHTML = '';
        const choose = document.createElement("option")
        choose.textContent = "--Please choose a plot--";
        select_filler.appendChild(choose);
        purgePlot("plot2");
        plotTypeOptions(type,select_filler);
    });
    // event listener for plot 2
    const select_Plot2 = document.getElementById("plot_select_2");
    select_Plot2.addEventListener("change", function() {
        var plot = select_Plot2.value;
        console.log("Selected plot2 plot: " + plot);
        purgePlot("plot2");
        plotFunction(plot, "plot2");
    });

    // event listener for plot 3 type
    const select_plot3_type = document.getElementById("plot_3_type");
    select_plot3_type.addEventListener("change", function() {
        var type = select_plot3_type.value;
        console.log("Selected plot3 type: " + type);
        const select_filler = document.getElementById("plot_select_3");
        select_filler.innerHTML = '';
        const choose = document.createElement("option")
        choose.textContent = "--Please choose a plot--";
        select_filler.appendChild(choose);
        purgePlot("plot3");
        plotTypeOptions(type,select_filler);
    });
    // event listener for plot 3
    const select_Plot3 = document.getElementById("plot_select_3");
    select_Plot3.addEventListener("change", function() {
        var plot = select_Plot3.value;
        console.log("Selected plot3 plot: " + plot);
        purgePlot("plot3");
        plotFunction(plot, "plot3");
    });
});

fetchTrips(); // runs the fetchTrips on page load
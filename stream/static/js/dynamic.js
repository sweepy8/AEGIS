async function fetchTrips() {
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
}

var telemetry = '';
async function fetchTelemetry(trip) {
    telemetry = '';
    try {
        const response = await fetch(`/static/trips/${trip}/sample_telemetry.json`);
        if (!response.ok) {
            console.log('Failed to load telemetry');
        }
        telemetry = await response.json();
        console.log(telemetry);
    } catch (error) {
        console.error('Fetch error:', error);
    }
}

async function selectPlot1(plot) {
    if(plot == "Motor Voltage & Current") {
        motorPlotVA("plot1");
    }
    if(plot == "Motor RPM") {
        motorPlotRPM("plot1");
    }
}

async function selectPlot2(plot) {
    if(plot == "Motor RPM") {
        motorPlotRPM("plot2");
    }
    if(plot == "Motor Voltage & Current") {
        motorPlotVA("plot2");
    }
}

async function selectPlot3(plot) {
    if(plot == "Motor RPM") {
        motorPlotRPM("plot3");
    }
    if(plot == "Motor Voltage & Current") {
        motorPlotVA("plot3");
    }
}

async function motorPlotVA(plot_name) {
    // console.log("motorPlotVA()");
    const time = [];
    const left_front_v = []; const right_front_v = [];
    const left_front_a = []; const right_front_a = [];

    const left_middle_v = []; const right_middle_v = [];
    const left_middle_a = []; const right_middle_a = [];

    const left_rear_v = []; const right_rear_v = [];
    const left_rear_a = []; const right_rear_a = [];

    for(let i = 0; i < await telemetry.duration_s; i++) {
        time[i] = i;
        left_front_v[i] = JSON.stringify(telemetry.telemetry[i].motors.front_left.voltage_v);
        left_front_a[i] = JSON.stringify(telemetry.telemetry[i].motors.front_left.current_a);
        left_middle_v[i] = JSON.stringify(telemetry.telemetry[i].motors.mid_left.voltage_v);
        left_middle_a[i] = JSON.stringify(telemetry.telemetry[i].motors.mid_left.current_a);
        left_rear_v[i] = JSON.stringify(telemetry.telemetry[i].motors.rear_left.voltage_v);
        left_rear_a[i] = JSON.stringify(telemetry.telemetry[i].motors.rear_left.current_a);

        right_front_v[i] = JSON.stringify(telemetry.telemetry[i].motors.front_right.voltage_v);
        right_front_a[i] = JSON.stringify(telemetry.telemetry[i].motors.front_right.current_a);
        right_middle_v[i] = JSON.stringify(telemetry.telemetry[i].motors.mid_right.voltage_v);
        right_middle_a[i] = JSON.stringify(telemetry.telemetry[i].motors.mid_right.current_a);
        right_rear_v[i] = JSON.stringify(telemetry.telemetry[i].motors.rear_right.voltage_v);
        right_rear_a[i] = JSON.stringify(telemetry.telemetry[i].motors.rear_right.current_a);
    }

    // Plot using plotly
    var lf_v = {
        x: time,
        y: left_front_v,
        type: 'scatter',
        name: 'LFront_V',
    }
    var lf_a = {
        x: time,
        y: left_front_a,
        type: 'scatter',
        name: 'LFront_A',
    }
    var lm_v = {
        x: time,
        y: left_middle_v,
        type: 'scatter',
        name: 'LMiddle_V',
    }
    var lm_a = {
        x: time,
        y: left_middle_a,
        type: 'scatter',
        name: 'LMiddle_A',
    }
    var lr_v = {
        x: time,
        y: left_rear_v,
        type: 'scatter',
        name: 'LRear_V',
    }
    var lr_a = {
        x: time,
        y: left_rear_a,
        type: 'scatter',
        name: 'LRear_A',
    }
    var rf_v = {
        x: time,
        y: right_front_v,
        type: 'scatter',
        name: 'RFront_V'
    }
    var rf_a = {
        x: time,
        y: right_front_a,
        type: 'scatter',
        name: 'RFront_A',
    }
    var rm_v = {
        x: time,
        y: right_middle_v,
        type: 'scatter',
        name: 'RMiddle_V',
    }
    var rm_a = {
        x: time,
        y: right_middle_a,
        type: 'scatter',
        name: 'RMiddle_A',
    }
    var rr_v = {
        x: time,
        y: right_rear_v,
        type: 'scatter',
        name: 'RRear_V',
    }
    var rr_a = {
        x: time,
        y: right_rear_a,
        type: 'scatter3d',
        name: 'RRear_A',
    }

    var va_plot = [lf_v, lf_a, lm_v, lm_a, lr_v, lr_a, rf_v, rf_a, rm_v, rm_a, rr_v, rr_a];
    var va_layout = {
        margin: {
            t: 20,
            b: 20,
            l: 20,
            r: 0,
        },
    }
    Plotly.newPlot(plot_name, va_plot, va_layout);
}

async function motorPlotRPM(plot_name) {
    // console.log("motorPlotRPM()");
    const time = [];
    const left_front_rpm = []; const right_front_rpm = [];
    const left_middle_rpm = []; const right_middle_rpm = [];
    const left_rear_rpm = []; const right_rear_rpm = [];

    for(let i = 0; i < await telemetry.duration_s; i++) {
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

    var rpm_plot = [lf_rpm, rf_rpm, lm_rpm, rm_rpm, lr_rpm, rr_rpm];
    var rpm_layout = {
        margin: {
            t: 20,
            b: 20,
            l: 35,
            r: 20,
        },
    }
    Plotly.newPlot(plot_name, rpm_plot, rpm_layout);
}

// Toggle Fullscreen for plot 1
function toggleFullScreen1() {
        const plot1 = document.getElementById('plot1');
        plot1.classList.toggle('fullscreen_div');

        Plotly.relayout(plot1, {autosize: true});
}
// Toggle Fullscreen for plot 2
function toggleFullScreen2() {
        const plot2 = document.getElementById('plot2');
        plot2.classList.toggle('fullscreen_div');

        Plotly.relayout(plot2, {autosize: true});
}
// Toggle Fullscreen for plot 3
function toggleFullScreen3() {
        const plot3 = document.getElementById('plot3');
        plot3.classList.toggle('fullscreen_div');

        Plotly.relayout(plot3, {autosize: true});
}

// Adds event listener for a change in selection option in the select tag
document.addEventListener("DOMContentLoaded", function() {
    const select = document.getElementById("trip_select");
    select.addEventListener("change", function() {
        const trip = this.value;
        console.log("Selected trip: " + trip);
        fetchTelemetry(trip);
    });
});

// Adds event listener for a change in selection option in the select tag for plot1
document.addEventListener("DOMContentLoaded", function() {
    const select = document.getElementById("plot_select_1");
    select.addEventListener("change", function() {
        var plot = this.value;
        console.log("Selected plot1 plot: " + plot);
        selectPlot1(plot);
    });
});

// Adds event listener for a change in selection option in the select tag for plot2
document.addEventListener("DOMContentLoaded", function() {
    const select = document.getElementById("plot_select_2");
    select.addEventListener("change", function() {
        var plot = this.value;
        console.log("Selected plot2 plot: " + plot);
        selectPlot2(plot);
    });
});

// Adds event listener for a change in selection option in the select tag for plot3
document.addEventListener("DOMContentLoaded", function() {
    const select = document.getElementById("plot_select_3");
    select.addEventListener("change", function() {
        var plot = this.value;
        console.log("Selected plot3 plot: " + plot);
        selectPlot3(plot);
    });
});

fetchTrips(); // runs the fetchTrips on page load
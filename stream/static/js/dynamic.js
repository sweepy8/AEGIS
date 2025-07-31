// function to fetchs trip telemetry data from the json file
var telemetry;
async function fetchTelemetry(trip_n) {
    telemetry = ''; // resets telemetry variable

    console.log(window.location.href);
    // change correct ip address for when changing host servers
    if (window.location.href == "http://127.0.0.1:5000/trip_viewer") {
        document.getElementById('trip').textContent = `${trip_n}`;
        document.getElementById('video').append(await insertVideo(trip_n));

        // LiDAR Visualizer
        var ptsArr = await getPoints(`/static/trips/${trip_n}/scan_${trip_n}.txt`);
        var intensity = getDimFromPoints(ptsArr,3);
        //console.log(ptsArr);
        var points = {
        x:getDimFromPoints(ptsArr, 0),
        y:getDimFromPoints(ptsArr, 1),
        z:getDimFromPoints(ptsArr, 2),
        mode: 'markers',
        marker: {
            size: 2,
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
            scene:{aspectratio: { x: 1, y: 1, z: 0.35 }},
            paper_bgcolor: 'black'};
        Plotly.newPlot('LiDAR', data, layout);

    }
    try {
        const response = await fetch(`/static/trips/${trip_n}/sample_telemetry.json`);
        if (!response.ok) {
            console.log('Failed to load telemetry');
            if (window.location.href == "http://127.0.0.1:5000/trip_viewer") {
                printTelemetryOverview(telemetry);
                printTelemetryData(telemetry);
            }
            if (window.location.href == "http://127.0.0.1:5000/trip_raw_data") {
                printTelemetryRawData(telemetry);
            }
        }

        telemetry = await response.json();
        console.log(telemetry);
        if (window.location.href == "http://127.0.0.1:5000/trip_viewer") {
            printTelemetryOverview(telemetry);
            console.log('calling scrubber')
            linkScrubberToTrip(trip_n);
        }
        if (window.location.href == "http://127.0.0.1:5000/trip_raw_data") {
            printTelemetryRawData(telemetry);
        }
    } catch (error) {
        console.error('Fetch error:', error);
    }
}

async function fetchTrips() {
    const response = await fetch('/trips'); // fetchs data from python
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
    const list_trips = document.getElementById('trip_btns');
    if (!list_trips) {
        console.error('trip_btns <ul> not found');
        return;
    }
    list_trips.innerHTML = ''; // clears old data

    // creates new list with updates trips
    if(Array.isArray(folders)) {
        folders.forEach(trip => {
            const li = document.createElement('li'); // creates list element

            const button = document.createElement('button'); // creates button tag
            button.textContent = trip; // creates button text
            button.classList.add('open-btn'); // adds a class to button
            button.onclick = () => fetchTelemetry(`${trip}`); // adds on click alert

            li.appendChild(button); // adds button to list element
            list_trips.appendChild(li); // adds list element to list
        });
    } else {
        list_trips.innerHTML = `<li>Error loading trips</li>`; // error message
    }
}

// Sets Telemetry Data Overview on HTML by id tag
async function printTelemetryOverview(telemetry) {
    if (!telemetry) { // Resets all p tags to error if no telemetry
        const container = document.getElementById('telemetry_stamp');
        const par = container.getElementsByTagName('p');
        for (let p of par) {
            p.textContent = 'Error';
        }
    } else { // prints all stamped JSON data, i.e models etc.
    document.getElementById('timestamp').textContent = JSON.stringify(telemetry.timestamp);
    document.getElementById('duration').textContent = JSON.stringify(telemetry.duration_s);
    document.getElementById('battery').textContent = JSON.stringify(telemetry.traits.models.battery);
    document.getElementById('battery_size').textContent = JSON.stringify(telemetry.traits.battery_cap_mah);
    document.getElementById('motors').textContent = JSON.stringify(telemetry.traits.models.motors);
    document.getElementById('rpi').textContent = JSON.stringify(telemetry.traits.models.rpi);
    document.getElementById('arduino').textContent = JSON.stringify(telemetry.traits.models.arduino);
    document.getElementById('ultrasonic').textContent = JSON.stringify(telemetry.traits.models.ultrasonics);
    document.getElementById('lidar').textContent = JSON.stringify(telemetry.traits.models.lidar);
    document.getElementById('lidar_motor').textContent = JSON.stringify(telemetry.traits.models.lidar_motor);
    document.getElementById('camera').textContent = JSON.stringify(telemetry.traits.models.camera);
    }
}

// Sets Telemetry Data on HTML by id tag
async function printTelemetryData(i) {
    if (!telemetry) { // Resets all p tags to error if no telemetry
        const container = document.getElementById('telemetry_data');
        const par = container.getElementsByTagName('p');
        for (let p of par) {
            p.textContent = 'Error';
        }
    } else { // prints all stamped JSON data, i.e models etc.
    // RPI
    document.getElementById('uptime').textContent = JSON.stringify(telemetry.telemetry[i].rpi.uptime_s);
    document.getElementById('cpu_util').textContent = JSON.stringify(telemetry.telemetry[i].rpi.cpu_util_pct);
    document.getElementById('mem_util').textContent = JSON.stringify(telemetry.telemetry[i].rpi.mem_util_pct);
    document.getElementById('storage').textContent = JSON.stringify(telemetry.telemetry[i].rpi.storage_avail_mb);
    document.getElementById('rpi_temp').textContent = JSON.stringify(telemetry.telemetry[i].rpi.temp_c);
    // LiDAR
    document.getElementById('lidar_con').textContent = JSON.stringify(telemetry.telemetry[i].lidar.connected);
    document.getElementById('scanning').textContent = JSON.stringify(telemetry.telemetry[i].lidar.scanning);
    document.getElementById('scan_pct').textContent = JSON.stringify(telemetry.telemetry[i].lidar.scan_pct);
    document.getElementById('saved_scan').textContent = JSON.stringify(telemetry.telemetry[i].lidar.saving_file);
    document.getElementById('fixed_mode').textContent = JSON.stringify(telemetry.telemetry[i].lidar.fixed_mode);
    document.getElementById('motor_pos').textContent = JSON.stringify(telemetry.telemetry[i].lidar.motor_pos_deg);
    // Camera
    document.getElementById('camera_con').textContent = JSON.stringify(telemetry.telemetry[i].camera.connected);
    document.getElementById('recording').textContent = JSON.stringify(telemetry.telemetry[i].camera.recording);
    document.getElementById('streaming').textContent = JSON.stringify(telemetry.telemetry[i].camera.streaming);
    document.getElementById('saved_scan').textContent = JSON.stringify(telemetry.telemetry[i].camera.last_file);
    // Motors
    document.getElementById('fl_volt').textContent = JSON.stringify(telemetry.telemetry[i].motors.front_left.voltage_v);
    document.getElementById('fl_cur').textContent = JSON.stringify(telemetry.telemetry[i].motors.front_left.current_a);
    document.getElementById('fl_rpm').textContent = JSON.stringify(telemetry.telemetry[i].motors.front_left.rpm);
    document.getElementById('ml_volt').textContent = JSON.stringify(telemetry.telemetry[i].motors.mid_left.voltage_v);
    document.getElementById('ml_cur').textContent = JSON.stringify(telemetry.telemetry[i].motors.mid_left.current_a);
    document.getElementById('ml_rpm').textContent = JSON.stringify(telemetry.telemetry[i].motors.mid_left.rpm);
    document.getElementById('rl_volt').textContent = JSON.stringify(telemetry.telemetry[i].motors.rear_left.voltage_v);
    document.getElementById('rl_cur').textContent = JSON.stringify(telemetry.telemetry[i].motors.rear_left.current_a);
    document.getElementById('rl_rpm').textContent = JSON.stringify(telemetry.telemetry[i].motors.rear_left.rpm);
    document.getElementById('fr_volt').textContent = JSON.stringify(telemetry.telemetry[i].motors.front_right.voltage_v);
    document.getElementById('fr_cur').textContent = JSON.stringify(telemetry.telemetry[i].motors.front_right.current_a);
    document.getElementById('fr_rpm').textContent = JSON.stringify(telemetry.telemetry[i].motors.front_right.rpm);
    document.getElementById('mr_volt').textContent = JSON.stringify(telemetry.telemetry[i].motors.mid_right.voltage_v);
    document.getElementById('mr_cur').textContent = JSON.stringify(telemetry.telemetry[i].motors.mid_right.current_a);
    document.getElementById('mr_rpm').textContent = JSON.stringify(telemetry.telemetry[i].motors.mid_right.rpm);
    document.getElementById('rr_volt').textContent = JSON.stringify(telemetry.telemetry[i].motors.rear_right.voltage_v);
    document.getElementById('rr_cur').textContent = JSON.stringify(telemetry.telemetry[i].motors.rear_right.current_a);
    document.getElementById('rr_rpm').textContent = JSON.stringify(telemetry.telemetry[i].motors.rear_right.rpm);
    // Ultrasonics
    document.getElementById('lidar_us').textContent = JSON.stringify(telemetry.telemetry[i].ultrasonics.lidar_cm);
    document.getElementById('fl_us').textContent = JSON.stringify(telemetry.telemetry[i].ultrasonics.left_cm);
    document.getElementById('fm_us').textContent = JSON.stringify(telemetry.telemetry[i].ultrasonics.center_cm);
    document.getElementById('fr_us').textContent = JSON.stringify(telemetry.telemetry[i].ultrasonics.right_cm);
    document.getElementById('rear_us').textContent = JSON.stringify(telemetry.telemetry[i].ultrasonics.rear_cm);
    // IMU
    document.getElementById('roll').textContent = JSON.stringify(telemetry.telemetry[i].imu.roll_dps);
    document.getElementById('pitch').textContent = JSON.stringify(telemetry.telemetry[i].imu.pitch_dps);
    document.getElementById('yaw').textContent = JSON.stringify(telemetry.telemetry[i].imu.yaw_dps);
    document.getElementById('accel_x').textContent = JSON.stringify(telemetry.telemetry[i].imu.accel_x_mps2);
    document.getElementById('accel_y').textContent = JSON.stringify(telemetry.telemetry[i].imu.accel_y_mps2);
    document.getElementById('accel_z').textContent = JSON.stringify(telemetry.telemetry[i].imu.accel_z_mps2);
    // UGV
    document.getElementById('bat_cap').textContent = JSON.stringify(telemetry.telemetry[i].ugv.battery.capacity_pct);
    document.getElementById('bat_volt').textContent = JSON.stringify(telemetry.telemetry[i].ugv.battery.voltage_v);
    document.getElementById('bat_cur').textContent = JSON.stringify(telemetry.telemetry[i].ugv.battery.current_a);
    document.getElementById('headlight').textContent = JSON.stringify(telemetry.telemetry[i].ugv.headlights);
    document.getElementById('amb_temp').textContent = JSON.stringify(telemetry.telemetry[i].ugv.ambient_temp_c);
    document.getElementById('amb_light').textContent = JSON.stringify(telemetry.telemetry[i].ugv.ambient_light_wpm2);
    }
}

// Sets Telemetry Data Overview on HTML by id tag
async function printTelemetryRawData(telemetry) {
    const par = document.getElementById('par_raw_data');
    par.textContent = "Loading...";

    if (!telemetry) { // Resets all p tags to error if no telemetry
        par.textContent = 'Error';
    } else { 
            // prints all JSON content, i.e models, telemetry etc.
            console.log("Printing Raw Data")
            par.textContent = JSON.stringify(telemetry);
    }
}

async function insertVideo(tripName) {

    let video_url = `/static/trips/${tripName}/video_${tripName}.mp4`;

    const fragment = document.createDocumentFragment();
    // Remove child elements
    let vid_box = document.getElementById('video');
    for (const child of vid_box.children){
        vid_box.removeChild(child);
    }

    if ((await fetch(video_url)).ok) {
        var video = fragment.appendChild(document.createElement('video'));
        video.innerText = "Loading video...";
        video.id = `video_${tripName}`;
        video.src = video_url;
        video.type = "video/mp4";
        video.autoplay = true;
        video.playsInline = true;
        video.style.height = '100%';
        video.style.width = '100%';
    }
    else {
        var video = fragment.appendChild(document.createElement('img'));
        video.id = `video_${tripName}`;
        video.src = "static/images/no_video.gif";
    }
    return video; 
}

// LiDAR 3D Scatter Plot Functions
async function getPoints(filename) {

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
    let dim = [];
    points.forEach(point => {
        dim.push(point[index]);
    });

    return dim;
}

// Toggle Fullscreen for LiDAR plot
function toggleFullScreen() {
        const lidar_container = document.getElementById('LiDAR');
        lidar_container.classList.toggle('fullscreen_div');

        Plotly.relayout(lidar_container, {autosize: true});
    }

async function linkScrubberToTrip(tripName) {
    const scrubber = document.getElementById("scrubber");
    // const vid = document.getElementById(`video_${tripName}`);
    // const telBox = document.getElementById("telemetry_data");
    // console.log('In Scrubber');
    var tripLenSeconds = telemetry.duration_s;

    // 1. Link scrubber to video element
    // if (vid) {

    //     // update scrubber value every 50ms
    //     var updateScrubberInterval = setInterval(() => {
    //         if (vid.currentTime > 0 && !vid.paused && !vid.ended && vid.readyState > 2) {
    //             scrubber.value = scrubber.max * (vid.currentTime / vid.duration);
    //             scrubber.dispatchEvent(new Event('input'));
    //         }
    //     }, 200);

    //     scrubber.addEventListener("input", function updateVidPos() {
    //         tripLenSeconds = vid.duration;
    //         let scrubPos = scrubber.value / scrubber.max;
    //         vid.currentTime = tripLenSeconds * scrubPos;
    //     });
    // }
    // else { console.warn(`No video found for ${tripName}.`); }

    // 2. Link scrubber to telemetry file
    scrubber.addEventListener("input", function updateTelBox() {
        let scrubPos = scrubber.value / scrubber.max;
        let totTelemetry = telemetry.duration_s;
        let i = Math.floor(totTelemetry * scrubPos);

        // console.log(i)
        printTelemetryData(i-1);
    });
    
    

    // 3. Link scrubber to time signature output
    if (tripLenSeconds) {
        scrubber.addEventListener("input", function updateScrubberOutput() {
            // calculate and set scrubber position in terms of trip duration
            let tripPos = Math.floor(tripLenSeconds * (scrubber.value / scrubber.max)),
                hours   = Math.floor(tripPos / 3600),
                minutes = Math.floor((tripPos % 3600) / 60),
                seconds = Math.round(tripPos % 60);

            document.getElementById("scrubber_value").value = 
                String(hours).padStart(2, '0')   + ':' +
                String(minutes).padStart(2, '0') + ':' +
                String(seconds).padStart(2, '0');
        });
    }
    else { console.warn(`No trip length given for ${tripName}.`); }
}

fetchTrips(); // loads list immediately
// setInterval(fetchTrips, 5000); // loads trip list at intervals of 3 seconds


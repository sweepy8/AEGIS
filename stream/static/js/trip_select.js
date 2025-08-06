// AEGIS stream dynamic elements - Trip Select
// AEGIS Senior Design, Created on 6/17/2025


/*
Python generates files --> Flask embeds html elements --> 
    JS detects (QueryAll) those elements --> JS loads data
*/

// NOTE: In order to be able to redirect dynamically allocated HTML elements 
// back to the Python scripts which generated them via url_for calls, you need 
// to create the url strings at render-time inside of the html. Those variables
// can then be accessed in all client-side js files. If a variable ending in URL
// appears to come from nowhere, check the head section of main.html.

async function selectTrip(tripBtnId) {

    // Update button visuals on click
    const selected_tag = '>> ';
    let btns = document.querySelectorAll('.trip_btn');
    btns.forEach(btn => {
        if (btn.id == tripBtnId && !(btn.innerText.includes(selected_tag))) {
            btn.innerText = selected_tag + btn.innerText;
        }
        else if (btn.id != tripBtnId && btn.innerText.includes(selected_tag)) {
            btn.innerText = btn.innerText.replace(selected_tag, '');
        }
    });

    // Trim button label into "tripN", where N is trip number
    const tripName = tripBtnId.replace(">>> ", '').replace("_btn", '');
    const telBox = document.getElementById("telemetry_data");
    const vidBox = document.getElementById("video_container");
    const playBtn = document.getElementById("play_btn");

    // Clear previous telemetry data
    Array.from(telBox.children).forEach(child => {telBox.removeChild(child);});

    // clear other embedded videos
    Array.from(vidBox.children).forEach(child => {vidBox.removeChild(child);});

    // Unlink scrubber from any previous trip
    await unlinkScrubber();

    // Attach a loading message until the video is loaded
    let waiting = document.createDocumentFragment()
        .appendChild(document.createElement('p'));
    waiting.innerText = "Loading video, please wait...";
    waiting.id = "loading_msg";
    waiting.style.textAlign = 'center';
    vidBox.append(waiting);

    if (tripName == "lf") { vidBox.append(insertLiveFeed()); } 
    else                  { vidBox.append(await insertVideo(tripName)); }
}

async function linkScrubberToTrip(tripName) {
    const scrubber = document.getElementById("scrubber");
    const vid = document.getElementById(`video_${tripName}`);
    const telFileURL = `/static/trips/${tripName}/tel_${tripName}.txt`;
    const telBox = document.getElementById("telemetry_data");

    var telArray = null;
    var tripLenSeconds = vid.duration;

    // Attempt to construct an array of telemetry data from file URL.
    try {
        // fetch api returns a promise to the file data
        const telFileData = await fetch(telFileURL);
        // awaits file data, then splits into array
        telArray = (await telFileData.text()).split('\n');
    }
    catch (error) { console.warn(error); }

    // 1. Link scrubber to video element
    if (vid) {

        // update scrubber value every 50ms
        var updateScrubberInterval = setInterval(() => {
            if (vid.currentTime > 0 && !vid.paused && !vid.ended && vid.readyState > 2) {
                scrubber.value = scrubber.max * (vid.currentTime / vid.duration);
                scrubber.dispatchEvent(new Event('input'));
            }
        }, 200);

        scrubber.addEventListener("input", function updateVidPos() {
            tripLenSeconds = vid.duration;
            let scrubPos = scrubber.value / scrubber.max;
            vid.currentTime = tripLenSeconds * scrubPos;
        });
    }
    else { console.warn(`No video found for ${tripName}.`); }

    // 2. Link scrubber to telemetry file
    if (telArray) {
        scrubber.addEventListener("input", function updateTelBox() {
            let scrubPos = scrubber.value / scrubber.max;
            let currLines = Math.floor(telArray.length * scrubPos);

            // Adds lines 'before' current position
            for (i = 0; i < currLines; i++) {
                let line = document.getElementById(`tl${i}`);
                if (!line) {
                    const fragment = document.createDocumentFragment();
                    const line = fragment.appendChild(document.createElement('p'));
                    line.textContent = `${telArray[i]}`;
                    line.id = `tl${i}`;
                    telBox.prepend(fragment);
                }
            }
            // Removes lines 'after' current position
            for (i = currLines; i < telArray.length; i++) {
                let line = document.getElementById(`tl${i}`);
                if (line) { telBox.removeChild(line); }
            }
        });
    }
    else {
        console.warn(`No telemetry data given for ${tripName}.`);
    };

    // 3. Link scrubber to time signature output
    if (tripLenSeconds) {
        scrubber.addEventListener("input", function updateScrubberOutput() {
            // calculate and set scrubber position in terms of trip duration
            let tripPos = tripLenSeconds * (scrubber.value / scrubber.max),
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

async function unlinkScrubber() {
    const scrubber = document.getElementById("scrubber");
    const playBtn = document.getElementById("play_btn");

    // Remove the periodic scrubber update caused by running videos
    if (window.updateScrubberInterval) { clearInterval(window.updateScrubberInterval); }

    scrubber.value = scrubber.min;
    document.getElementById("scrubber_value").value = "00:00:00";

    try {
        scrubber.removeEventListener("input", updateScrubberOutput);
        scrubber.removeEventListener("input", updateTelBox);
        scrubber.removeEventListener("input", updateVidPos);
        playBtn.removeEventListener("click", handlePlayBtn);
    }
    catch {
        console.warn("Attempted to unlink scrubber that was already unlinked.");
    }
}

function insertLiveFeed() {

    const fragment = document.createDocumentFragment();
    let liveFeed = fragment.appendChild(document.createElement('img'));
    liveFeed.id = "live_feed";
    liveFeed.class="live_feed";
    liveFeed.src = liveFeedURL;  // This comes from main.html. See note above
    liveFeed.alt = "Live Camera Feed";

    // Remove loading message
    let loadMsg = document.getElementById("loading_msg");
    if (loadMsg) { loadMsg.parentElement.removeChild(loadMsg); }

    return liveFeed;
}

async function insertVideo(tripName) {

    let videoURL = `/static/trips/${tripName}/video_${tripName}.mp4`;

    const fragment = document.createDocumentFragment();
    if ((await fetch(videoURL)).ok) {
        var video = fragment.appendChild(document.createElement('video'));
        video.innerText = "Loading video...";
        video.id = `video_${tripName}`;
        video.src = videoURL;
        video.type = "video/mp4";
        video.autoplay = false;
        video.playsInline = true;

        video.style.height = '100%';
        video.style.width = '100%';

        video.addEventListener('loadeddata', async function handleLoadedVid() {

            await linkScrubberToTrip(tripName);

            // Remove loading message
            let loadMsg = document.getElementById("loading_msg");
            if (loadMsg) { loadMsg.parentElement.removeChild(loadMsg); }

            // Add play/pause button functionality
            const playBtn = document.getElementById("play_btn");

            playBtn.addEventListener("click", function handlePlayBtn() {
                if (video.paused) {
                    video.play();
                    playBtn.innerText = '⏸';
                }
                else {
                    video.pause();
                    playBtn.innerText = '▶';
                }
            });

            // Provide play/pause functionality to spacebar by simulating click
            // document.addEventListener("keydown", function(event) {
            //     if (event.code === "space") {
            //         event.preventDefault();
            //         playBtn.dispatchEvent(new Event("click"));
            //     }
            // });
            // Perhaps add convenient shortcuts here? left/right for fwd/back?

        });
    }
    else {
        var video = fragment.appendChild(document.createElement('img'));
        video.id = "no_video_img";
        video.src = "static/images/no_video.gif";

        // Remove loading message
        let loadMsg = document.getElementById("loading_msg");
        if (loadMsg) { loadMsg.parentElement.removeChild(loadMsg); }
    }

    return video; 
}


// MAIN FUNCTION ---------------------------------------------------------------

async function main() {

    selectTrip('lf_btn');       // Initialize webpage to the live feed

    var trip_btns = document.querySelectorAll('.trip_btn');

    trip_btns.forEach(btn => {
        // Event listener expects a function reference. In order to pass args
        // we must wrap the function call in an arrow function
        btn.addEventListener("click", () => { selectTrip(btn.id); });
    });
}

main().catch(console.log)
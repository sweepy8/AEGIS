
// Captures trip data in array from file asynchronously ------------------------
async function captureTelArray(filename) {
    try {
        // returns a promise to the file data
        const response = await fetch(filename)
        // waits for the file data's text, then splits into an array
        const telArray = (await response.text()).split('\n');
        return telArray;
    }
    catch (error) { console.log(error); }
}

function initTripScrubber(tripLengthSeconds) {
    const scrubber = document.getElementById("scrubber");
    scrubber.addEventListener("input", function () {
        
        var tripPos = tripLengthSeconds * (scrubber.value / scrubber.max),
            hours   = Math.floor(tripPos / 3600),
            minutes = Math.floor((tripPos % 3600) / 60),
            seconds = Math.round(tripPos % 60);

        document.getElementById('scrub_pos').value = 
            String(hours).padStart(2, '0')   + ':' +
            String(minutes).padStart(2, '0') + ':' +
            String(seconds).padStart(2, '0');
    });
}

async function main() {
    var telFile = 'test.txt';
    var telArray = await captureTelArray(telFile);
    const tripLengthSeconds = 3785;

    initTripScrubber(tripLengthSeconds);


    const scrubber = document.getElementById("scrubber");

    scrubber.addEventListener("input", function () {
        let numLines = Math.floor(telArray.length * scrubber.value / scrubber.max);
        const box = document.getElementById("telemetry_box");

        const currLines = box.childNodes;

        // Adds lines 'below' current position
        for (i = 0; i < numLines; i++) 
        {
            if (document.getElementById(`tl${i}`) == null) {
                const fragment = document.createDocumentFragment();
                const line = fragment.appendChild(document.createElement('p'));
                line.textContent = `${i+1}: ${telArray[i]}`;
                line.id = `tl${i}`;
                box.appendChild(fragment);
            }
        }

        // Removes lines 'above' current position
        for (i = numLines; i < telArray.length; i++) {
            if (document.getElementById(`tl${i}`) != null) {
                box.removeChild(document.getElementById(`tl${i}`));
            }
        }

    });
}

main().catch(console.log);

/*
Python generates files --> Flask embeds html elements
    --> JS detects (QueryAll) those elements --> JS loads data
*/
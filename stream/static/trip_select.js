// AEGIS stream dynamic elements
// AEGIS Senior Design, Created on 6/17/2025

window.addEventListener("DOMContentLoaded", (event) => {

    var trip_btns = document.querySelectorAll('.trip_btn');

    trip_btns.forEach(btn => {
        btn.addEventListener("click", update_trip_btn);
        btn.addEventListener("click", select_trip)
    });

});

function update_trip_btn()
{
    const selected_tag = '>>> ';
    let btns = document.querySelectorAll('.trip_btn');

    btns.forEach(btn => {
        if ((btn === this) && (btn.innerText.includes(selected_tag) == false)) {
            btn.innerText = selected_tag + btn.innerText;
        }
        else if ((btn !== this) && (btn.innerText.includes(selected_tag) == true)) {
            btn.innerText = btn.innerText.replace(selected_tag, '');
        }
    });
}

function select_trip() {
    
}
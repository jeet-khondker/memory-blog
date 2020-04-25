const greeting = document.getElementById("greeting");

/************************
* FUNCTION: SAY GREETING
 ************************/
function sayGreeting() {
    if (new Date().getHours() < 10) {
        document.getElementById("greeting").innerHTML = "Good Morning ☀️";
    } else if (new Date().getHours() < 12) {
        document.getElementById("greeting").innerHTML = "Good Day 🌤";
    } else if (new Date().getHours() >= 12 && new Date().getHours() < 18) {
        document.getElementById("greeting").innerHTML = "Good Afternoon ⛅️";
    } else if (new Date().getHours() >= 18 && new Date().getHours() < 24) {
        document.getElementById("greeting").innerHTML = "Good Evening 🌙";
    } else {
        document.getElementById("greeting").innerHTML = '';
    }
}

/*****************************
* FUNCTION: PLAY DELETE SOUND
 ****************************/
function playDelSound(el) {
    var delSound = document.createElement("audio");
    var link = el.srcElement.attributes.href.textContent; 

    delSound.src = "/static/sounds/delete.mp3";
    delSound.play();
    setTimeout(function(){window.location = link;}, 1000);
    el.preventDefault(); 
}



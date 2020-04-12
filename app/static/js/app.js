function playDelSound(el) {
    var delSound = document.createElement("audio");
    var link = el.srcElement.attributes.href.textContent; 

    delSound.src = "/static/sounds/delete.mp3";
    delSound.play();
    setTimeout(function(){window.location = link;}, 1000);
    el.preventDefault(); 
}
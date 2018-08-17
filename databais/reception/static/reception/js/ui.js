
var modal = document.getElementById('email_box');
var overlay = document.getElementById("overlay");

function on() {
    overlay.style.display = "block";
    var email_input = document.getElementById("id_email");
    email_input.select();
}

function off() {
    overlay.style.display = "none";
}

window.onclick = function(event) {
    console.log(event.target, overlay.style.display);
    if ((event.target === overlay) && (overlay.style.display === "block")) {
        off()
    }
};




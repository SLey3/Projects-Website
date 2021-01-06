const isHover = e => e.parentElement.querySelector(':hover') === e;

let navbar = document.getElementById('nav');
document.addEventListener('mousemove', function checkNavHover() {
    var hovered = isHover(navbar);
    if (hovered !== checkNavHover.hovered) {
        console.log(hovered ? 'hovered' : 'not hovered');
        checkNavHover.hovered = hovered;
        if (hovered) {
            const container = document.getElementById('cntnr');
            const seperator = document.getElementById('sep');
            const body = document.getElementById("body-content");
            container.style.marginLeft = "-45.75rem";
            body.style.right = "calc(-45.75rem + 94.01rem)"
            seperator.style.background = "rgb(44, 44, 44)";
        } else {
            const container = document.getElementById('cntnr');
            const seperator = document.getElementById('sep');
            const body = document.getElementById("body-content");
            container.style.marginLeft = '-66.32rem';
            body.style.right = '59.32rem';
            seperator.style.background = "rgb(128, 128, 128)";
        }
    }
});
const isHover = e => e.parentElement.querySelector(':hover') === e;

let navbar = document.getElementById('nav');
document.addEventListener('mousemove', function checkNavHover() {
    var hovered = isHover(navbar);
    if (hovered !== checkNavHover.hovered) {
        console.log(hovered ? 'hovered' : 'not hovered');
        checkNavHover.hovered = hovered;
        if (hovered) {
            const container = document.getElementById('cntnr');
            container.style.marginLeft = "-33.32rem";
        } else {
            const container = document.getElementById('cntnr');
            container.style.marginLeft = '-66.32rem';
        }
    }
});
const isHover = e => e.parentElement.querySelector(':hover') === e;

let navbar = document.getElementById('nav');
document.addEventListener('mousemove', function checkNavHover() {
    var hovered = isHover(navbar);
    if (hovered !== checkNavHover.hovered) {
        console.log(hovered ? 'Navbar Hovered' : 'Navbar Not Hovered');
        checkNavHover.hovered = hovered;
        if (hovered) {
            const container = document.getElementById('cntnr');
            const seperators = document.getElementsByName("sep");
            const body = document.getElementById("body-content");
            container.style.marginLeft = "-25.95rem";
            body.style.right = "15.12rem"
            for (s = 0; s < seperators.length; s++) {
                let seperator = seperators[s];
                seperator.style.background = "rgb(44, 44, 44)";
            }

        } else {
            const container = document.getElementById('cntnr');
            const seperators = document.getElementsByName('sep');
            const body = document.getElementById("body-content");
            container.style.marginLeft = '-45.01rem';
            body.style.right = '28.13rem';
            for (s = 0; s < seperators.length; s++) {
                let seperator = seperators[s];
                seperator.style.background = "rgb(128, 128, 128)";
            }
        }
    }
});
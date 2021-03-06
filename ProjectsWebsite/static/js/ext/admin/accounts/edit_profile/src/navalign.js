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
            const infTitle = document.getElementsByName("sub-title");
            container.style.marginLeft = "13.67rem";
            for (s = 0; s < seperators.length; s++) {
                let seperator = seperators[s];
                seperator.style.background = "rgb(44, 44, 44)";
            }
            for (i = 0; i < infTitle.length; i++) {
                let title = infTitle[i];
                title.style.whiteSpace = "nowrap";
            }

        } else {
            const container = document.getElementById('cntnr');
            const seperators = document.getElementsByName('sep');
            const infTitle = document.getElementsByName("sub-title");
            container.style.marginLeft = '-10rem';
            for (s = 0; s < seperators.length; s++) {
                let seperator = seperators[s];
                seperator.style.background = "rgb(128, 128, 128)";
            }
            for (i = 0; i < infTitle.length; i++) {
                let title = infTitle[i];
                title.style.whiteSpace = "pre-line";
            }
        }
    }
});
function show_pass(query, color, options) {
    var password = document.getElementById(query);
    var pass_icon = document.querySelector('.fa-lock');
    if (password.type == "password") {
        if (color) {
            pass_icon.style.color = color;
        } else {
            pass_icon.style.color = "#7f2092";
        }
        password.type = "text";
        if (options) {
            password.style.border = options[0];
            password.style.width = options[1];
        }
    } else {
        delete color;
        password.type = "password";
        if (options) {
            password.style.width = "50%";
        }
        delete options;
        pass_icon.style.color = "grey";
    }
}
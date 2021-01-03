function show_confirm(query, color, options) {
    var confirm_password = document.getElementById(query);
    var confirm_pass_icon = document.querySelector('.fa-check');
    if (confirm_password.type === "password") {
        if (color) {
            confirm_pass_icon.style.color = color;
        } else {
            confirm_pass_icon.style.color = "#7f2092";
        }
        confirm_password.type = "text";
        if (options) {
            confirm_password.style.border = options[0];
            confirm_password.style.width = options[1];
        }
    } else {
        delete color;
        confirm_password.type = "password";
        if (options) {
            confirm_password.style.width = "50%";
        }
        delete options;
        confirm_pass_icon.style.color = "grey";
    }
}
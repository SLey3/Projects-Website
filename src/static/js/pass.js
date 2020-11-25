function show_pass() {
    var password = document.getElementById('password');
    var pass_icon = document.querySelector('.fa-lock');
    if (password.type === "password") {
        password.type = "text";
        pass_icon.style.color = "#7f2092";
    } else {
        password.type = "password";
        pass_icon.style.color = "grey";
    }
}
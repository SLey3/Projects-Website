function show_confirm() {
    var confirm_password = document.getElementById('confirm_pass');
    var confirm_pass_icon = document.querySelector('.fa-check');
    if (confirm_password.type === "password") {
        confirm_password.type = "text";
        confirm_pass_icon.style.color = "#7f2092";
    } else {
        confirm_password.type = "password";
        confirm_pass_icon.style.color = "grey";
    }
}
function NoValidateInput() {
    var inputs = document.getElementsByTagName('input');
    for (var i = 0; i < inputs.length; i++) {
        if (inputs[i].type.toLowerCase() == 'text') {
            var input = inputs[i];
            input.removeAttribute("required");
            input.setAttribute("novalidate");
        }
    }
}
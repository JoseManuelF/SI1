// Script de las funcionalidades de register.html

function checkPassword(pass1, pass2){
    var n = pass1.value.localeCompare(pass2.value);
    if(n != 0) {
        pass2.pattern = "";
    } else {
        pass2.pattern = "*";
        window.location.href = "../html/home.html";
    }
}

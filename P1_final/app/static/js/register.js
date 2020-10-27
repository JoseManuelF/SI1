// Script de las funcionalidades de register.html

function checkPassword(){
    var pass1 = document.getElementsByName('psw')[0];
    var pass2 = document.getElementsByName('repeat_psw')[0];

    var pass2_title = document.getElementById('repeat_psw_title');

    // Comparamos las contraseñas
    var n = pass1.value.localeCompare(pass2.value);
    if(n != 0) {
        pass2.setCustomValidity("Las contraseñas no coinciden.");
        pass2_title.style.color = 'red';
        pass2.style.color = 'red';
    } else {
        pass2.setCustomValidity("");
        pass2_title.style.color = 'black';
        pass2.style.color = 'black';
    }
}

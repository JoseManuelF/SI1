// Script de las funcionalidades de home.html

function menuButton(){
    var menu = document.getElementById("menu");

    if(window.getComputedStyle(menu, null).getPropertyValue("display") != "none"){
        menu.style.display = "none";
    } else{
        menu.style.display = "block";
    }
}

function categoriesButton(){
    var categ = document.getElementById("category");
    var despl = document.getElementById("desplegable");

    if(window.getComputedStyle(categ, null).getPropertyValue("display") != "none"){
        categ.style.display = "none";
        despl.src="../media/Desplegable.png"; // Las categorías no han sido desplegadas
    } else{
        categ.style.display = "block";
        despl.src="../media/Desplegable2.png"; // Las categorías se despliegan
    }
}

function loginWindow(){
    var login = document.getElementById("loginForm");

    if(window.getComputedStyle(login, null).getPropertyValue("display") != "none"){
        login.style.display='none';
    } else{
        login.style.display='block';
    }
}

function profileStatus(){
    var prof = document.getElementById("profile");
    prof.innerHTML = "Your name"; // Actualiza el nombre del usuario
}

// When the user clicks anywhere outside of the login form, close it
window.onclick = function(event) {
    // Get the login form
    var login = document.getElementById("loginForm");

    if (event.target == login) {
        login.style.display = "none";
    }
}




menu_opener = document.getElementById('navbar-menu')
menu_dropdown = document.getElementById('navbar-menu-dd')
menu_just_opened = false


menu_opener.onclick = function(){
    menu_dropdown.classList.toggle("open")

}

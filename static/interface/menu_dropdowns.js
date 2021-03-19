


menu_opener = document.getElementById('navbar-menu')
menu_dropdown = document.getElementById('navbar-menu-dd')
menu_just_opened = false


menu_opener.onclick = function(){
    menu_dropdown.classList.add("open")
    menu_just_opened = true
    console.log("opened dropdown")
}

document.onclick = function(){
    if (menu_just_opened){
        menu_just_opened = false
    }else{
        menu_dropdown.classList.remove("open")
        console.log("closed dropdown")
    }

}
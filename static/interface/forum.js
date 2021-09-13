
function toggle_spoiler(element){
    if (element.parentNode.parentNode.getElementsByTagName('div')[1].getElementsByTagName('div')[0].style.display != '')
    {
        element.parentNode.parentNode.getElementsByTagName('div')[1].getElementsByTagName('div')[0].style.display = '';
        element.innerText = '';
        element.value = 'Спойлер';
    }
    else {
        element.parentNode.parentNode.getElementsByTagName('div')[1].getElementsByTagName('div')[0].style.display = 'none';
        element.innerText = '';
        element.value = 'Спойлер';
    }


}

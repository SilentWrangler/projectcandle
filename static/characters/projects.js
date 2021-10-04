
const authtoken = document.getElementById('auth').value;

function httpGetAsync(theUrl, callback)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
            callback(xmlHttp.responseText);
    }
    xmlHttp.open("GET", theUrl, true); // true for asynchronous
    xmlHttp.send(null);
}


function httpPostAsync(theUrl, callback, data = null)
{
    var xmlHttp = new XMLHttpRequest();

    xmlHttp.onreadystatechange = function() {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
            callback(xmlHttp.responseText);
    }
    xmlHttp.open("POST", theUrl, true); // true for asynchronous
    xmlHttp.setRequestHeader('Authorization', `Token ${authtoken}`)
    xmlHttp.send(data);
}

function start_project(target, type, form){
    url = `/projects/api/start_character_project?target=${target}&project=${type}`;
    data = new FormData( form );
    httpPostAsync(url, (response) =>{
        console.log(response)
        document.location.reload()
    }, data)
}

registered = {}

function register_form(target, type, element){
    if (registered[type]){
        console.log(`form already registered: ${type}`);
        return;
    }
    console.log(`listener added: ${type}`);
    element.addEventListener("submit",function (event){
        event.preventDefault();
        console.log("event fired");
        start_project(target, type, element);
    });
    registered[type] = true;
}

function restart_project(id){
    url = `/projects/api/restart?project=${id}`;
    httpPostAsync(url, (response) =>{
        console.log(response)
        document.location.reload()
    })
}

function stop_project(id){
    con = confirm("Действительно забросить?")
    if (!con) return;
    url = `/projects/api/stop?project=${id}`;
    httpPostAsync(url, (response) =>{
        console.log(response)
        document.location.reload()
    })
}

function setqueue(id,priority){
    url = `/projects/api/set_priority?project=${id}&priority=${priority}`;
    httpPostAsync(url, (response) =>{
        console.log(response)
        document.location.reload()
    })

}


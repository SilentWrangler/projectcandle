const tile_size = 425;
const atlas_src = "/static/map/hires_wip.png";
const atlas_cols = 6;
var scale = 0.2;

const min_scale = 0.0025;
const max_scale = 0.5;
const scale_step = 0.0005;


var ImageIndexes = {};

ImageIndexes.main_biome = {
    "WTR": 0,
    "PLN": 6,
    "DSR": 12
};

ImageIndexes.biome_mod= {
    "NON":0,
    "FRT":1,
    "SWP":2,
    "HLS":3,
    "MNT":4
}

ImageIndexes.city = {
    "GEN":18,
    "MAN":24,
    "FRM":30,
    "LBR":36,
    "DEF":42,
    "FCT":48,
    "MIN":54,
    "SRL":60
}


Aliases = {}

Aliases.biomes = {

    "WTR": {
        "":gettext("Море"),
    },
    "PLN": {
        "NON":gettext("Плодородные поля"),
        "FRT":gettext("Зелёные леса"),
        "SWP":gettext("Болота"),
        "HLS":gettext("Холмы"),
        "MNT":gettext("Горы")
    },
    "DSR": {
        "NON":gettext("Пустыня"),
        "FRT":gettext("Жаркие леса"),
        "SWP":gettext("Оазис"),
        "HLS":gettext("Дюны"),
        "MNT":gettext("Пустынные горы")
    }

}

Aliases.cities = {
    "GEN":gettext("Жилые кварталы"),
    "MAN":gettext("Сборщики маны"),
    "FRM":gettext("Фермы"),
    "LBR":gettext("Библиотеки"),
    "DEF":gettext("Форт"),
    "FCT":gettext("Фабрика"),
    "MIN":gettext("Шахта"),
    "SRL":gettext("Гнездо Печали")
}

Aliases.races = {
    'HUM':"Люди",
    'ELF':"Эльфы",
    'ORC':"Орки",
    'DWA':"Дварфы",
    'GOB':"Гоблины",
    'FEY':"Феи"
}

function resizeCanvas(canvas){
    canvas.width= window.innerWidth*0.8;
    canvas.height=window.innerHeight*0.8;
}



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
//
// Asset loader
//

var Loader = {
    images: {}
};

Loader.loadImage = function (key, src) {
    var img = new Image();

    var d = new Promise(function (resolve, reject) {
        img.onload = function () {
            this.images[key] = img;
            resolve(img);
        }.bind(this);

        img.onerror = function () {
            reject("Could not load image: " + src);
        };
    }.bind(this));

    img.src = src;
    return d;
};

Loader.getImage = function (key) {
    return (key in this.images) ? this.images[key] : null;
};


//
// Keyboard handler
//

var Keyboard = {};

Keyboard.LEFT = 37;
Keyboard.RIGHT = 39;
Keyboard.UP = 38;
Keyboard.DOWN = 40;

Keyboard._keys = {};

Keyboard.listenForEvents = function (keys) {
    window.addEventListener('keydown', this._onKeyDown.bind(this));
    window.addEventListener('keyup', this._onKeyUp.bind(this));

    keys.forEach(function (key) {
        this._keys[key] = false;
    }.bind(this));
}

Keyboard._onKeyDown = function (event) {
    var keyCode = event.keyCode;
    if (keyCode in this._keys) {
        event.preventDefault();
        this._keys[keyCode] = true;
    }
};

Keyboard._onKeyUp = function (event) {
    var keyCode = event.keyCode;
    if (keyCode in this._keys) {
        event.preventDefault();
        this._keys[keyCode] = false;
    }
};

Keyboard.isDown = function (keyCode) {
    if (!keyCode in this._keys) {
        throw new Error('Keycode ' + keyCode + ' is not being listened to');
    }
    return this._keys[keyCode];
};



function Camera(map, width, height) {
    this.minX = 0;
    this.minY = 0;
    this.x = this.minX;
    this.y = this.minY;
    this.width = width;
    this.height = height;
    this.maxX = map.cols * (map.tsize*scale) - width;
    this.maxY = map.rows * (map.tsize*scale) - height;
}

Camera.SPEED = 256; // pixels per second

Camera.prototype.move = function (delta, dirx, diry) {
    // move camera
    this.x += dirx * Camera.SPEED * delta;
    this.y += diry * Camera.SPEED * delta;
    // clamp values
    this.x = Math.max(this.minX, Math.min(this.x, this.maxX));
    this.y = Math.max(this.minY, Math.min(this.y, this.maxY));
};


Camera.prototype.cellToScreen = function(x,y){

    var xScreen = x*tile_size*scale - this.x;
    var yScreen = x*tile_size*scale - this.y;

    return [xScreen,yScreen]

}

Camera.prototype.screenToCell = function(x,y){



    var xCell = Math.floor((this.x+x) / (tile_size*scale));
    var yCell = Math.floor((this.y+y) / (tile_size*scale));
    return [xCell,yCell]

}


MapPainter = {};

MapPainter.update = function (delta) {
    // handle camera movement with arrow keys
    var dirx = 0;
    var diry = 0;
    if (Keyboard.isDown(Keyboard.LEFT)) { dirx = -1; }
    if (Keyboard.isDown(Keyboard.RIGHT)) { dirx = 1; }
    if (Keyboard.isDown(Keyboard.UP)) { diry = -1; }
    if (Keyboard.isDown(Keyboard.DOWN)) { diry = 1; }

    this.camera.move(delta, dirx, diry);
};

MapPainter.run = function (context) {
    this.ctx = context;
    this._previousElapsed = 0;

    var p = this.load();
    Promise.all(p).then(function (loaded) {
        this.init();
        window.requestAnimationFrame(this.tick);
    }.bind(this));
};

MapPainter.tick = function (elapsed) {
    window.requestAnimationFrame(this.tick);

    // clear previous frame
    this.ctx.clearRect(0, 0, this.dimensions.x, this.dimensions.y);

    // compute delta time in seconds -- also cap it
    var delta = (elapsed - this._previousElapsed) / 1000.0;
    delta = Math.min(delta, 0.25); // maximum delta of 250 ms
    this._previousElapsed = elapsed;

    this.update(delta);
    this.render();
}.bind(MapPainter);


MapPainter.init = function(){
    this.atlas = Loader.getImage('tset');
    var canvas = document.getElementById('map');
    resizeCanvas(canvas);


    this.ctx = canvas.getContext('2d');
    this.dimensions = {"x":canvas.width,"y":canvas.height};
    var worldJSON = document.getElementById('world').innerHTML;
    this.cell_data = JSON.parse(worldJSON);
    var map = {'cols':this.cell_data.width,'rows':this.cell_data.height,'tsize':tile_size}
    this.camera = new Camera(map, canvas.width, canvas.height);
    Keyboard.listenForEvents(
        [Keyboard.LEFT, Keyboard.RIGHT, Keyboard.UP, Keyboard.DOWN]);
    canvas.addEventListener("mouseout",canvasMouseLeaveHandler);
    canvas.addEventListener("mouseover",canvasMouseOverHandler);
    canvas.addEventListener("mousedown",canvasMouseDownHandler);
    canvas.addEventListener("mouseup",canvasMouseUpHandler);
    canvas.addEventListener("mousemove",canvasMouseMoveHandler);

}


MapPainter.render = function(){
    var cells = this.cell_data.cells;

    var renderCell = function(cell,xPos,yPos){


        var ii = ImageIndexes.main_biome[cell.main_biome]; //Draw main biome underneath
        var xSor = 0;
        var ySor = Math.floor(ii/atlas_cols)*tile_size;
        MapPainter.ctx.drawImage(
            MapPainter.atlas,
            xSor, ySor,
            tile_size,tile_size,
            xPos,yPos,
            tile_size*scale,tile_size*scale
            );

        ii = ImageIndexes.biome_mod[cell.biome_mod]; //Draw modification on top
        xSor = ii*tile_size;
        MapPainter.ctx.drawImage(
            MapPainter.atlas,
            xSor, ySor,
            tile_size,tile_size,
            xPos,yPos,
            tile_size*scale,tile_size*scale
            );

        if (cell.city_type!=""){
            ii = ImageIndexes.city[cell.city_type]+cell.city_tier-1; //Draw a city, if there is one
            xSor = (ii%atlas_cols)*tile_size;
            ySor = Math.floor(ii/atlas_cols)*tile_size;
            MapPainter.ctx.drawImage(
                MapPainter.atlas,
                xSor, ySor,
                tile_size,tile_size,
                xPos,yPos,
                tile_size*scale,tile_size*scale
            );

        }

    }

    var startCol = Math.floor((this.camera.x) / (tile_size*scale));
    var endCol = Math.min(startCol + Math.floor(this.camera.width / (tile_size*scale))+1,this.cell_data.width-1);
    var startRow = Math.floor((this.camera.y) / (tile_size*scale));
    var endRow = Math.min(startRow + Math.floor(this.camera.height / (tile_size*scale))+1,this.cell_data.height-1);

    var offsetX = -this.camera.x + startCol * (tile_size*scale);
    var offsetY = -this.camera.y + startRow * (tile_size*scale);

    for(var c = startCol; c <= endCol; c++){
        for (var r = startRow; r <= endRow; r++) {
            var idx =c*this.cell_data.height+r
            var cell = cells[idx];

            var x = (c - startCol) * (tile_size*scale)+ offsetX;
            var y = (r - startRow) * (tile_size*scale)+ offsetY;

            renderCell(cell,x,y);

        }
    }


}

MapPainter.load = function(){

    return[
        Loader.loadImage('tset',atlas_src)
        ];
}



window.onload = function (){
    var context = document.getElementById('map').getContext('2d');
    MapPainter.run(context);
}

window.onresize = function(){
    var canvas = document.getElementById('map');
    resizeCanvas(canvas);
    var map = {'cols':MapPainter.cell_data.width,'rows':MapPainter.cell_data.height,'tsize':tile_size}
    MapPainter.camera = new Camera(map, canvas.width, canvas.height);
}


bp =  document.getElementById('scale_plus');
bm =  document.getElementById('scale_minus');
scale_range = document.getElementById('scale_range');


upscale = function(){
    rescale(scale+scale_step);
    MapPainter.render();
}
downscale = function(){
    rescale(scale-scale_step);
    bp.disabled = false;

}

rangescale = function(event){
    rescale(scale_range.value);
}

rescale = function(new_scale){
    var prev_scale = scale;


    scale = Math.min(Math.max(min_scale,new_scale),max_scale);


    bm.disabled = scale<=min_scale;

    bp.disabled = scale>=max_scale;

    scale_range.value = scale;

    var camera = MapPainter.camera;
    camera.maxX = MapPainter.cell_data.width * (tile_size*scale) - camera.width;
    camera.maxY = MapPainter.cell_data.height * (tile_size*scale) - camera.height;

    var temp_x = camera.x + camera.width/2;
    temp_x = temp_x/(tile_size*prev_scale);
    temp_x = temp_x*tile_size*scale;
    camera.x = temp_x - camera.width/2;

    var temp_y = camera.y + camera.height/2;
    temp_y = temp_y/(tile_size*prev_scale);
    temp_y = temp_y*tile_size*scale;
    camera.y = temp_y - camera.height/2 ;


    camera.x = Math.max(camera.minX, Math.min(camera.x, camera.maxX));
    camera.y = Math.max(camera.minY, Math.min(camera.y, camera.maxY));

    MapPainter.render();
}

bp.onclick = upscale;
bm.onclick = downscale;
scale_range.oninput= rangescale;


display_celldata = function(response){
    cell = JSON.parse(response).data;

    celldata =  document.getElementById("celldata");

    celldata.class = "cellinfo";

    cell_info = document.getElementById("celldata-info-coord");
    cell_info.innerHTML = `${cell.x}x${cell.y}`


    cell_info = document.getElementById("celldata-info-biome");
    cell_info.innerHTML = `${Aliases.biomes[cell.main_biome][cell.biome_mod]}`


    cell_info_city = document.getElementById('celldata-info-city');
    cell_info_city.innerHTML = "";
    cell_info_pops = document.getElementById('celldata-info-pops');
    cell_info_pops.innerHTML = "";
    if (cell.city_tier>0){
        cell_info_city.innerHTML = `${Aliases.cities[cell.city_type]} LVL ${cell.city_tier}`

        cell_info_pops.innerHTML = '<table style="border:none">';


         var counter = {
            'HUM':0,
            'ELF':0,
            'ORC':0,
            'DWA':0,
            'GOB':0,
            'FEY':0
         };

         cell.pops.forEach((i)=>{
             counter[i.race]+=1;
         });

         for (const [r,c] of Object.entries(counter)){
             if (c>0){
             cell_info_pops.innerHTML += `<tr><td>${Aliases.races[r]}</td><td> ${c}</td></tr>`
             }
         }
        cell_info_pops.innerHTML += "</table>";
        cell_info_chars = document.getElementById('celldata-info-chars');
        cell_info_chars.innerHTML = '';
        cell.characters.forEach((char)=>{
            cell_info_chars.innerHTML+=`<tr><a href="/characters/${char.id}">${char.name}</a></tr>`
        });
    }


}


var dragflag = false;
var canvas_mouseover = false;

canvasMouseLeaveHandler = function(event){
    canvas_mouseover = false;
    dragflag = false;
}

canvasMouseOverHandler = function(event){
    canvas_mouseover = true;
}

canvasMouseDownHandler = function(event){
    dragflag = true;

}

canvasMouseUpHandler = function(event){
    dragflag = false;

}


var coords;
var timeoutid = 0;

canvasMouseMoveHandler = function(event){
    if (dragflag){
        event.preventDefault();
        var camera = MapPainter.camera;
        camera.x -= event.movementX;
        camera.y -= event.movementY;
        camera.x = Math.max(camera.minX, Math.min(camera.x, camera.maxX));
        camera.y = Math.max(camera.minY, Math.min(camera.y, camera.maxY));
        MapPainter.render();

    }
    else{
        var rect = MapPainter.ctx.canvas.getBoundingClientRect();
        var offsetX = rect.left;
        var offsetY = rect.top;

        mouseX=parseInt(event.clientX-offsetX);
        mouseY=parseInt(event.clientY-offsetY);

        if (coords){
            if (MapPainter.camera.screenToCell(mouseX,mouseY)!=coords){
                clearTimeout(timeoutid);
            }
        }

        coords = MapPainter.camera.screenToCell(mouseX,mouseY);


        timeoutid = setTimeout(()=>{
            if (!canvas_mouseover){return;}

            var url = `/world/api/getcell?world=${MapPainter.cell_data.id}&x=${coords[0]}&y=${coords[1]}`;

            httpGetAsync(url,display_celldata);
        },100);

    }

}



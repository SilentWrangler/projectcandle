const tile_size = 425;
const atlas_src = "/static/map/hires_wip.png";
const atlas_cols = 6;
const scale = 0.2;

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
    this.x = 0;
    this.y = 0;
    this.width = width;
    this.height = height;
    this.maxX = map.cols * map.tsize - width;
    this.maxY = map.rows * map.tsize - height;
}

Camera.SPEED = 256; // pixels per second

Camera.prototype.move = function (delta, dirx, diry) {
    // move camera
    this.x += dirx * Camera.SPEED * delta;
    this.y += diry * Camera.SPEED * delta;
    // clamp values
    this.x = Math.max(0, Math.min(this.x, this.maxX));
    this.y = Math.max(0, Math.min(this.y, this.maxY));
};



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
    canvas.width= window.innerWidth*0.9;
    canvas.height=window.innerHeight*0.9;
    this.ctx = canvas.getContext('2d');
    this.dimensions = {"x":canvas.width,"y":canvas.height};
    var worldJSON = document.getElementById('world').innerHTML;
    this.cell_data = JSON.parse(worldJSON);
    var map = {'cols':this.cell_data.width,'rows':this.cell_data.height,'tsize':tile_size}
    this.camera = new Camera(map, canvas.width, canvas.height);
    Keyboard.listenForEvents(
        [Keyboard.LEFT, Keyboard.RIGHT, Keyboard.UP, Keyboard.DOWN]);

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

    var startCol = Math.floor(this.camera.x / (tile_size*scale));
    var endCol = startCol + (this.camera.width / (tile_size*scale))+1;
    var startRow = Math.floor(this.camera.y / (tile_size*scale));
    var endRow = startRow + (this.camera.height / (tile_size*scale))+1;

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

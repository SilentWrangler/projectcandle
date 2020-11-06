const tile_size = 16;
const atlas_src = "/static/map/placeholder.png";
const atlas_cols = 6;

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



MapPainter = {}


MapPainter.render = function(response){
    var object = JSON.parse(response)
    var cells = object.data.cells;

    var renderCell = function(cell){
        var xPos = cell.x * tile_size;
        var yPos = cell.y * tile_size;

        var ii = ImageIndexes.main_biome[cell.main_biome]; //Draw main biome underneath
        var xSor = 0;
        var ySor = Math.floor(ii/atlas_cols)*tile_size;
        MapPainter.ctx.drawImage(
            MapPainter.atlas,
            xSor, ySor,
            tile_size,tile_size,
            xPos,yPos,
            tile_size,tile_size
            );

        ii = ImageIndexes.biome_mod[cell.biome_mod]; //Draw modification on top
        xSor = ii*tile_size;
        MapPainter.ctx.drawImage(
            MapPainter.atlas,
            xSor, ySor,
            tile_size,tile_size,
            xPos,yPos,
            tile_size,tile_size
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
                tile_size,tile_size
            );

        }

    }
    cells.forEach(renderCell);

}

MapPainter.load = function(context,atlas,wid){
    this.ctx = context;
    this.atlas = atlas;
    httpGetAsync("api/getworld/"+wid,this.render);

}

window.onload = function (){
    var context = document.getElementById('map').getContext('2d');
    var p = Loader.loadImage('tset',atlas_src);
    p.then((result) =>{
        var atlas = Loader.getImage('tset');
        var wid = document.getElementById('wid').value;
        MapPainter.load(context,atlas,wid);
    }
    );

}

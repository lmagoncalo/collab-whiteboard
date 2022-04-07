const socket = io();

// ------------- Whiteboard -------------

let canvas = document.getElementById('whiteboard-canvas');
let ctx = canvas.getContext('2d');
let clientWidth = window.screen.width;
let clientHeight = window.screen.height;
canvas.width = clientWidth; //document.width is obsolete
canvas.height = clientHeight; //document.height is obsolete


let n_x_squares = 80;
let n_y_squares = 45;
let square_size_x = Math.floor(clientWidth / n_x_squares);
let square_size_y = Math.floor(clientHeight / n_y_squares);

// Color picker
let currentColor = '#ff0000';

function drawOnCanvas(x, y, color) {
    ctx.fillStyle = color;
    ctx.fillRect(x * square_size_x, y * square_size_y, square_size_x, square_size_y);
}

function startDraw(e) {
    // Hack to draw even if cursor doesn't move
    // let x = e.offsetX || e.layerX - canvas.offsetLeft;
    // let y = e.offsetY || e.layerY - canvas.offsetTop;
    let x = e.layerX;
    let y = e.layerY;

    x = Math.floor(x / square_size_x);
    y = Math.floor(y / square_size_y);

    currentPixel = {
        x: x,
        y: y,
        color: currentColor,
    };

    drawOnCanvas(x, y, currentColor);

    socket.emit('pixel-place', currentPixel);

    currentColor = '#' + Math.floor(Math.random()*16777215).toString(16);
}

canvas.addEventListener('mousedown', startDraw, false);

socket.on('new-pixel', function(data) {
    drawOnCanvas(data.x, data.y, data.color);
});

socket.on('draw-pixels', function(data) {
    for (let i = 0; i < data.length; i++) {
        let pixel = data[i];
        console.log(pixel);
        drawOnCanvas(pixel.x, pixel.y, pixel.color);
    }
});
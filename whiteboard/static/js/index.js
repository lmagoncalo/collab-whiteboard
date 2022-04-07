const socket = io();

// ------------- Users -------------
socket.on('users', function(msg) {
    document.getElementById('user-count').textContent = msg + ' online';
});



// ------------- Whiteboard -------------
let brush = document.getElementById('brush');
let brushCtx = brush.getContext('2d');
let brushCenterX = brush.width / 2;
let brushCenterY = brush.height / 2;
brushCtx.lineWidth = 1;
function drawBrush(width) {
    brushCtx.clearRect(0, 0, brush.width, brush.height);
    brushCtx.beginPath();
    brushCtx.arc(brushCenterX, brushCenterY, width / 2, 0, 2 * Math.PI, false);
    brushCtx.stroke();
}

let canvas = document.getElementById('whiteboard-canvas');
let ctx = canvas.getContext('2d');
ctx.lineCap = 'round';
ctx.lineJoin = 'round';

let currentStroke = null;
// When undo is pressed, pop top stroke off and redraw
let strokes = [];

// Color picker
let colorPicker = document.getElementById('color-picker');
let currentColor = '#' + colorPicker.value;
colorPicker.onchange = function() {
    currentColor = '#' + this.value;
};

function drawNewPoint(e) {
    brush.style.top = e.clientY - brushCenterY + 'px';
    brush.style.left = e.clientX - brushCenterX + 'px';
    if (currentStroke === null)
        return;

    // cross-browser canvas coordinates
    let x = e.offsetX || e.layerX - canvas.offsetLeft;
    let y = e.offsetY || e.layerY - canvas.offsetTop;

    currentStroke.points.push({x: x, y: y});
    drawOnCanvas(currentStroke.points, currentStroke.color, currentStroke.thickness);

    socket.emit('stroke-update', {x: x, y: y})
}

function drawOnCanvas(plots, color, thickness) {
    ctx.beginPath();
    ctx.moveTo(plots[0].x, plots[0].y);

    for(let i = 1; i < plots.length; i++) {
      ctx.lineTo(plots[i].x, plots[i].y);
    }

    ctx.lineWidth = thickness;
    ctx.strokeStyle = color;
    ctx.stroke();
}

function startDraw(e) {
    if (eraseCheckbox.checked) {
        currentColor = '#FFFFFF';
    }

    // Hack to draw even if cursor doesn't move
    let x = e.offsetX || e.layerX - canvas.offsetLeft;
    let y = e.offsetY || e.layerY - canvas.offsetTop;

    currentStroke = {
        thickness: currentThickness,
        color: currentColor,
        points: [{x: x-1, y: y-1}]
    };

    socket.emit('stroke-start', currentStroke);

    drawNewPoint(e);
}

function endDraw() {
    strokes.push(currentStroke);
    currentStroke = null;

    if (eraseCheckbox.checked) {
        currentColor = '#' + colorPicker.value;
    }

    undoButton.disabled = false;
}


canvas.addEventListener('mousedown', startDraw, false);
canvas.addEventListener('mousemove', drawNewPoint, false);
canvas.addEventListener('mouseup', endDraw, false);

socket.on('draw-new-stroke', function(data) {
    drawOnCanvas(data.points, data.color, data.thickness);
});

socket.on('draw-strokes', function(data) {
    for (let i = 0; i < data.length; i++) {
        let stroke = data[i];
        drawOnCanvas(stroke.points, stroke.color, stroke.thickness);
    }
});
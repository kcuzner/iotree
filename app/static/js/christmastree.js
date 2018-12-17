const socket = io('http://localhost', { path: "/app/socket.io", transports: ['websocket'], upgrade: false });

socket.on('image', function(data) {
    var canvas = document.getElementById('canvas');
    var ctx = canvas.getContext('2d');
    var blob = new Blob([data.image], { type: 'image/jpeg' });
    var img = new Image();
    img.onload = function () {
        ctx.drawImage(img, 0, 0);
    }
    img.src = URL.createObjectURL(blob);
});


const socket = io('http://localhost', { path: "/app/socket.io", transports: ['websocket'], upgrade: false });

socket.on('image', function(data) {
    var canvas = document.getElementById('canvas');
    var ctx = canvas.getContext('2d');
    var blob = new Blob([data.image], { type: 'image/jpeg' });
    var img = new Image();
    img.onload = function () {
        console.log(img.width, img.height);
        width = img.width / img.height * 320
        ctx.drawImage(img, 0, 0, img.width, img.height, 0, 0, width, 320);
    }
    img.src = URL.createObjectURL(blob);
});


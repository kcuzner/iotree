const socket = io('http://localhost', { path: "/app/socket.io", transports: ['websocket'], upgrade: false });


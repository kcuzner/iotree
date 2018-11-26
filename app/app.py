#!/usr/bin/env python3

import eventlet
eventlet.monkey_patch()

import socketio
import argparse
from flask import Flask, render_template, send_from_directory
import redis

sio = socketio.Server()
app = Flask(__name__)
app.debug = True

path_prefix = ''

def stream_image():
    """
    Streams images from the server into sio
    """
    db_stream = redis.StrictRedis(host='127.0.0.1', port='6379')
    db_image = redis.StrictRedis(host='127.0.0.1', port='6379')
    ps = db_stream.pubsub()
    ps.subscribe('__keyspace@0__:image')
    while True:
        for message in ps.listen():
            if message['channel'] == b'__keyspace@0__:image' and\
                    message['data'] == b'set':
                data = db_image.get('image')
                sio.emit('image', {'image': data})

@app.route('/')
def index():
    global path_prefix
    return render_template('index.html', path_prefix=path_prefix)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('static/css', path)

@sio.on('connect')
def sio_connect(sid, environ):
    print('connect', sid, environ)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Christmas Tree Controller App')
    parser.add_argument('--path-prefix', default='/', help='Path prefix this app is running under (for reverse-proxy)')

    args = parser.parse_args()
    path_prefix = args.path_prefix

    eventlet.spawn(stream_image)

    app = socketio.Middleware(sio, app)
    eventlet.wsgi.server(eventlet.listen(('', 3000)), app)


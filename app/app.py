#!/usr/bin/env python3

import eventlet
eventlet.monkey_patch()

import socketio
import argparse, io, json
from flask import Flask, render_template, send_from_directory, request
import redis

sio = socketio.Server()
app = Flask(__name__)
app.debug = True

path_prefix = ''

def read_settings(filename):
    with open(filename) as f:
        return json.load(f)

def open_redis(settings):
    password = settings['redis-password'] if settings['redis-auth'] else None
    return redis.StrictRedis(host=settings['redis-hostname'], port=settings['redis-port'], password=password)

def stream_image(settings):
    """
    Streams images from the server into sio
    """
    db_stream = open_redis(settings)
    db_image = open_redis(settings)
    ps = db_stream.pubsub()
    ps.subscribe('__keyspace@0__:image')
    while True:
        for message in ps.listen():
            if message['channel'] == b'__keyspace@0__:image' and\
                    message['data'] == b'set':
                data = db_image.get('image')
                sio.emit('image', {'image': data})

db_app = None

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

@app.route('/pattern', methods=['POST'])
def pattern():
    j = request.get_json()
    #TODO: Some sanitizing
    db_app.publish('pixels', json.dumps(j))
    return json.dumps({ 'success': True }), 200, { 'content-type': 'application/json' }

@sio.on('connect')
def sio_connect(sid, environ):
    print('connect', sid, environ)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Christmas Tree Controller App')
    parser.add_argument('--settings', default='./settings.json')

    args = parser.parse_args()
    settings = read_settings(args.settings)

    args = parser.parse_args()
    path_prefix = settings['path-prefix']

    db_app = open_redis(settings)

    eventlet.spawn(stream_image, settings)

    app = socketio.Middleware(sio, app)
    eventlet.wsgi.server(eventlet.listen(('', 3000)), app)


#!/usr/bin/env python3

import eventlet
eventlet.monkey_patch()

import socketio
import argparse, io, json
from flask import Flask, render_template, send_from_directory, request, Response
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
    Streams images from the server as a generator

    Note that this opens its own redis connection and gets its own copies of
    the image sequence.
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
                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + data + b'\r\n')

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

@app.route('/video')
def video_feed():
    """
    Streams images from the server
    """
    db_stream = open_redis(settings)
    db_image = open_redis(settings)
    ps = db_stream.pubsub()
    ps.subscribe('__keyspace@0__:image')

    streamon = True

    def generate():
        while streamon:
            for message in ps.listen():
                if message['channel'] == b'__keyspace@0__:image' and\
                        message['data'] == b'set':
                    data = db_image.get('image')
                    yield (b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' + data + b'\r\n')

    response = Response(generate(),
            mimetype='multipart/x-mixed-replace; boundary=frame')

    @response.call_on_close
    def done():
        streamon = False
        ps.close()

    return response

def repack_pixels(raw):
    # Only support up to 50 pixels
    if len(raw) > 50:
        raw = raw[:50]
    # Sanitize the pixels
    for d in raw:
        if d['type'] == 'random-hue':
            step = float(d['step'])
            if step > 0.1:
                step = 0.1
            if step < 0:
                step = 0
            yield { 'type': 'random-hue', 'step': step }
        elif d['type'] == 'keyframe':
            keys = []
            for k in d['keys']:
                # Extract numeric data
                key = { 'r': int(k['r']), 'g': int(k['g']), 'b': int(k['b']) }
                if 'steps' in k:
                    key['steps'] = int(k['steps'])
                if 'max-steps' in k:
                    key['max-steps'] = int(k['max-steps'])
                # Clamp all numeric values at 0-255
                key = dict([(k, abs(v) & 0xFF) for k, v in key.items()])
                # Only accept specific key types
                if k['type'] == 'linear':
                    key['type'] = 'linear'
                    keys.append(key)
                elif k['type'] == 'sine':
                    key['type'] = 'sine'
                    keys.append(key)
                elif k['type'] == 'wall':
                    key['type'] = 'wall'
                    keys.append(key)
            # only accept up to 64 keyframes
            if len(keys) < 64:
                keys = keys[:64]
            yield { 'type': 'keyframe', 'keys': keys }
        else:
            raise ValueError('No such pixel type')


@app.route('/pattern', methods=['POST'])
def pattern():
    j = request.get_json()
    repacked = list(repack_pixels(j))
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


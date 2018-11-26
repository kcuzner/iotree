#!/usr/bin/env python3

import socketio
import eventlet
import argparse
from flask import Flask, render_template, send_from_directory

sio = socketio.Server()
app = Flask(__name__)
app.debug = True

path_prefix = ''

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

    app = socketio.Middleware(sio, app)
    eventlet.wsgi.server(eventlet.listen(('', 3000)), app)


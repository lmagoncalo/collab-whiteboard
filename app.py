from collections import defaultdict
from flask import Flask, render_template, url_for, request
from flask_socketio import SocketIO, emit
import os
import operator
from threading import Lock
import time
from colormap import rgb2hex, hex2rgb


# Taken from https://web.archive.org/web/20190420170234/http://flask.pocoo.org/snippets/35/
class ReverseProxied(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)


app = Flask(__name__)
# app.wsgi_app = ReverseProxied(app.wsgi_app)
socketio = SocketIO(app)

users = 0

button_pressed = False

pixels = {}
pixels_lock = Lock()

# Taken from https://stackoverflow.com/questions/32132648/python-flask-and-jinja2-passing-parameters-to-url-for
@app.context_processor
def override_url_for():
    if app.debug:
        return dict(url_for=dated_url_for)
    return dict(url_for=url_for)


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


@app.route('/')
def index():
    return render_template('index.html')


def get_all_pixels():
    """
    Retrieve pixels as a list.
    :return: list of pixels
    """
    # global pixels
    # return pixels.tolist()
    global pixels
    all_pixels = []
    for keys, value in pixels.items():
        all_pixels.append({'x': keys[0], 'y': keys[1], 'color': rgb2hex(*value)})
    return all_pixels


@socketio.on('connect')
def socket_connect():
    global users, button_clicks
    users += 1
    emit('draw-pixels', get_all_pixels())


# Whiteboard handling
@socketio.on('pixel-place')
def pixel_place(data):
    global pixels

    with pixels_lock:
        # print(data)
        color = hex2rgb(data['color'])
        pixels[(data['x'], data['y'])] = color

        update_pixel = {
            'x': data['x'],
            'y': data['y'],
            'color': data['color'],
        }

    emit('new-pixel', update_pixel, broadcast=True, include_self=False)

if __name__ == '__main__':
    print("Server running.")
    # socketio.run(app, host='0.0.0.0', debug=True)
    socketio.run(app, host='10.16.1.247', debug=False)



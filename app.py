from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import os
from threading import Lock
import pickle
from flask_apscheduler import APScheduler
import time


app = Flask(__name__)
# socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)
socketio = SocketIO(app, cors_allowed_origins="*")

scheduler = APScheduler()
scheduler.init_app(app)

pixels = {}
pixels_lock = Lock()


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
        all_pixels.append({'x': keys[0], 'y': keys[1], 'color': value})
    return all_pixels


@socketio.on('connect')
def socket_connect():
    print("Connected")
    emit('draw-pixels', get_all_pixels())


# Whiteboard handling
@socketio.on('pixel-place')
def pixel_place(data):
    global pixels

    with pixels_lock:
        # print(data)
        color = data['color']
        pixels[(data['x'], data['y'])] = color

        update_pixel = {
            'x': data['x'],
            'y': data['y'],
            'color': data['color'],
        }

    emit('new-pixel', update_pixel, broadcast=True, include_self=False)


@socketio.on('pixel-remove')
def pixel_remove(data):
    global pixels

    with pixels_lock:
        # print(data)
        del pixels[(data['x'], data['y'])]

        removed_pixel = {
            'x': data['x'],
            'y': data['y'],
        }

    emit('remove-pixel', removed_pixel, broadcast=True, include_self=False)


@scheduler.task('cron', id='save_pixels', minute=5) # every 2 minutes
def save_pixels():
    ts = time.time()
    with open('saves/pixels_{}.pickle'.format(int(ts)), 'wb') as handle:
        pickle.dump(pixels, handle, protocol=pickle.HIGHEST_PROTOCOL)


"""
with open('filename.pickle', 'rb') as handle:
    b = pickle.load(handle)
"""


if __name__ == '__main__':
    print("Server running.")
    scheduler.start()
    port = int(os.environ.get('PORT', 8080))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)


"""
# create a binary pickle file 
f = open("file.pkl","wb")

# write the python object (dict) to pickle file
pickle.dump(dict,f)

# close file
f.close()
"""



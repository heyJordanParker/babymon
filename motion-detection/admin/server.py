from __future__ import absolute_import

import cv2
import os
import io
from datetime import (
    datetime,
    timedelta
)
from threading import Thread
from functools import wraps
from flask import (
    send_file,
    abort,
    request,
    redirect,
    make_response,
    render_template
)

from lib import config
from admin import (
    state,
    server_webapp
)
from admin.lib import generate_session_token


class Server(Thread):
    _instance = None

    def __init__(self):
        super(Server, self).__init__()
        self.setDaemon(True)

    def run(self):
        """ Run the server."""
        server_webapp.run(host=config['host'], port=config['port'])

    @classmethod
    def startup(cls):
        """ Start the server in a thread and return. """
        if not Server._instance:
            Server._instance = Server()

        if not Server._instance.isAlive():
            super(Server, Server._instance).start()


session_token = generate_session_token()


def requires_auth(f):
    """Wrapper for routes that requires auth."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'session_id' not in request.cookies or \
           request.cookies['session_id'] != session_token:
            return login()
        return f(*args, **kwargs)
    return decorated


@server_webapp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        if str(request.form['password']) == str(config['password']):
            global session_token
            session_token = generate_session_token()
            response = make_response(redirect('/'))
            response.set_cookie('session_id', value=session_token)
            return response
        return redirect('/')


@server_webapp.route('/')
@requires_auth
def status():
    return render_template('home.html', state=state, config=config)


@server_webapp.route('/view')
@requires_auth
def view():
    return render_template('snapshot.html', state=state, img='/snapshot')


@server_webapp.route('/snapshot')
@requires_auth
def snapshot():
    img = cv2.imread(config['snapshot'])
    stamp = os.path.getmtime(config['snapshot'])
    stamp = datetime.fromtimestamp(stamp)
    stamp += timedelta(hours=3)
    stamp = stamp.strftime('%H:%M:%S')
    stamp += '; motion: %s' % config['camera_state']['motion']
    cv2.putText(img, stamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (128, 255, 128), 2)

    if config['camera_state']['motion']:
        x = config['camera_state']['motion_x']
        y = config['camera_state']['motion_y']
        w = config['camera_state']['motion_w']
        h = config['camera_state']['motion_h']
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    _, jpeg = cv2.imencode('.jpg', img)
    return send_file(io.BytesIO(jpeg.tostring()), mimetype='image/%s' % config['snapshot'][-3:])


@server_webapp.route('/arm')
@requires_auth
def arm():
    state['active'] = True
    return redirect('/')


@server_webapp.route('/disarm')
@requires_auth
def disarm():
    state['active'] = False
    return redirect('/')


@server_webapp.route('/logout')
@requires_auth
def logout():
    global session_token
    session_token = generate_session_token()
    return redirect('/')


@server_webapp.route('/health')
def health_check():
    return 'OK'

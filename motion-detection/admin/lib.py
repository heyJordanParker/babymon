from __future__ import absolute_import

import hashlib
from time import time
from lib import config
from flask import Flask


def generate_session_token():
    return hashlib.sha256(bytes(config['password']) + bytes(time())).hexdigest()

state = {}
state['active'] = False

server_webapp = Flask(config['identifier'])

from __future__ import absolute_import

import json

from lib import config
from lib.lib import log

from admin import state
from admin.runners.camera import CameraRunner
from admin.runners.md import MotionDetectionRunner

VIDEO_STREAMER = CameraRunner(True)
MOTION_DETECTOR = MotionDetectionRunner()

RUNNERS = [VIDEO_STREAMER, MOTION_DETECTOR]


def load_foreign_state():
    cam_state = {}

    try:
        with open(config['camera_state_file']) as infile:
            cam_state = json.load(infile)
    except Exception as e:
        log('Failed to load camera state: %s' % repr(e))

    config['camera_state'] = cam_state


def check():
    load_foreign_state()
    if state['active']:
        MOTION_DETECTOR.run()
    else:
        MOTION_DETECTOR.stop()

    for runner in RUNNERS:
        runner.check()

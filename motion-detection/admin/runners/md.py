from __future__ import absolute_import
import os
import re
import json

from lib.lib import (
    run_command,
    log,
    is_running
)
from admin.runners.base import BaseRunner


class MotionDetectionRunner(BaseRunner):

    CAMERA_ID = 'camera'
    COMMAND = '/bin/bash -c "APP_CONFIG=./resources/camera.yaml python md.py"'

    def __init__(self, enabled=False):
        self.enabled = enabled

    def run(self):
        self.enabled = True

    def stop(self):
        self.enabled = False

    def check(self):
        if self.enabled and not self._is_locked():
            log('Starting motion detection')
            self.run_background_command(self.COMMAND, timeout=0)
        elif not self.enabled and self._is_locked():
            log('Killing motion detection')
            self._kill()

    @classmethod
    def _get_lock_file(cls, resource):
        lock_root = os.path.realpath(cls.TMP_FOLDER)

        if not os.path.exists(lock_root):
            os.mkdir(lock_root)

        lock_name = re.sub(r'[^a-zA-Z0-9]+', '_', resource)
        return os.path.join(lock_root, lock_name + '.lock')

    @classmethod
    def _check_lock(cls, lock_file):
        """
        Check if the lock is active. If so - return the PID of the process that has locked the
        resource. If the lock is not valid - return None.

        :param resource: Name of the resource to lock.
        :param dir_name: Base directory to store lock files.
        :return: PID of the process holding the lock iff the lock is active, None otherwise.
        """

        # Check if the process that locked the file is still running
        try:
            if os.path.exists(lock_file):
                with open(lock_file, 'r') as lock_handle:
                    data = json.load(lock_handle)

                # Check if process is still running and proc name is still the same
                if is_running(data['pid']):
                    proc_name = run_command('ps -p %s -o comm=' % data['pid'])
                    if proc_name == data['name']:
                        return data['pid']
        except Exception as exc:
            log('Unexpected exception while checking for motion detector lock: %s' % repr(exc))

        return None

    @classmethod
    def _is_locked(cls):
        lock_file = cls._get_lock_file(cls.CAMERA_ID)
        return True if cls._check_lock(lock_file) else False

    @classmethod
    def _kill(cls):
        """
        Unlock a resource. Or shortly - kill the process that has locked the resource.

        :param resource: Name of the resource to lock
        :param dir_name: Base directory to store lock files, default is /var/tmp
        """
        lock_file = cls._get_lock_file(cls.CAMERA_ID)
        pid = cls._check_lock(lock_file)

        if pid:
            run_command('/bin/kill %s' % pid)

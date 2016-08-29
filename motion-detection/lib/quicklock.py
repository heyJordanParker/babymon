from __future__ import absolute_import
import os
import re
import json
import time

from lib import config
from lib.lib import (
    run_command,
    log,
    is_running
)


def _get_lock_file(resource, dir_name):
    lock_root = os.path.realpath(dir_name)

    if not os.path.exists(lock_root):
        os.mkdir(lock_root)

    lock_name = re.sub(r'[^a-zA-Z0-9]+', '_', resource)
    return os.path.join(lock_root, lock_name + '.lock')


def _check_lock(lock_file):
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
        log('Unexpected exception, unlocking: %s' % repr(exc))

    return None


def is_locked(resource, dir_name=config['tmp_folder']):
    lock_file = _get_lock_file(resource, dir_name)
    return True if _check_lock(lock_file) else False


def lock(resource=config['identifier'], dir_name=config['tmp_folder']):
    """
    Lock a resource so that if this function is called again before the lock is
    released, a RuntimeError will be raised.

    :param resource: Name of the resource to lock.
    :param dir_name: Base directory to store lock files.
    """
    # Check if the process that locked the file is still running 
    lock_file = _get_lock_file(resource, dir_name)
    locked_by_pid = _check_lock(lock_file)
    if locked_by_pid:
        raise RuntimeError('Resource %s is locked by PID %s' % (resource, locked_by_pid))


    # Create the lock with the current process information
    pid = os.getpid()
    proc_name = run_command('ps -p %s -o comm=' % pid)
    with open(lock_file, 'w') as lock_handle:
        json.dump({"name": proc_name, "pid": pid, "timestamp": int(time.time())}, lock_handle)


def force_unlock(resource, dir_name=config['tmp_folder']):
    """
    Unlock a resource. Or shortly - kill the process that has locked the resource.

    :param resource: Name of the resource to lock
    :param dir_name: Base directory to store lock files, default is /var/tmp
    """
    lock_file = _get_lock_file(resource, dir_name)
    pid = _check_lock(lock_file)

    if pid:
        run_command('/bin/kill %s' % pid)

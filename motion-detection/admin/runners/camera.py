import os
import socket
import time
from lib.lib import log
from admin.runners.base import BaseRunner


class CameraRunner(BaseRunner):

    VIDEO_PORT = 8554
    SNAPSHOT_FILE = '/tmp/camera.bmp'
    PROCESSES = ['vlc', 'ffmpeg', 'raspivid']
    COMMAND = "/usr/bin/sudo -u pi /bin/bash -c \"" \
              "raspivid -o - -t 0 -n -w 640 -h 360 | " \
              "tee >( ffmpeg -nostats -i pipe:0 -y -r 2 -updatefirst 1 /tmp/camera.bmp) | " \
              "cvlc -vvv stream:///dev/stdin --sout '#rtp{sdp=rtsp://:8554/babymon}' :demux=h264\""

    def __init__(self, enabled=False):
        self.enabled = enabled

    def run(self):
        self.enabled = True

    def stop(self):
        self.enabled = False

    def check(self):
        running = self._check_video_port() and self._check_snapshot_file()
        if self.enabled and not running:
            # Sanity kill for dangling processes
            for proc in self.PROCESSES:
                self.killall(proc)
            log('Starting video streaming')
            self.run_background_command(self.COMMAND, timeout=0)
            # sleep for a few seconds in order to get the process up and running. The ffmpeg part requires some time to
            # start creating the snapshots.
            timeout = 10.0
            while not self._check_snapshot_file() and timeout > 0:
                time.sleep(0.5)
                timeout -= 0.5
            if not self._check_snapshot_file():
                log('Failed to start the video streaming')
        elif not self.enabled and running:
            # import pdb;pdb.set_trace()
            log('Killing video streaming')
            for proc in self.PROCESSES:
                self.killall(proc)

    def _check_video_port(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1) # 1 second timeout
        connect_result = -1
        try:
            connect_result = sock.connect_ex(('127.0.0.1', self.VIDEO_PORT))
        except:
            pass

        return connect_result == 0

    def _check_snapshot_file(self):
        # Check if the snapshot was created in less than 2 seconds. If not - then we probably have a problem.
        try:
            last_modified_timestamp = os.path.getmtime(self.SNAPSHOT_FILE)
            return abs(time.time() - last_modified_timestamp) < 2
        except:
            return False

from datetime import datetime
from time import sleep
import cv2
import numpy
import json

from lib import config
from lib.lib import log


class MotionDetector(object):
    """
    Motion detection.
    """

    MIN_MOTION_SIZE = (5, 5)
    IMAGE_SIZE = (640, 360)
    DEBUG_FRAME_SCALE = 4.0
    HISTORY_SIZE = 10

    def __init__(self, camera, on_motion, cv2_detector=None, debug=False):
        """
        Create motion detector.
        :param camera: camera to be used for getting snapshots
        :param on_motion: function to be called if motion is detected
        :param cv2_detector: motion detector
        :param debug: controls the debug output
        """
        if not camera or not on_motion:
            raise AssertionError('Required argument not set - camera.')
        if cv2_detector:
            self.detector = cv2_detector
        elif hasattr(cv2, 'createBackgroundSubtractorMOG2'):
            self.detector = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=16, detectShadows=True)
        elif hasattr(cv2, 'BackgroundSubtractorMOG2'):
            self.detector = cv2.BackgroundSubtractorMOG2(history=100, varThreshold=16, bShadowDetection=True)
        else:
            raise AssertionError('Required argument not set - cv2_detector.')

        self.camera = camera
        self.on_motion_callback = on_motion
        self.debug = debug
        self.last_no_motion = None
        self.last_motion = None
        self.consequent_motion_frames = 0
        self.last_frame = None
        if 'mask' in config['motion']:
            self.mask = cv2.imread(config['motion']['mask'])
            self.mask = cv2.cvtColor(self.mask, cv2.COLOR_BGR2GRAY)
        else:
            self.mask = None
        self.history = []

    def validate_image(self, img):
        # Check if the image is defective. We get such images where a given line is repeated till
        # the end of the image. This triggers false alarm. So we compare the last two lines of the
        # array and if they are the same - this is defective image.
        height = img.shape[0]
        result = not (img[height-2] == img[height-3]).all()
        if not result:
            log('Detected defective image.')
        return result

    def check(self):
        """
        Check if moiton is detected. If so - calls the on_motion callback.
        :return: True iff motion is detected, False otherwise.
        """
        full_frame = self.camera.snapshot(retries=config['motion']['camera_retry_count'])

        if full_frame is None:
            # Failed to get snapshot...
            return False

        if not self.validate_image(full_frame):
            return False

        # B&W frame will be used for motion detection
        frame = cv2.cvtColor(full_frame, cv2.COLOR_BGR2GRAY)

        # apply the mask for motion detection
        if self.mask is not None:
            frame = cv2.bitwise_and(frame, self.mask)

        motion_mask = self.detector.apply(frame)

        # erode the motion detection mask in order to filter out the noise
        erode_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (6, 6))
        motion_mask = cv2.erode(motion_mask, erode_kernel, iterations=1)

        x, y, w, h = cv2.boundingRect(motion_mask)

        motion_detected = w >= self.MIN_MOTION_SIZE[0] or h >= self.MIN_MOTION_SIZE[1]

        if motion_detected:
            self.last_motion = datetime.now()
            self.consequent_motion_frames += 1
        else:
            self.last_no_motion = datetime.now()
            self.consequent_motion_frames = 0

        if len(self.history) < self.HISTORY_SIZE:
            self.history.append(motion_detected)
        else:
            self.history[0:self.HISTORY_SIZE-1] = self.history[1:self.HISTORY_SIZE]
            self.history[self.HISTORY_SIZE-1] = motion_detected

        data = {'motion_length': self.consequent_motion_frames,
                'motion_history': self.history,
                'motion': motion_detected,
                'motion_x': x,
                'motion_y': y,
                'motion_w': w,
                'motion_h': h}
        self.share_state(data)

        if not motion_detected:
            self.last_frame = full_frame
            return False

        motion_frame = numpy.copy(full_frame)

        # create rectangle around the detected motion
        cv2.rectangle(motion_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if self.debug:
            # add the motion detection mask
            motion_mask = cv2.resize(motion_mask, (0, 0), fx=1/self.DEBUG_FRAME_SCALE, fy=1/self.DEBUG_FRAME_SCALE)
            motion_frame[((self.DEBUG_FRAME_SCALE-1) * self.IMAGE_SIZE[1] / self.DEBUG_FRAME_SCALE):self.IMAGE_SIZE[1],
                         ((self.DEBUG_FRAME_SCALE-1) * self.IMAGE_SIZE[0] / self.DEBUG_FRAME_SCALE):self.IMAGE_SIZE[0]] =\
                cv2.cvtColor(motion_mask, cv2.COLOR_GRAY2RGB)

        self.on_motion_callback(motion_frame=motion_frame,
                                snapshot=full_frame,
                                prev_snapshot=self.last_frame,
                                last_motion=self.last_motion,
                                last_no_motion=self.last_no_motion,
                                motion_length=self.consequent_motion_frames)

        self.last_frame = full_frame
        return True

    def run(self):
        """Start the motion detection loop."""

        interval = int(config['motion']['interval'])

        while True:
            last_snapshot = datetime.now()
            try:
                motion = self.check()
            except Exception as e:
                log('Got exception:\n %s' % repr(e))
                motion = None

            if (datetime.now() - last_snapshot).total_seconds() < interval:
                sleep(interval - (datetime.now() - last_snapshot).total_seconds())
            if self.debug:
                log('Frame processed, motion: %s' % ('\033[92mTrue\033[0m' if motion else 'False'))

    @classmethod
    def share_state(cls, data):
        with open(config['camera_state_file'], 'w') as outfile:
            json.dump(data, outfile)

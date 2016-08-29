from lib import config
from lib.quicklock import lock
from sharp_eye.action import on_motion
from sharp_eye.cam import Camera
from sharp_eye.detector import MotionDetector


if __name__ == '__main__':
    lock()
    cam = Camera(file=config['motion']['snapshot'])
    detector = MotionDetector(camera=cam, on_motion=on_motion, debug=True)
    detector.run()

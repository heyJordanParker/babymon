from StringIO import StringIO
import cv2

from lib import config
from lib.tools import send_email


def on_motion(motion_frame, snapshot, prev_snapshot, last_motion, last_no_motion, motion_length):
    """
    Callback invoked when a motion is detected.

    :param motion_frame: the motion frame, 1/2 size of the snapshot with motion details
    :param snapshot: full size snapshot from the camera
    :param last_motion: datetime for the last snapshot with motion
    :param last_no_motion: datetime for the last snapshot without motion
    :param motion_length: count of subsequent motion snapshots
    """
    # if last_no_motion and motion_length == 1:
    #     attachment = {
    #         'data': StringIO(cv2.imencode('.jpg', snapshot)[1].tostring()),
    #         'name': 'snapshot.jpg'}
    #     send_email('Got motion!', 'Got motion on %s' % config['identifier'], [attachment])

    # if last_no_motion and motion_length == 1:
    #     attachment = {
    #         'data': StringIO(cv2.imencode('.jpg', motion_frame)[1].tostring()),
    #         'name': 'motion.jpg'}
    #     attachment2 = {
    #         'data': StringIO(cv2.imencode('.jpg', snapshot)[1].tostring()),
    #         'name': 'snapshot.jpg'}
    #     attachment3 = {
    #         'data': StringIO(cv2.imencode('.jpg', prev_snapshot)[1].tostring()),
    #         'name': 'prev_snapshot.jpg'}
    #
    #     send_email('Got motion!', 'Got motion on baby monitor', [attachment, attachment2, attachment3])

    pass
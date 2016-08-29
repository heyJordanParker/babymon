import cv2


class Camera(object):
    """
    Dummy camera that read the image from file.
    """

    def __init__(self, file):
        """
        Initialize. Do nothing as the stupid mofos haven't created good picamera module.
        """
        self.file = file
        pass

    def snapshot(self, retries=0):
        """
        Get snapshot from the camera.
        :param retries: how many retries to be done for getting the snapshot
        :return: numpy array
        """
        frame = None
        while frame is None and retries >= 0:
            retries -= 1
            try:
                return cv2.imread(self.file)
            except:
                # raise the exception only if we won't retry anymore
                if retries < 0:
                    raise
                else:
                    pass

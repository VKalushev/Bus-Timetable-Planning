import cv2 as cv

from picamera.array import PiRGBArray
from picamera import PiCamera
import time


class Capture:
    def __init__(self):
        # Init PiCamera.
        self._camera = PiCamera()
        self._camera.resolution = (640, 480)

        # Allow the camera time to boot
        time.sleep(1)

        # Create a raw capture for opencv
        self._rawCapture = PiRGBArray(self._camera, size = (640, 480))
        self._rawCapture.truncate(0)

        self.last_frame = None

    # Get an image of the next frame from the capture feed and return it
    def read(self):
        # Capture from the camera using the video port for speed
        self._camera.capture(self._rawCapture, format="bgr", use_video_port=True)
        frame_image = self._rawCapture.array

        # Clear the buffer for next capture
        self._rawCapture.truncate(0)
            
        # Flip the image vertically
        frame_image = cv.flip(frame_image, 0)

        # Store the last frame.
        self.last_frame = frame_image
        return frame_image

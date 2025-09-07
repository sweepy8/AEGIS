# Raspberry Pi Camera Module v2 program
# AEGIS Senior Design, Created on ../../25

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, Quality
from picamera2.outputs import PyavOutput
from time import sleep

import os
os.environ["LIBCAMERA_LOG_LEVELS"] = "2"    # Prevents console print clutter

from utils.file_utils import get_timestamped_filename

class Camera(Picamera2):
    """
    An extension of the Picamera2 class that includes AEGIS-specific fields and
    methods. For info about Picamera2, visit 
    'datasheets.raspberrypi.com/camera/picamera2-manual.pdf'

    Attributes:
        config (dict): Holds video configuration information.
        video_quality: The quality with which to encode the video stream.
        connected (bool): Whether or not the camera is connected to the system.
        recording (bool): Whether or not the camera is recording.
    """

    def __init__(self) -> None:
        try:
            super(Camera, self).__init__()
            self.connected = True
            self.config = self.create_video_configuration(
                main=  {'format':'XRGB8888'},
                lores= {'format':'RGB888'}
            )
        except:
            print("[ERR] camera.py: No camera detected!")
            self.connected = False

        self.video_quality = Quality.VERY_HIGH
        self.encoder = H264Encoder(repeat=True)
        self.recording = False

    def my_start_recording(self) -> str | None:
        """
        Wrapper around the picamera2 start method. Begins recording video to a
        timestamped file.

        Returns:
            filename (str): The timestamped filename of the video being recorded.
        """
        if self.recording == False:
            filename: str = get_timestamped_filename(
                save_path='data/videos', prefix='video', ext='.mp4')
            self.start_encoder(
                encoder=self.encoder,
                output=PyavOutput(output_name=filename),
                quality=self.video_quality
            )
            print("[RUN] camera.py: Began hi-res encoder...")
            self.start()
            print(f"[RUN] camera.py: Began recording to {filename}...")
            self.recording = True
            return filename
        else:
            print("[ERR] camera.py: Camera is already recording!")
            return None
    
    def my_stop_recording(self) -> None:
        """
        PLACEHOLDER, TO BE FILLED IN LATER ***
        """
        if self.recording == True:
            print("[RUN] camera.py: Attempting to stop recording...")
            self.stop_encoder()
            print("[RUN] camera.py: Stopped hi-res encoder...")
            self.recording = False
        else:
            print("[RUN_ERROR] camera.py: Camera is not recording!")
#Endclass

def record_test(seconds : int) -> None:
    """
    Simple test to record and save a video with a timestamped filename.

    Args:
        seconds (int): The number of seconds to record a test video for.
    """

    UGV_Cam = Camera()
    if (UGV_Cam is None):
        print("[ERR] camera.py: Can't run a camera test without a camera!")
        return
    
    UGV_Cam.my_start_recording()
    sleep(seconds)
    UGV_Cam.my_stop_recording()

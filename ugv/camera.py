# Raspberry Pi Camera Module v2 program
# AEGIS Senior Design, Created on ../../25

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, Quality
from picamera2.outputs import PyavOutput
from time import sleep
from cv2 import imencode

import os
os.environ["LIBCAMERA_LOG_LEVELS"] = "2"

from utils.file_utils import get_timestamped_filename

class Camera(Picamera2):
    '''
    An extension of the Picamera2 class that includes AEGIS-specific fields and methods.\n
    For info about Picamera2, visit 'datasheets.raspberrypi.com/camera/picamera2-manual.pdf'
    '''

    def __init__(self) -> None:
        '''
        PLACEHOLDER, TO BE FILLED IN LATER ***
        '''
        super(Camera, self).__init__()

        self.config = self.create_video_configuration(
            main=  {'format':'XRGB8888'},
            lores= {'format':'RGB888'}
        )

        self.video_quality = Quality.VERY_HIGH
        self.stream_quality = Quality.VERY_LOW
        self.encoder = H264Encoder(repeat=True)
        self.connected = True
        self.recording = False
        self.streaming = False

    def generate_frames(self):
        '''
        PLACEHOLDER, TO BE FILLED IN LATER ***
        ### This function taken from Shilleh on youtube.com/watch?v=NOAY1aaVPAw
        ### To better understand, look into generator functions and iterators
        '''
        while True:
            frame = self.capture_array("lores")
            success, buffer = imencode(ext='.jpg', img=frame)
            frame = buffer.tobytes()
            if (success):
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


    def my_start_recording(self) -> str | None:
        '''
        PLACEHOLDER, TO BE FILLED IN LATER ***
        '''
        if self.recording == False:
            filename = get_timestamped_filename('data/videos', 'video', '.mp4')
            self.start_encoder(
                encoder=self.encoder,
                output=PyavOutput(filename),
                quality=self.video_quality
            )
            print("[RUNTIME] camera.py: Began hi-res encoder...")
            self.start()
            print(f"[RUNTIME] camera.py: Began recording to {filename}...")
            self.recording = True
            return filename
        else:
            print("[RUN_ERROR] camera.py: Failed to start recording, are you already recording?")
            return None
    
    def my_stop_recording(self) -> None:
        '''
        PLACEHOLDER, TO BE FILLED IN LATER ***
        '''
        if self.recording == True:
            print("[RUNTIME] camera.py: Attempting to stop recording...")
            self.stop_encoder()
            print("[RUNTIME] camera.py: Stopped hi-res encoder...")
            self.recording = False
        else:
            print("[RUN_ERROR] camera.py: Failed to stop recording, are you sure you are recording?")
#Endclass

def record_test(seconds : int) -> None:
    '''
    Simple test to record and save a video with a timestamped filename.
    '''
    if (UGV_Cam is None):
        print("[ERROR] camera.py->record_test(): Can't perform test without a camera!")
        return
    
    filename = UGV_Cam.my_start_recording()
    for i in range(0, seconds):
        sleep(1)
    UGV_Cam.my_stop_recording()


# Global UGV camera object to be shared between other modules.
# Starts camera configured with 
# Additional cameras could be instantiated here and shared similarly.
try:
    UGV_Cam = Camera()
    UGV_Cam.start(UGV_Cam.config)
    print("[INIT] camera.py: UGV camera initialized successfully...")
except IndexError as e:
    print(f"[ERROR] camera.py: Camera not connected!")
    UGV_Cam = None


if __name__ == "__main__":
    record_test(30)
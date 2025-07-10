# Raspberry Pi Camera Module v2 program
# AEGIS Senior Design, Created on ../../25

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, Quality
from picamera2.outputs import PyavOutput, FileOutput
from time import sleep
from cv2 import imencode

import os
os.environ["LIBCAMERA_LOG_LEVELS"] = "2"

from utils.file_utils import get_timestamped_filename



'''
UPDATE THE ENCODER OUTPUTS! ONE FileOutput AND ONE PyavOutput, PIPE FILEOUTPUT
TO RPI_UART.PY and PIPE PyavOutput TO STREAM.PY

'''



# Wrapper around Picamera2 object
class Camera(Picamera2):
    '''
    An extension of the Picamera2 class that includes AEGIS-specific data fields and class methods.\n
    For information about Picamera2, visit 'datasheets.raspberrypi.com/camera/picamera2-manual.pdf'
    '''

    def __init__(self) -> None:
        '''
        PLACEHOLDER, TO BE FILLED IN LATER ***
        '''
        super(Camera, self).__init__()

        self.config = self.create_video_configuration(
            main={
                'format':'XRGB8888'
            },
            lores={
                'format':'XRGB8888'
            }
        )

        self.attrs = {
            'quality': Quality.VERY_HIGH,
            'encoder': H264Encoder(repeat=True),
            'connected': True,
            'recording': False,
            'streaming': False
        }


    # This function taken from Shilleh on youtube.com/watch?v=NOAY1aaVPAw
    # To better understand, look into generator functions and iterators
    def generate_frames(self):
        '''
        PLACEHOLDER, TO BE FILLED IN LATER ***
        '''
        while True:
            frame = self.capture_array()
            ret, buffer = imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


    def my_start_recording(self) -> str | None:
        '''
        PLACEHOLDER, TO BE FILLED IN LATER ***
        '''
        if self.attrs['recording'] == False:
            filename = get_timestamped_filename('data/videos', 'video', '.mp4')
            self.start_recording(
                encoder=self.attrs['encoder'],
                output=PyavOutput(filename),
                quality=self.attrs['quality']
            )
            self.attrs['recording'] = True
            return filename
        else:
            print("camera.py: Failed to start recording, are you already recording?")
            return None
    
    def my_stop_recording(self) -> None:
        '''
        PLACEHOLDER, TO BE FILLED IN LATER ***
        '''
        if self.attrs['recording'] == True:
            self.stop_recording()
            self.attrs['recording'] = False
        else:
            print("camera.py: Failed to stop recording, are you sure you are recording?")

# Global UGV camera object to be shared between other modules.
# Additional cameras could be instantiated here and shared similarly.
UGV_Cam = Camera()
UGV_Cam.start()

def record_test(seconds : int) -> None:
    '''
    Simple test to record and save a video with a timestamped filename.
    '''
    filename = UGV_Cam.my_start_recording()
    print(f"camera.py: Recording video to: '{filename}'...")
    sleep(seconds)
    UGV_Cam.my_stop_recording()
    print(f"camera.py: Saved video at:     '{filename}'.")

if __name__ == "__main__":
    record_test(30)
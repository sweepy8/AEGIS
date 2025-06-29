
from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder, Quality

from time import sleep
from cv2 import imencode

from utils.file_utils import get_timestamped_filename

# Wrapper around Picamera2 object
class Camera(Picamera2):

    def __init__(self, mode: str = 'preview') -> None:

        super(Camera, self).__init__()

        self.quality = Quality.VERY_HIGH
        self.encoder = H264Encoder()
        self.configure_mode(mode)


    def configure_mode(self, mode: str) -> None:
        if mode == 'video':
            self.configuration = self.create_video_configuration()
        elif mode == 'preview':
            self.configuration = self.create_preview_configuration(
                main={'format':'XRGB8888'}
            )

        self.configure(self.configuration)


    # This function taken from Shilleh on youtube.com/watch?v=NOAY1aaVPAw
    # To better understand, look into generator functions and iterators
    def generate_frames(self):
        while True:
            frame = self.capture_array()
            ret, buffer = imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


    def record_video(self, filename: str, seconds: int) -> int:
        self.configure_mode('video')
        self.start_recording(
            encoder=self.encoder, output=filename, quality=self.quality
        )
        sleep(seconds) # FIX THIS, maybe ASYNCIO or thread?
        self.stop_recording()
        print(f"{seconds} second video saved as {filename}!")




# END OF CAMERA CLASS ---------------------------------------------------------

def test_record(cam: Camera, len_seconds: int) -> None:
    filename = get_timestamped_filename('data/videos', 'video', '.h264')
    print(f"Beginning {duration_seconds} second recording...")
    cam.record_video(filename, len_seconds)
    print(f"Recording complete! Stored at {filename}.")


if __name__ == "__main__":
    duration_seconds = 10
    cam = Camera()
    test_record(cam, duration_seconds)


'''
TRIP_RECORDER.PY SHOULD BE INTEGRATED INTO THE CAMERA FILE

# Testing file
# Records video and stores them on the hard drive

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, Quality
from time import sleep

def init_camera() -> Picamera2:
    cam = Picamera2()
    cam.configure(cam.create_video_configuration())
    return cam

def record_video(cam : Picamera2, file_name : str, seconds : int) -> None:
    cam.start_recording(
        encoder=H264Encoder(),
        output=file_name,
        quality=Quality.VERY_HIGH
    )
    sleep(seconds)
    cam.stop_recording()

'''
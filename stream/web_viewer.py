# Unified web view program
# AEGIS Senior Design, Created on 6/9/25

from flask import Flask, Response, render_template, send_file
from ugv.camera import UGV_Cam
from utils.stream_utils import create_visualizer_fig

from time import sleep
from multiprocessing import Process

# ROUTES ----------------------------------------------------------------------

app = Flask(__name__)

@app.route('/video_feed')   # Embedded in root page
def video_feed() -> Response:
    '''
    *************************************.
    '''
    if UGV_Cam.connected:
        return Response(
            UGV_Cam.generate_frames(), 
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
    else:
        return send_file(
            path_or_file='static/images/no_video.gif',
            mimetype='image/gif'
        )

@app.route('/')
def show_main_page() -> str:
    '''
    **********************************.
    '''
    return render_template('main.html')

@app.route('/visualizer')   # Embedded in root page
def visualizer() -> Response:
    '''
    **********************************.
    '''
    return Response(
        create_visualizer_fig(),
        mimetype='image/png'
    )

# # Prevent all caching
# @app.after_request
# def add_http_headers(response : Response) -> Response:
#     '''
#     **********************************.
#     '''
#     response.headers['cache-control'] = 'no-store'
#     return response

def test_rec():
    filename = UGV_Cam.my_start_recording()

    for x in range(1, 21):
        sleep(1)
        print(x, " seconds into 10s video...")
    UGV_Cam.my_stop_recording()
    print(f"multi_cam_test.py: Saved video at:     '{filename}'.")

    print("test_rec all done!")


def run_stream() -> None:
    '''
    **********************************.
    '''

    app.run(
        host='10.40.78.112',
        port=5000,
        use_reloader=False
    )

if __name__ == "__main__":
    run_stream()
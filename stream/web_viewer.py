# Unified web view program
# AEGIS Senior Design, Created on 6/9/25

from picamera2  import Picamera2
from flask      import Flask, Response, render_template
from cv2        import imencode
from matplotlib import figure
from io         import BytesIO
from base64     import b64encode


# This function taken from Shilleh on youtube.com/watch?v=NOAY1aaVPAw
# To better understand, look into generator functions and iterators
def generate_frames():
    while True:
        frame = camera.capture_array()
        ret, buffer = imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def create_visualizer_fig():
    fig = figure.Figure()
    axis = fig.add_subplot(1,1,1)

    x_vals = range(100)
    y_vals = [x ** 2 for x in x_vals]
    axis.plot(x_vals, y_vals, color="white")

    fig.patch.set_facecolor('black')
    axis.set_facecolor('black')
    for spine in axis.spines.values(): spine.set_edgecolor('white')
    axis.set_title("LiDAR Visualizer (Placeholder)", color='w')
    axis.set_xlabel("X", color='white')
    axis.set_ylabel("Y", color='white')
    axis.tick_params(colors='w', which='both')
    fig.tight_layout()

    output_png = BytesIO()
    fig.savefig(output_png, format='png')
    encoded_data = b64encode(output_png.getbuffer()).decode('ascii')

    return output_png.getvalue()


def init_telemetry_frame():
    pass

def update_telemetry_frame():
    pass

# ROUTES ----------------------------------------------------------------------

app = Flask(__name__)

camera = Picamera2()
camera.configure(
    camera.create_preview_configuration(
        main={ "format": 'XRGB8888'} # Comment this and look at the feed :)
    )
)
camera.start()

# Stop caching 
@app.after_request
def add_http_headers(response : Response):
    response.headers['cache-control'] = 'no-store'
    return response

@app.route('/')
def show_main_page():
    return render_template('main.html')

@app.route('/video_feed')   # Embedded in root page
def video_feed():
    return Response(
        generate_frames(), 
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/visualizer')   # Embedded in root page
def visualizer():
    return Response(
        create_visualizer_fig(),
        mimetype='image/png'
    )

app.run(
    host='0.0.0.0',         # 0.0.0.0 runs on all addresses
    port=5000
)
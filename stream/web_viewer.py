# Unified web view program
# AEGIS Senior Design, Created on 6/9/25

from flask      import Flask, Response, render_template, send_file
from matplotlib import figure
from io         import BytesIO

from ugv.camera import Camera


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

    return output_png.getvalue()


# ROUTES ----------------------------------------------------------------------

app = Flask(__name__)

try:
    camera = Camera()
    camera.start()
except ValueError:
    camera_connected = False
else:
    camera_connected = True


@app.route('/video_feed')   # Embedded in root page
def video_feed():
    if camera_connected:
        return Response(
            camera.generate_frames(), 
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
    else:
        return send_file(path_or_file='static/images/no_video.gif', mimetype='image/gif')


# # Prevent all caching 
# @app.after_request
# def add_http_headers(response : Response):
#     response.headers['cache-control'] = 'no-store'
#     return response


@app.route('/')
def show_main_page():
    return render_template('main.html')

@app.route('/visualizer')   # Embedded in root page
def visualizer():
    return Response(
        create_visualizer_fig(),
        mimetype='image/png'
    )

def run_stream():
    app.run(
        host='0.0.0.0',         # 0.0.0.0 runs on all addresses
        port=5000
)
    
if __name__ == "__main__":
    run_stream()
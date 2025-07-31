# Unified web view program
# AEGIS Senior Design, Created on 6/9/25

from flask import Flask, Response, render_template, send_file, jsonify
import os # os allows directory navigation
# from ugv.camera import UGV_Cam
# from utils.stream_utils import create_visualizer_fig

from time import sleep
# from multiprocessing import Process

# ROUTES ----------------------------------------------------------------------

app = Flask(__name__) # Creates Flask app instance

# Sets absolute directory path because python is stupid
btn_folder = os.path.join(app.static_folder, 'trips') 
# Directory to be monitored for buttons

# app routes for each html page
@app.route('/') # inside '' is the link for href to link page
def main_page():
    return render_template('main.html') # Loads main html page
@app.route('/trip_viewer')
def trip_viewer():
    return render_template('trip_viewer.html') # loads trip viewer
@app.route('/trip_raw_data')
def trip_raw_data():
    return render_template('trip_raw_data.html') # loads trip raw data
@app.route('/about')
def about():
    return render_template('about.html') # loads about page
@app.route('/admin')
def admin():
    return render_template('admin.html') # loads admin page

@app.route('/trips')
def get_trips():
    try:
        # gets list of all files and folders in btn_folder path
        entries = os.listdir(btn_folder)

        # removes files from array and leaves on folders
        folders = [f for f in entries if os.path.isdir(os.path.join(btn_folder, f))]
        # path.isdir returns folders only, not files
        return jsonify(folders) # convertes list to JSON and returns
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500 

# Python Functions ----------------------------------------------------------

# def run_stream() -> None:
#     # Runs the website and its functions at the bellow ip address
#     app.run(
#         host='10.40.119.174',
#         port=5000,
#         use_reloader=False
#     )

if __name__ == "__main__":
    # run_stream() # Start Server
    # os.makedirs(btn_folder, exist_ok=True)
    app.run(debug=True)
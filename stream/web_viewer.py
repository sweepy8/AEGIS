# Unified web viewer backend
# AEGIS Senior Design, Created on 6/9/25

from flask import Flask, render_template, jsonify, request
import os # os allows directory navigation

# ROUTES ----------------------------------------------------------------------

app = Flask(__name__) # Creates Flask app instance

# Directory to be monitored for buttons
# Sets absolute directory path because python is stupid
btn_folder = os.path.join(app.static_folder, 'trips')       #type: ignore

# Routes for each of the HTML pages
@app.route('/') # inside '' is the link for href to link page
def main_page():
    return render_template('home.html') # Loads home html page
@app.route('/telemetry')
def telemetry_page():
    return render_template('telemetry.html') # Loads telemetry html page
@app.route('/admin')
def admin_page():
    return render_template('admin.html') # Loads admin html page
@app.route('/about')
def about_page():
    return render_template('about.html') # Loads about html page

# Routes for backend file retrieval, should not be accessed as webpages
@app.route('/getTripFolders')
def get_trip_folders():
    """
    Retrieves all trip folders and sends them to frontend as JSON object.
    """
    try:
        all = os.listdir(btn_folder)
        folders = [f for f in all if os.path.isdir(os.path.join(btn_folder, f))]
        return jsonify(folders)
    except Exception as e:
        return jsonify({"error": str(e)}), 500 
    
@app.route('/getVideoFiles')
def get_video_files():
    """
    Retrieves all video files and sends them to the frontend as JSON object.
    """
    trip = request.args.get('trip','')
    abs_path = os.path.abspath(os.path.join(btn_folder, trip))

    video_files = [f for f in os.listdir(abs_path)
        if os.path.isfile(os.path.join(abs_path, f)) and f.endswith('.mp4')]
    
    return jsonify(video_files)

@app.route('/getScanFiles')
def get_scan_files():
    """
    Retrieves all scan files and sends them to frontend as JSON object.
    """
    trip = request.args.get('trip', '')  # Get trip name from fetch query
    abs_path = os.path.abspath(os.path.join(btn_folder, trip))
    
    scan_files = [f for f in os.listdir(abs_path)
        if os.path.isfile(os.path.join(abs_path, f)) and f.endswith('.txt')]

    return jsonify(scan_files)

@app.route('/getTelemetryFile')
def get_telemetry_file():
    trip = request.args.get('trip', '')
    abs_path = os.path.abspath(os.path.join(btn_folder, trip))

    tel_files = [f for f in os.listdir(abs_path)
        if os.path.isfile(os.path.join(abs_path, f)) and f.endswith('.json')]

    return jsonify(tel_files)   # Should always be exactly one JSON file


if __name__ == "__main__":
    # os.makedirs(btn_folder, exist_ok=True)
    app.run(debug=True)
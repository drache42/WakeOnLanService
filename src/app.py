from flask import Flask, jsonify, render_template, redirect, url_for
import requests
from wakeonlan import send_magic_packet
import time
import os

app = Flask(__name__)

# Check if the app is in debug mode based on an environment variable
DEBUG_MODE = os.getenv("FLASK_DEBUG", "false").lower() == "true"
print(f"DEBUG_MODE: {DEBUG_MODE}")  # Log the debug mode status.
print(f"App debug mode is {'on' if app.debug else 'off'}")

global attempts
attempts = 0

@app.route("/check_url")
def check_url_status():
    url = "http://192.168.1.109:3000"
    global attempts
    attempts += 1
    
    if not DEBUG_MODE:
        send_magic_packet("18-C0-4D-07-5B-2D")
        
    
    if(app.debug):
        if(attempts >= 5):
            status = "available"
        else:
            status = "debug"
    elif check_url(url):
        status = "available"
    elif(attempts >= 10):
        status = "error"
    else:
        status = "unavailable"
    
    return jsonify(
        {
            "status": status,
            "attempts": attempts,
            "url": url
        })

def check_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
    except requests.RequestException as e:
        print(f"Request failed: {e}")
    return False

@app.route("/")
def index():
    global attempts
    url = "http://192.168.1.109:3000"
    attempts = 0

    if(DEBUG_MODE):
        return render_template("loading.html", attempts=attempts)
        
    if check_url(url) and not DEBUG_MODE:
        return redirect(url)
    else:
        if not DEBUG_MODE:
            send_magic_packet("18-C0-4D-07-5B-2D")

    return render_template("loading.html", attempts=attempts)

@app.route("/debug-status")
def debug_status():
    return f"App debug mode is {'on' if app.debug else 'off'}, Environment variable debug mode is {'on' if DEBUG_MODE else 'off'}"

if __name__ == "__main__":
    app.run(debug=DEBUG_MODE)
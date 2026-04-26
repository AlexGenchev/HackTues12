import os, subprocess, threading, requests
from datetime import datetime
from signal import pause
from dotenv import load_dotenv
from gpiozero import Button

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/complaints/upload")
RECORDINGS_DIR = os.path.expanduser("~/smart_box_recordings")
os.makedirs(RECORDINGS_DIR, exist_ok=True)

_lock = threading.Lock()
_recording_process = None
_current_file = None

def start_recording():
    global _recording_process, _current_file
    filename = os.path.join(RECORDINGS_DIR, f"rec_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav")
    
    cmd = ["arecord", "-f", "cd", "-t", "wav", filename]
    audio_device = os.getenv("AUDIO_DEVICE")
    if audio_device:
        cmd = ["arecord", "-D", audio_device, "-f", "cd", "-t", "wav", filename]
        
    _recording_process = subprocess.Popen(cmd)
    _current_file = filename

def stop_and_upload():
    global _recording_process, _current_file
    if _recording_process:
        _recording_process.terminate()
        _recording_process.wait()
        threading.Thread(target=upload, args=(_current_file,), daemon=True).start()
        _recording_process, _current_file = None, None

def upload(filepath):
    try:
        with open(filepath, "rb") as f:
            requests.post(BACKEND_URL, files={"audio_file": f}, timeout=120)
    except Exception as e:
        print(f"Error: {e}")

def on_pressed():
    with _lock:
        if not _recording_process: start_recording()

def on_released():
    with _lock: stop_and_upload()

if __name__ == "__main__":
    btn = Button(23, pull_up=True, bounce_time=0.3)
    btn.when_pressed, btn.when_released = on_pressed, on_released
    pause()


from gpiozero import Button
from signal import pause
import subprocess
from datetime import datetime
import os
import requests
import json

os.makedirs("/home/alexgenchev1/Music", exist_ok=True)

button = Button(23, pull_up=True, bounce_time=0.3)
recording = None
current_filename = None

BACKEND_URL = "http://10.232.188.196:8000/complaints/upload"


def send_audio_to_backend(filepath):
    try:
        print(f"--- SENDING FILE TO BACKEND: {filepath} ---")

        with open(filepath, "rb") as f:
            files = {
                "audio_file": (os.path.basename(filepath), f, "audio/wav")
            }

            response = requests.post(BACKEND_URL, files=files)
  
        print("=== BACKEND RESPONSE ===")
        print("Status code:", response.status_code)

        try:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))

            if "recognised_text" in data:
                print("\n=== RECOGNISED TEXT ===")
                print(data["recognised_text"])

        except Exception:
            print(response.text)

    except Exception as e:
        print("Error sending audio:", e)


def toggle_recording():
    global recording, current_filename

    if recording is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        current_filename = f"/home/alexgenchev1/Music/rec_{timestamp}.wav"

        print(f"--- STARTING RECORDING: {current_filename} ---")
        recording = subprocess.Popen([
            "arecord",
            "-D", "plughw:2,0",
            "-f", "cd",
            "-t", "wav",
            current_filename
        ])

    else:
        print("--- STOPPING RECORDING ---")
        recording.terminate()
        recording.wait()
        recording = None

        send_audio_to_backend(current_filename)


button.when_pressed = toggle_recording

print("Ready! Press the button to start/stop recording.")
pause()
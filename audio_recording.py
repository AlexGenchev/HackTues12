from gpiozero import Button
from signal import pause
import subprocess
from datetime import datetime
import os

os.makedirs("/home/alexgenchev1/Music", exist_ok=True)

button = Button(23, pull_up=True)
recording = None 

def toggle_recording():
    global recording
    
    if recording is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/home/alexgenchev1/Music/rec_{timestamp}.wav"
        
        print(f"--- STARTING RECORDING: {filename} ---")
        recording = subprocess.Popen([
            "arecord",
            "-D", "plughw:2,0",
            "-f", "cd",
            "-t", "wav",
            filename
        ])
    
    else:
        print("--- STOPPING RECORDING ---")
        recording.terminate()
        recording.wait() 
        recording = None

button.when_pressed = toggle_recording

print("Ready! Press the button to start/stop recording.")
pause()
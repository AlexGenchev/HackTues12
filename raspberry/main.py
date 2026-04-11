# raspberry/main.py
# Raspberry Pi entry point for the Smart Box citizen complaint device.
#
# Behaviour:
#   - Waits for a button press on GPIO pin 23.
#   - On PRESS  → starts recording audio via arecord.
#   - On RELEASE → stops recording and uploads the WAV file to the backend.
#
# Configuration is loaded entirely from a .env file in this directory.
# Copy .env.example to .env and fill in BACKEND_URL before running.

import json
import logging
import os
import subprocess
import threading
from datetime import datetime
from signal import pause

import requests
from dotenv import load_dotenv
from gpiozero import Button

# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

BACKEND_URL: str = os.getenv(
    "BACKEND_URL",
    "http://localhost:8000/complaints/upload",
)

# Directory where recordings are saved locally on the Pi.
RECORDINGS_DIR = os.path.join(os.path.expanduser("~"), "smart_box_recordings")
os.makedirs(RECORDINGS_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Recording state — protected by a Lock to avoid race conditions.
# ---------------------------------------------------------------------------

_lock = threading.Lock()
_recording_process: subprocess.Popen | None = None
_current_filename: str | None = None


# ---------------------------------------------------------------------------
# ALSA / arecord helpers
# ---------------------------------------------------------------------------

def _start_recording() -> None:
    """Start capturing audio from the USB microphone using arecord."""
    global _recording_process, _current_filename

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(RECORDINGS_DIR, f"rec_{timestamp}.wav")

    logger.info("--- STARTING RECORDING: %s ---", filename)
    process = subprocess.Popen(
        [
            "arecord",
            "-D", "plughw:2,0",   # Adjust device index if required on your Pi.
            "-f", "cd",           # 16-bit stereo 44100 Hz
            "-t", "wav",
            filename,
        ]
    )
    _recording_process = process
    _current_filename = filename


def _stop_recording() -> str | None:
    """Stop the running arecord process and return the filename."""
    global _recording_process, _current_filename

    if _recording_process is None:
        return None

    logger.info("--- STOPPING RECORDING ---")
    _recording_process.terminate()
    _recording_process.wait()

    filename = _current_filename
    _recording_process = None
    _current_filename = None
    return filename


# ---------------------------------------------------------------------------
# Backend upload
# ---------------------------------------------------------------------------

def _send_audio_to_backend(filepath: str) -> None:
    """Upload a WAV file to the backend and log the transcribed response."""
    logger.info("--- SENDING FILE TO BACKEND: %s ---", filepath)
    try:
        with open(filepath, "rb") as f:
            files = {"audio_file": (os.path.basename(filepath), f, "audio/wav")}
            response = requests.post(BACKEND_URL, files=files, timeout=120)

        logger.info("Backend response status: %d", response.status_code)

        try:
            data = response.json()
            logger.info("Response JSON:\n%s", json.dumps(data, indent=2, ensure_ascii=False))

            if data.get("status") == "success":
                logger.info(
                    "=== TRANSCRIBED TEXT ===\n%s",
                    data.get("transcribed_text", "(empty)"),
                )
                logger.info(
                    "Category: %s | Urgency: %s | Municipality: %s",
                    data.get("category"),
                    data.get("urgency"),
                    data.get("municipality"),
                )
            else:
                logger.error(
                    "Pipeline step failed: %s — %s",
                    data.get("step_failed"),
                    data.get("detail"),
                )
        except ValueError:
            logger.error("Backend returned non-JSON response: %s", response.text[:500])

    except requests.exceptions.ConnectionError:
        logger.error("Cannot reach backend at %s — is the server running?", BACKEND_URL)
    except requests.exceptions.Timeout:
        logger.error("Backend request timed out after 120 seconds.")
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Unexpected error sending audio: %s", exc)


def _upload_in_thread(filepath: str) -> None:
    """Run backend upload in a daemon thread so the button stays responsive."""
    thread = threading.Thread(
        target=_send_audio_to_backend, args=(filepath,), daemon=True
    )
    thread.start()


# ---------------------------------------------------------------------------
# Button event handlers
# ---------------------------------------------------------------------------

def on_button_pressed() -> None:
    """Handle GPIO button press — start a new recording if not already active."""
    with _lock:
        if _recording_process is not None:
            logger.warning("Button pressed but recording already active — ignoring.")
            return
        _start_recording()


def on_button_released() -> None:
    """Handle GPIO button release — stop recording and upload to backend."""
    with _lock:
        filepath = _stop_recording()

    if filepath is None:
        logger.warning("Button released but no active recording — ignoring.")
        return

    logger.info("Recording saved to: %s", filepath)
    _upload_in_thread(filepath)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    button = Button(23, pull_up=True, bounce_time=0.3)
    button.when_pressed = on_button_pressed
    button.when_released = on_button_released

    logger.info("Smart Box is ready. Press the button to record a complaint.")
    logger.info("Backend URL: %s", BACKEND_URL)
    logger.info("Recordings directory: %s", RECORDINGS_DIR)
    logger.info("Press Ctrl+C to exit.")
    pause()

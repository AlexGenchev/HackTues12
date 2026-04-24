"""
simulate_device.py
------------------
A utility script to simulate the Raspberry Pi's behaviour locally.
This script allows you to test the FastAPI backend by uploading an existing .wav file 
directly, bypassing the need for physical hardware.

Usage:
  python tests/simulate_device.py path/to/your/audio.wav

Optional arguments:
  --url URL     The backend upload endpoint (default: http://localhost:8000/complaints/upload)
"""

import os
import argparse
import requests
import sys

DEFAULT_BACKEND_URL = "http://localhost:8000/complaints/upload"

def main():
    parser = argparse.ArgumentParser(description="Simulate Raspberry Pi audio upload.")
    parser.add_argument("audio_file", help="Path to the audio file (e.g., .wav) to upload.")
    parser.add_argument("--url", default=DEFAULT_BACKEND_URL, help=f"Backend API URL (default: {DEFAULT_BACKEND_URL})")
    
    args = parser.parse_args()

    if not os.path.exists(args.audio_file):
        print(f"Error: File '{args.audio_file}' not found.")
        sys.exit(1)

    print(f"Uploading '{args.audio_file}' to Backend API at {args.url} ...\n")
    
    try:
        with open(args.audio_file, "rb") as f:
            # We must use "audio_file" as the key to match FastAPI's parameter name
            files = {"audio_file": (os.path.basename(args.audio_file), f, "audio/wav")}
            
            # Timeout set to 120s, matching the Raspberry Pi script
            response = requests.post(args.url, files=files, timeout=120)
            
        print(f"HTTP Status Code: {response.status_code}")
        
        try:
            # Try parsing response as JSON for prettier output
            data = response.json()
            import json
            print("\nResponse Data:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except ValueError:
            print("\nResponse Data (Raw):")
            print(response.text)
            
        if response.status_code != 200:
            print("\nWarning: The request wasn't totally successful.")
            sys.exit(1)
            
    except requests.exceptions.ConnectionError:
        print(f"Error: Failed to connect to {args.url}.")
        print("Please ensure the backend server is running (e.g., via 'uvicorn backend.main:app --reload').")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print(f"Error: Request to {args.url} timed out (120s limit).")
        print("The AI pipeline might be taking too long or the backend is hanging.")
        sys.exit(1)

if __name__ == "__main__":
    main()

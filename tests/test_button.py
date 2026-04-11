# tests/test_button.py
#
# Hardware sanity check — NOT production code.
# Run this on the Raspberry Pi to verify that GPIO pin 23 is wired
# correctly and that gpiozero can detect button press/release events.
# Usage: python tests/test_button.py
# Press Ctrl+C to exit.

from gpiozero import Button
from signal import pause

button = Button(23, pull_up=True)

button.when_pressed = lambda: print("Button PRESSED — GPIO pin 23 detected.")
button.when_released = lambda: print("Button RELEASED — GPIO pin 23 detected.")

print("Hardware test running. Press the button to verify GPIO pin 23.")
print("Press Ctrl+C to exit.")
pause()

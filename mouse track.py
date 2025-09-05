import pyautogui
import time


print("Tracking mouse position. Press Ctrl+C to stop.\n")

try:
    while True:
        x, y = pyautogui.position()
        # Overwrite the same line
        print(f"\rMouse position: ({x:4}, {y:4})", end="")
        time.sleep(0.01)  # update every 0.1 second
except KeyboardInterrupt:
    print("\nStopped.")
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from pynput import mouse
import pyautogui
import pygetwindow as gw
import math
import os
import time

# Start Selenium
service = Service(r"C:\Users\Nathan\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=service)

# Path to your saved HTML file
while True:
    choice = input("Do you want to test on a HTML page or a webpage (html/web)?")
    if choice == "html":
        file_path = os.path.abspath("htmlTEST.html")
        driver.get("file://" + file_path)
        break
    elif choice == "web":
        driver.get("https://www.google.com/")
        break
    else:
        print("Please enter either html or web")

time.sleep(1)  # allow page to load

# --- Get Chrome window position & size ---
chrome_windows = [w for w in gw.getAllWindows() if "Chrome" in w.title]
if not chrome_windows:
    raise RuntimeError("No Chrome window found!")
win = chrome_windows[0]
window_left, window_top = win.left, win.top

# --- Collect button coordinates ---
buttons = driver.find_elements("tag name", "button")
button_centers = []
for btn in buttons:
    loc = btn.location
    size = btn.size
    center_x = window_left + loc["x"] + size["width"] // 2
    center_y = window_top + loc["y"] + size["height"] // 2
    button_centers.append((center_x, center_y))
    print(f"Button '{btn.text}' at {center_x},{center_y}")

# Settings
slow_radius = int(input("What do you want the pull radius (px) to be? (100px is recommended)"))   # slowdown zone
print(f"The radius of the effect is {slow_radius}px")
max_lock_strength = float(input("How strong (0.1 - 1) do you want the pull to be? (0.8 is recommended)"))  # maximum pull force at button center
print(f"The maximum lock strength is {max_lock_strength}")

# Track last position
last_pos = pyautogui.position()

def on_move(x, y):
    global last_pos
    dx = x - last_pos[0]
    dy = y - last_pos[1]

    # Find nearest button
    nearest_btn = None
    nearest_dist = float("inf")
    for bx, by in button_centers:
        dist = math.hypot(x - bx, y - by)
        if dist < nearest_dist:
            nearest_dist = dist
            nearest_btn = (bx, by)

    if nearest_dist < slow_radius:
        bx, by = nearest_btn
        # Scale movement slowdown
        factor = nearest_dist / slow_radius
        dx *= factor
        dy *= factor

        # Magnetic pull scales as you get closer
        strength = (1 - factor) * max_lock_strength
        pull_x = (bx - x) * strength
        pull_y = (by - y) * strength

        new_x = int(last_pos[0] + dx + pull_x)
        new_y = int(last_pos[1] + dy + pull_y)

        pyautogui.moveTo(new_x, new_y)
        last_pos = (new_x, new_y)
    else:
        last_pos = (x, y)

# Start listener
with mouse.Listener(on_move=on_move) as listener:
    listener.join()

driver.quit()

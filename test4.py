import uiautomation as auto
import keyboard
import time
import threading
from uiautomation import UIAutomationInitializerInThread
import win32api
import math

# ======= CONFIGURATION =======
SNAP_RADIUS = 37       # How close the cursor must be to snap
REFRESH_RATE = 0.00001   # Seconds between snap checks
HOTKEY_SCAN = 'ctrl+alt+s'  # Toggle scanning
HOTKEY_SNAP = 'ctrl+alt+a'  # Toggle snapping

# ======= GLOBAL VARIABLES =======
clickable_controls = []   # List of (x,y) centers of clickable elements
running = False           # Whether scanning is active
snapping = True           # Whether snapping is active
scanner_thread = None     # Thread handle


# ======= SCANNER THREAD FUNCTION =======
def _run_scanner():
    global running, clickable_controls

    with UIAutomationInitializerInThread():
        print("\n[SCAN STARTED]")
        print("=" * 50)

        while running:
            clickable_controls = []

            try:
                hwnd = auto.GetForegroundWindow()
                if hwnd:
                    window = auto.ControlFromHandle(hwnd)

                    def find_clickables(control):
                        if not running:
                            return
                        if isinstance(control, (
                            auto.ButtonControl,
                            auto.HyperlinkControl,
                            auto.MenuItemControl,
                            auto.TabItemControl,
                            auto.CheckBoxControl,
                            auto.RadioButtonControl,
                        )):
                            rect = control.BoundingRectangle
                            if rect:
                                cx = (rect.left + rect.right) // 2
                                cy = (rect.top + rect.bottom) // 2
                                clickable_controls.append((cx, cy))
                                print(f"Name: {control.Name}, Class: {control.ClassName}, Pos: ({cx}, {cy})")

                        for child in control.GetChildren():
                            find_clickables(child)

                    find_clickables(window)

            except Exception as e:
                print("Scan error:", e)

            time.sleep(1)


# ======= HOTKEY HANDLERS =======
def toggle_scanning():
    global running, scanner_thread

    if not running:
        running = True
        scanner_thread = threading.Thread(target=_run_scanner, daemon=True)
        scanner_thread.start()
    else:
        running = False
        print("\n[SCAN STOPPED]")


def toggle_snapping():
    global snapping
    snapping = not snapping
    state = "ON" if snapping else "OFF"
    print(f"[SNAP] Snapping is now {state}")


# ======= SNAPPING THREAD =======
def monitor_and_snap():
    global snapping
    while True:
        if not snapping:
            time.sleep(REFRESH_RATE)
            continue

        try:
            mouse_x, mouse_y = win32api.GetCursorPos()

            for (cx, cy) in clickable_controls:
                dx = cx - mouse_x
                dy = cy - mouse_y
                distance = math.hypot(dx, dy)

                if distance < SNAP_RADIUS:
                    win32api.SetCursorPos((cx, cy))
                    break

        except Exception as e:
            print("Snap error:", e)

        time.sleep(REFRESH_RATE)


# ======= MAIN EXECUTION BLOCK =======
print("Script loaded.")
print(f"Press {HOTKEY_SCAN} to toggle scanning.")
print(f"Press {HOTKEY_SNAP} to toggle snapping.")

# Start snapping thread
snap_thread = threading.Thread(target=monitor_and_snap, daemon=True)
snap_thread.start()

# Register hotkeys
keyboard.add_hotkey(HOTKEY_SCAN, toggle_scanning)
keyboard.add_hotkey(HOTKEY_SNAP, toggle_snapping)

# Keep script alive
keyboard.wait()

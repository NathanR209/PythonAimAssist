import uiautomation as auto
import keyboard
import time
import threading
from uiautomation import UIAutomationInitializerInThread
import pyautogui
from pywinauto.application import Application
import win32api 
import math

# ======= CONFIGURATION =======
HOTKEY = 'ctrl+alt+s'  # Hotkey to toggle scanning

# ======= GLOBAL VARIABLES =======
clickable_controls = []
running = False          # Whether scanning is active
scanner_thread = None    # Thread handle
target_window = None     # The window being scanned


# ======= SCANNER THREAD FUNCTION =======
def _run_scanner():
    global running, target_window, clickable_controls

    # The key change is moving the context manager to the top of the function
    # This ensures that CoInitialize is called before the first uiautomation call.
    with UIAutomationInitializerInThread():
        # Save the starting window
        target_window = auto.GetForegroundControl()
        if not target_window:
            print("No active window found to scan.")
            running = False
            return

        print(f"\n[SCAN STARTED] Window: {target_window.Name}")
        print("=" * 50)

        while running:
            # If user switched windows → stop scanning
            current_window = auto.GetForegroundControl()
            if current_window and current_window.NativeWindowHandle != target_window.NativeWindowHandle:
                print("\n[SCAN STOPPED] Window changed.")
                running = False
                break

            clickable_controls = []

            def find_and_print_clickables(control):
                if not running:
                    return
                if isinstance(control, (auto.ButtonControl,
                                        auto.HyperlinkControl,
                                        auto.MenuItemControl,
                                        auto.TabItemControl,
                                        auto.CheckBoxControl,
                                        auto.RadioButtonControl)):
                    rect = control.BoundingRectangle
                    if rect:
                        cx = (rect.left + rect.right) // 2
                        cy = (rect.top + rect.bottom) // 2
                        print(f"Name: {control.Name}, Class: {control.ClassName}, "
                              f"Position: ({cx}, {cy})")
                        clickable_controls.append(control)

                for child in control.GetChildren():
                    find_and_print_clickables(child)

            find_and_print_clickables(target_window)
            time.sleep(1)


# ======= HOTKEY HANDLER FUNCTION =======
def scan_target_window():
    global running, scanner_thread

    if not running:
        # Start scanning
        running = True
        scanner_thread = threading.Thread(target=_run_scanner)
        scanner_thread.daemon = True
        scanner_thread.start()
    else:
        # Stop scanning
        running = False
        print("\n[SCAN STOPPED] (Hotkey pressed)")


# ======= MAIN EXECUTION BLOCK =======
print("Script loaded. Press " + HOTKEY + " to toggle scanning.")
keyboard.add_hotkey(HOTKEY, scan_target_window)
keyboard.wait()

import subprocess, pathlib, ctypes

win_path = r"H:\My Drive\Ho so ca nhan\b. ThS KHMT\Skill\Web Super\workspace"

# Close all lingering low-mem explorers first 
subprocess.run("taskkill /f /im explorer.exe /t", shell=True, capture_output=True)
import time; time.sleep(1)

# Restart the shell (critical for Google Drive paths)
subprocess.Popen("explorer.exe", shell=True)
time.sleep(1)

# Now open the target folder in a new window 
# Use STARTUPINFO to force foreground and new window
si = subprocess.STARTUPINFO()
si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
si.wShowWindow = 1  # SW_SHOWNORMAL
proc = subprocess.Popen(
    f'explorer.exe "{win_path}"',
    shell=False,
    executable="C:\\Windows\\explorer.exe",
    startupinfo=si,
    creationflags=subprocess.CREATE_NEW_CONSOLE
)
print("PID:", proc.pid)
time.sleep(2)

import sys; print("Done, check screen for Explorer window")

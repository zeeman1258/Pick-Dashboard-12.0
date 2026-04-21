#!/usr/bin/env python3
import os, subprocess, webbrowser, threading, time, signal, sys
from pathlib import Path

ROOT = Path(__file__).parent
PICK_APP  = ROOT / "pick-dashboard-app-3.6.6" / "pick-dashboard-app" / "app.py"
ANA_APP   = ROOT / "analytics-dashboard" / "app.py"

print("=== PICK DASHBOARD + ANALYTICS ===")
print(f"Pick app:      {PICK_APP}")
print(f"Analytics app: {ANA_APP}")

if not PICK_APP.exists():
    print(f"ERROR: Pick app not found at {PICK_APP}")
    input("Press Enter to exit...")
    sys.exit(1)
if not ANA_APP.exists():
    print(f"ERROR: Analytics app not found at {ANA_APP}")
    input("Press Enter to exit...")
    sys.exit(1)

print("\n🚚 Starting Pick Dashboard (port 5000)...")
p1 = subprocess.Popen([sys.executable, str(PICK_APP)], cwd=str(PICK_APP.parent))
time.sleep(1.5)

print("📊 Starting Analytics Dashboard (port 5001)...")
p2 = subprocess.Popen([sys.executable, str(ANA_APP)], cwd=str(ANA_APP.parent))

threading.Timer(3, lambda: webbrowser.open("http://localhost:5001")).start()

print("\n✅ Both running!")
print("Pick Dashboard : http://localhost:5000")
print("Analytics      : http://localhost:5001")
print("\nPress Ctrl+C to stop both...")

def stop(sig=None, frame=None):
    print("\nShutting down...")
    p1.terminate(); p2.terminate(); sys.exit(0)

signal.signal(signal.SIGINT, stop)
while True:
    time.sleep(1)

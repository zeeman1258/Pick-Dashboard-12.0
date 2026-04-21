Pick + Analytics Bundle 1.4

LAUNCH:
  python3 launcher.py

STRUCTURE:
  pick-analytics-bundle-1.4/
    pick-dashboard-app-3.6.6/
      pick-dashboard-app/
        app.py        ← Pick Dashboard (port 5000)
        data/         ← Routes saved here
    analytics-dashboard/
        app.py        ← Analytics (port 5001)
    launcher.py

Analytics auto-finds data/ from the pick app folder.

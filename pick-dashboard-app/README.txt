Pick Dashboard - web-ready multi-user app

Main admin default login:
- Username: zeck
- Password: zeeman1258

Notes:
- Replacing app.py keeps existing users and saved settings because they stay in pick_dashboard.db.
- users.txt is recreated from the database whenever users are created, updated, or deleted.
- The Windows launcher now opens the browser automatically to http://127.0.0.1:5000 when starting the app.
- Passwords in users.txt are stored as password hashes, not original plain-text passwords, because the database only stores hashed passwords.

Version 1.3 fixes:
- Restores predictable main admin login using the default built-in credentials unless you override them with environment variables.
- Opens the local dashboard in the browser automatically when started from Windows.
- Adds users.txt that is updated whenever users are created, updated, or deleted.
- Keeps the SQLite database and user settings in separate files so replacing app.py can keep the app operational.

Version 1.4 fixes:
- Fixes the missing open_browser_once function error on startup.

Version 1.5 fixes:
- Users can now reply back in support tickets like a customer support thread.
- users.txt now also stores each user's route-site login settings and refreshes when those settings are saved.

Version 1.6 note:
- users.txt is intended to store the plaintext password field, not the hashed password field.

Version 1.7 changes:
- Renames the top-right support button to Request feature.
- Updates the free-hosting tutorial with deployment-focused Render guidance and storage warnings.

Version 1.8 fixes:
- Changes the fallback port to 10000 for better Render compatibility.
- Updates deployment instructions so Render uses its own injected PORT variable instead of a manually forced one.

Version 1.9 changes:
- Adds automatic route detection instead of a manual route count field.
- Removes the Load day button and refreshes route data automatically every 3 minutes.
- Keeps already picked items visible by default and adds a Hide already picked toggle.
- Adds caching and threaded route loading to speed up repeated loads.

Version 2.0 changes:
- Preloads route data for all users when the app starts.
- Adds background server-side route refresh every 3 minutes.
- Adds a manual Refresh now button and a time-since-last-refresh indicator.
- Replaces the base root field with a Liquor/Hemp warehouse toggle.

Version 2.1 changes:
- Removes the Route site login section from the UI.
- Defaults route-site credentials to zeckm / Zm0948 for all users when blank.
- Improves authenticated route fetching and adds route debug output.

Version 2.2 changes:
- Adds an in-app Route debug button and debug panel so diagnostics are visible without manually opening /api/route_debug.

Version 2.3 fixes:
- Replaces the broken front-end script with one that matches the current UI so buttons work again.

Version 2.4 fixes:
- Fixes the SQLite SQL quoting error in init_db that prevented the app from starting.

Version 2.5 fixes:
- Adds a direct /api/load route decorator for compatibility with the current front end.
- Makes route-load failures show debug output without breaking button usability.

Version 2.6 fixes:
- Restores the /api/load and /api/picked endpoints expected by the current dashboard.
- Converts cached route data into the JSON shape used by the main route and item views.

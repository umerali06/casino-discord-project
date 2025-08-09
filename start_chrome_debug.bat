@echo off
echo ========================================
echo Starting Chrome with Debug Mode
echo ========================================
echo.

echo This will start Chrome with debugging enabled.
echo The roulette collector can then connect to this session.
echo.

echo Starting Chrome...
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir=./chrome_debug_profile

echo.
echo Chrome started with debugging on port 9222
echo Now you can:
echo 1. Navigate to the casino and log in
echo 2. Open the Immersive Roulette table
echo 3. Run the collector in another terminal
echo.

pause

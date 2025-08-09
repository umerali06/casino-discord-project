@echo off
echo ========================================
echo Evolution Gaming Roulette Collector
echo Installation Script
echo ========================================
echo.

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Creating necessary directories...
if not exist "data" mkdir data
if not exist "screenshots" mkdir screenshots
if not exist "logs" mkdir logs

echo.
echo Installation complete!
echo.
echo To start the collector, run:
echo python main.py
echo.
echo Press any key to exit...
pause > nul

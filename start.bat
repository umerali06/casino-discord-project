@echo off
echo ========================================
echo Evolution Gaming Roulette Collector
echo Starting (Stealth Mode)...
echo ========================================
echo.

echo Starting the roulette results collector with stealth mode...
echo This version bypasses Cloudflare and anti-bot protections.
echo.

python main_stealth.py

echo.
echo Collector stopped.
echo Press any key to exit...
pause > nul

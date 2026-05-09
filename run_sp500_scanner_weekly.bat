@echo off
setlocal EnableDelayedExpansion
REM S&P 500 sector scanner (yfinance, 64-bit Python 3.12). Output: sp500_universe.json

cd /d "%~dp0"
set "LOG=%~dp0sp500_scanner_weekly.log"
set "STATEDIR=%~dp0"
set "STATEDIR=!STATEDIR:~0,-1!"
(
echo ===== SP500 SCANNER START %DATE% %TIME% =====
py -3.12 -u "%~dp0sp500_scanner.py" ^
  --state-dir "!STATEDIR!" ^
  --top-sectors 3
set SCAN_ERR=!ERRORLEVEL!
echo ERRORLEVEL=!SCAN_ERR!
if !SCAN_ERR! equ 0 (
  if exist "%~dp0telegram_secrets.cmd" call "%~dp0telegram_secrets.cmd"
  py -3.12 "%~dp0scanner_telegram_notify.py" --state-dir "!STATEDIR!" --market sp500
)
echo ===== SP500 SCANNER END %DATE% %TIME% =====
echo.
) >> "!LOG!" 2>&1
call "%~dp0auto_push.bat"
endlocal

@echo off
setlocal EnableDelayedExpansion
REM Sector Relay 유니버스 (relay_universe.json, pykrx / 64비트 권장).
REM 작업 스케줄러: 이 BAT 트리거가 있어야 generated_at 가 갱신됨 — 매주 월요일 08:40 로 등록·확인.
REM 등록 안 하면 로그에 "이전 파일 그대로"만 쓰일 수 있음. 자동 등록: register_kiwoom_scheduled_tasks.ps1
REM 인자 규격: scanner.py --state-dir "%~dp0" --top-sectors 2  (작업 디렉터리 = 본 BAT 폴더)
REM py -3 고정 피함(32비트 3.13 조합 문제) → py -3.12 고정.

cd /d "%~dp0"
set "LOG=%~dp0scanner_weekly.log"
REM %~dp0 ends with \ ; inside quoted --state-dir "...\..." that backslash escapes the closing "
REM and glues the rest of the line into the path (WinError 123). Strip trailing backslash.
set "STATEDIR=%~dp0"
set "STATEDIR=!STATEDIR:~0,-1!"
(
echo ===== SCANNER START %DATE% %TIME% =====
py -3.12 -u "%~dp0scanner.py" ^
  --state-dir "!STATEDIR!" ^
  --top-sectors 2
set SCAN_ERR=!ERRORLEVEL!
echo ERRORLEVEL=!SCAN_ERR!
if !SCAN_ERR! equ 0 (
  if exist "%~dp0telegram_secrets.cmd" call "%~dp0telegram_secrets.cmd"
  py -3.12 "%~dp0scanner_telegram_notify.py" --state-dir "!STATEDIR!" --market kospi
)
echo ===== SCANNER END %DATE% %TIME% =====
echo.
) >> "!LOG!" 2>&1
call "%~dp0auto_push.bat"
endlocal

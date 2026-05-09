@echo off
cd /d "%~dp0"
where git >nul 2>&1
if errorlevel 1 (
  echo [PUSH] git 없음 — 건너뜀
  exit /b 0
)
if not exist ".git" (
  echo [PUSH] .git 없음 — git init 및 remote 추가 후 사용
  exit /b 0
)
git add relay_universe.json sp500_universe.json 2>nul
git diff --cached --quiet
if %errorlevel% equ 0 (
  echo [PUSH] 커밋할 변경 없음
  exit /b 0
)
git commit -m "scan %DATE% %TIME%"
if errorlevel 1 (
  echo [PUSH] commit 실패
  exit /b 1
)
git push origin gh-pages
if errorlevel 1 (
  echo [PUSH] push 실패 — remote/브랜치 확인
  exit /b 1
)
echo [PUSH] GitHub Pages 업로드 완료
exit /b 0

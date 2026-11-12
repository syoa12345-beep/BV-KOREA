@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ==========================================
echo   GitHub 자동 업로드를 시작합니다...
echo ==========================================

git add .
git commit -m "Auto update: %date% %time%"
git push origin main

echo.
echo ==========================================
echo   완료되었습니다! (1~2분 뒤 사이트 반영)
echo ==========================================
pause
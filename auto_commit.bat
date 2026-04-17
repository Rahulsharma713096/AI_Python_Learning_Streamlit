@echo off

cd /d C:\Users\hp\PycharmProjects\AI_Python_Learning

REM Get clean timestamp using PowerShell
for /f %%i in ('powershell -Command "Get-Date -Format yyyy-MM-dd_HH-mm"') do set datetime=%%i

echo ==============================
echo Adding files...
git add .

echo ==============================
echo Git Status:
git status

echo ==============================
echo Committing with timestamp...
git commit -m "Auto commit Done by Rahul %datetime%"

echo ==============================
echo Pushing to GitHub...
git push

echo ==============================
echo Done!
pause
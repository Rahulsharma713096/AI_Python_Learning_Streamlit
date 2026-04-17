@echo off

REM Go to project folder
cd /d C:\Users\hp\PycharmProjects\AI_Python_Learning

REM Get current date and time
for /f "tokens=1-4 delims=/ " %%a in ("%date%") do set mydate=%%d-%%b-%%c
for /f "tokens=1-2 delims=: " %%a in ("%time%") do set mytime=%%a-%%b

set datetime=%mydate%_%mytime%

echo ==============================
echo Adding files...
git add .

echo ==============================
echo Git Status:
git status

echo ==============================
echo Committing with timestamp...
git commit -m "Auto commit %datetime%"

echo ==============================
echo Done!
pause
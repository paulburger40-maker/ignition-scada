@echo off
setlocal
set "INSTALLDIR=C:\Program Files\Inductive Automation\Ignition"
set "SOURCE=C:\Users\Paul\OneDrive\Desktop\Ignition\home-scada\project"
set "TARGET=%INSTALLDIR%\data\projects\home_scada"
net session >nul 2>&1
if errorlevel 1 exit /b 10
if not exist "%TARGET%\project.json" exit /b 11
net stop Ignition
if errorlevel 1 exit /b 12
xcopy "%SOURCE%" "%TARGET%\" /E /I /Y >nul
if errorlevel 1 goto failed
net start Ignition
if errorlevel 1 exit /b 14
echo Home project UTC timestamp format corrected. Startup verification required.
exit /b 0
:failed
net start Ignition
exit /b 13

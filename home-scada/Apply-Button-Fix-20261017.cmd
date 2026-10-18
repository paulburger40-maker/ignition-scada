@echo off
setlocal
set "INSTALLDIR=C:\Program Files\Inductive Automation\Ignition"
set "WORKSPACE=C:\Users\Paul\OneDrive\Desktop\Ignition"
net session >nul 2>&1
if errorlevel 1 exit /b 10
if exist "%WORKSPACE%\backups\before-button-fix-20261017.gwbk" exit /b 11
cd /d "%INSTALLDIR%"
call gwcmd.bat -b "%WORKSPACE%\backups\before-button-fix-20261017.gwbk" -z 180
if errorlevel 1 exit /b 13
powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "%WORKSPACE%\home-scada\Apply-Button-Fix-20261017.ps1"
if errorlevel 1 exit /b 14
exit /b 0

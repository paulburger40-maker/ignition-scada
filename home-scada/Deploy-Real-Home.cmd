@echo off
setlocal
set "INSTALLDIR=C:\Program Files\Inductive Automation\Ignition"
set "WORKSPACE=C:\Users\Paul\OneDrive\Desktop\Ignition"
net session >nul 2>&1
if errorlevel 1 exit /b 10
if exist "%WORKSPACE%\backups\before-real-only-20261010.gwbk" exit /b 11
if not exist "%INSTALLDIR%\data\projects\home_scada\project.json" exit /b 12
cd /d "%INSTALLDIR%"
call gwcmd.bat -b "%WORKSPACE%\backups\before-real-only-20261010.gwbk" -z 180
if errorlevel 1 exit /b 13
xcopy "%WORKSPACE%\home-scada\project" "%INSTALLDIR%\data\projects\home_scada\" /E /I /Y >nul
if errorlevel 1 exit /b 14
call gwcmd.bat -r
if errorlevel 1 exit /b 15
exit /b 0

@echo off
setlocal
set "INSTALLDIR=C:\Program Files\Inductive Automation\Ignition"
set "WORKSPACE=C:\Users\Paul\OneDrive\Desktop\Ignition"
net session >nul 2>&1
if errorlevel 1 exit /b 10
if exist "%WORKSPACE%\backups\before-meter-identity-20261017.gwbk" exit /b 11
cd /d "%INSTALLDIR%"
call gwcmd.bat -b "%WORKSPACE%\backups\before-meter-identity-20261017.gwbk" -z 180
if errorlevel 1 exit /b 13
xcopy "%WORKSPACE%\home-scada\project\ignition\script-python\cube_meter" "%INSTALLDIR%\data\projects\home_scada\ignition\script-python\cube_meter\" /I /Y >nul
if errorlevel 1 exit /b 14
exit /b 0

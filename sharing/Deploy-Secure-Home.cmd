@echo off
setlocal
set "INSTALLDIR=C:\Program Files\Inductive Automation\Ignition"
set "WORKSPACE=C:\Users\Paul\OneDrive\Desktop\Ignition"
set "TARGET=%INSTALLDIR%\data\projects\home_scada"
net session >nul 2>&1
if errorlevel 1 exit /b 10
if not exist "%TARGET%\project.json" exit /b 11
if exist "%WORKSPACE%\backups\before-sharing-20261010.gwbk" exit /b 12
cd /d "%INSTALLDIR%"
call gwcmd.bat -b "%WORKSPACE%\backups\before-sharing-20261010.gwbk" -z 180
if errorlevel 1 exit /b 13
xcopy "%WORKSPACE%\home-scada\project" "%TARGET%\" /E /I /Y >nul
if errorlevel 1 exit /b 14
call gwcmd.bat -r
if errorlevel 1 exit /b 15
echo Authentication and control-role project resources deployed. Verify anonymous rejection before sharing.
exit /b 0

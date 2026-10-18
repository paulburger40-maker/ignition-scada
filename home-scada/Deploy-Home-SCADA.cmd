@echo off
setlocal
set "INSTALLDIR=C:\Program Files\Inductive Automation\Ignition"
set "WORKSPACE=C:\Users\Paul\OneDrive\Desktop\Ignition"
set "TARGET=%INSTALLDIR%\data\projects\home_scada"
net session >nul 2>&1
if errorlevel 1 exit /b 10
if exist "%TARGET%" (
  echo Existing home_scada directory found. Refusing to overwrite it.
  exit /b 11
)
cd /d "%INSTALLDIR%"
call gwcmd.bat -b "%WORKSPACE%\backups\before-home-scada-20261009.gwbk" -z 180
if errorlevel 1 exit /b 12
xcopy "%WORKSPACE%\home-scada\project" "%TARGET%\" /E /I /Y >nul
if errorlevel 1 exit /b 13
call gwcmd.bat -r
if errorlevel 1 exit /b 14
echo Separate home_scada project files deployed and Gateway reload requested. Runtime verification remains required.
exit /b 0

@echo off
setlocal
set "INSTALLDIR=C:\Program Files\Inductive Automation\Ignition"
set "WORKSPACE=C:\Users\Paul\OneDrive\Desktop\Ignition"
if exist "%WORKSPACE%\sharing\recovery-cancelled.flag" exit /b 20
net session >nul 2>&1
if errorlevel 1 exit /b 10
if exist "%WORKSPACE%\backups\before-password-recovery-20261010.gwbk" exit /b 11
cd /d "%INSTALLDIR%"
call gwcmd.bat -b "%WORKSPACE%\backups\before-password-recovery-20261010.gwbk" -z 180
if errorlevel 1 exit /b 12
rem This step is allowed only after explicit recovery approval.
rem No recovery credentials or CLI output are written to workspace files.
call gwcmd.bat -p -y
if errorlevel 1 exit /b 13
call gwcmd.bat -r
if errorlevel 1 exit /b 14
exit /b 0

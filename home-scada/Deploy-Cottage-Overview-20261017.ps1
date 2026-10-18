$ErrorActionPreference='Stop'
$workspaceDirectory='C:\Users\Paul\OneDrive\Desktop\Ignition'
$gatewayDirectory='C:\Program Files\Inductive Automation\Ignition'
$projectsDirectory=Join-Path $gatewayDirectory 'data\projects'
$projectPath=[IO.Path]::GetFullPath((Join-Path $projectsDirectory 'home_scada'))
$sourcePath=Join-Path $workspaceDirectory 'home-scada\overview-project'
$archivePath=[IO.Path]::GetFullPath((Join-Path $workspaceDirectory 'backups\home_scada-before-overview-20261017'))
$stagePath=[IO.Path]::GetFullPath((Join-Path $gatewayDirectory 'data\project-staging\home_scada-overview-20261017'))
$failedPath=[IO.Path]::GetFullPath((Join-Path $gatewayDirectory 'data\project-staging\home_scada-overview-failed-20261017'))
# Validate every recursive move target before changing any directory.
if ($projectPath -ne 'C:\Program Files\Inductive Automation\Ignition\data\projects\home_scada') { throw 'Unexpected project target' }
if (-not $archivePath.StartsWith($workspaceDirectory+'\backups\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Archive target is outside workspace backups' }
foreach ($targetPath in @($stagePath,$failedPath)) {
 if (-not $targetPath.StartsWith($gatewayDirectory+'\data\project-staging\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Staging path outside Gateway staging directory' }
}
if (Test-Path -LiteralPath $archivePath) { throw 'Existing archive preserved; refusing duplicate deployment' }
if (Test-Path -LiteralPath $stagePath) { throw 'Existing staging directory requires review' }
if (-not (Test-Path -LiteralPath (Join-Path $workspaceDirectory 'backups\before-cottage-overview-20261017.gwbk'))) { throw 'Supported Gateway backup missing' }
foreach ($relative in @('ignition\global-props\data.bin','com.inductiveautomation.perspective\session-permissions\data.bin')) {
 if ((Get-FileHash -LiteralPath (Join-Path $projectPath $relative)).Hash -ne (Get-FileHash -LiteralPath (Join-Path $sourcePath $relative)).Hash) { throw 'Project authentication differs; deployment stopped' }
}
$connectionPath=Join-Path $gatewayDirectory 'data\config\resources\core\ignition\database-connection\Home_Energy_SQLite'
if (Test-Path -LiteralPath $connectionPath) { throw 'Existing history connection requires review; not overwritten' }
$energyDataDirectory='C:\Users\Paul\IgnitionHome\history\cottage-overview'
if (-not (Test-Path -LiteralPath $energyDataDirectory)) { New-Item -ItemType Directory -Path $energyDataDirectory | Out-Null }
$dataUser=[System.Security.Principal.WindowsIdentity]::GetCurrent().Name
& icacls.exe $energyDataDirectory /inheritance:r /grant:r ($dataUser+':(OI)(CI)F') 'SYSTEM:(OI)(CI)F' 'Administrators:(OI)(CI)F' | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Unable to protect energy history directory' }
$gatewayService=Get-CimInstance Win32_Service -Filter "Name='Ignition'"
$gatewayProcessIds=@($gatewayService.ProcessId)+@(Get-CimInstance Win32_Process | Where-Object ParentProcessId -eq $gatewayService.ProcessId | Select-Object -ExpandProperty ProcessId)
Stop-Service Ignition
(Get-Service Ignition).WaitForStatus('Stopped',[TimeSpan]::FromSeconds(90))
$moved=$false
try {
 foreach ($gatewayProcessId in $gatewayProcessIds) {
  $gatewayProcess=Get-Process -Id $gatewayProcessId -ErrorAction SilentlyContinue
  if ($gatewayProcess -and -not $gatewayProcess.WaitForExit(90000)) { throw 'Gateway process still running' }
 }
 $stageParent=Split-Path -Parent $stagePath
 if (-not (Test-Path -LiteralPath $stageParent)) { New-Item -ItemType Directory -Path $stageParent | Out-Null }
 Copy-Item -LiteralPath $sourcePath -Destination $stagePath -Recurse
 Get-ChildItem -LiteralPath $sourcePath -File -Recurse | ForEach-Object {
  $relative=$_.FullName.Substring($sourcePath.Length+1)
  if ((Get-FileHash -LiteralPath $_.FullName).Hash -ne (Get-FileHash -LiteralPath (Join-Path $stagePath $relative)).Hash) { throw 'Staged resource verification failed' }
 }
 Copy-Item -LiteralPath (Join-Path $workspaceDirectory 'home-scada\gateway-config\ignition\database-connection\Home_Energy_SQLite') -Destination $connectionPath -Recurse
 Move-Item -LiteralPath $projectPath -Destination $archivePath
 $moved=$true
 Move-Item -LiteralPath $stagePath -Destination $projectPath
 Write-Output 'Single Overview installed; old house resources archived; authentication hashes unchanged'
} catch {
 if ($moved) {
  if (Test-Path -LiteralPath $projectPath) { Move-Item -LiteralPath $projectPath -Destination $failedPath }
  Move-Item -LiteralPath $archivePath -Destination $projectPath
 }
 throw
} finally { Start-Service Ignition }
Write-Output 'Gateway starting; verify live chart data and dedicated history storage'

$ErrorActionPreference='Stop'
$workspaceDirectory='C:\Users\Paul\OneDrive\Desktop\Ignition'
$gatewayDirectory='C:\Program Files\Inductive Automation\Ignition'
$backupPath=Join-Path $workspaceDirectory 'backups\before-meter-identity-20261017.gwbk'
if (-not (Test-Path -LiteralPath $backupPath)) { throw 'Supported pre-change backup missing' }
$gatewayService=Get-CimInstance Win32_Service -Filter "Name='Ignition'"
$gatewayProcessIds=@($gatewayService.ProcessId)+@(Get-CimInstance Win32_Process | Where-Object ParentProcessId -eq $gatewayService.ProcessId | Select-Object -ExpandProperty ProcessId)
Stop-Service Ignition
(Get-Service Ignition).WaitForStatus('Stopped',[TimeSpan]::FromSeconds(90))
try {
 foreach ($gatewayProcessId in $gatewayProcessIds) {
  $gatewayProcess=Get-Process -Id $gatewayProcessId -ErrorAction SilentlyContinue
  if ($gatewayProcess -and -not $gatewayProcess.WaitForExit(90000)) { throw 'Gateway process still running' }
 }
 $source=Join-Path $workspaceDirectory 'home-scada\project\ignition\script-python\cube_meter'
 $destination=Join-Path $gatewayDirectory 'data\projects\home_scada\ignition\script-python\cube_meter'
 foreach ($fileName in @('code.py','resource.json')) { Copy-Item -LiteralPath (Join-Path $source $fileName) -Destination (Join-Path $destination $fileName) -Force }
} finally { Start-Service Ignition }
Write-Output 'Exact built-in device identity mapping installed; Gateway starting'

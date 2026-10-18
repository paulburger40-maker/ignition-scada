$ErrorActionPreference='Stop'
$workspaceDirectory='C:\Users\Paul\OneDrive\Desktop\Ignition'
$gatewayDirectory='C:\Program Files\Inductive Automation\Ignition'
if (-not (Test-Path -LiteralPath (Join-Path $workspaceDirectory 'backups\before-button-fix-20261017.gwbk'))) { throw 'Supported Gateway backup missing' }
$gatewayService=Get-CimInstance Win32_Service -Filter "Name='Ignition'"
$gatewayProcessIds=@($gatewayService.ProcessId)+@(Get-CimInstance Win32_Process | Where-Object ParentProcessId -eq $gatewayService.ProcessId | Select-Object -ExpandProperty ProcessId)
Stop-Service Ignition
(Get-Service Ignition).WaitForStatus('Stopped',[TimeSpan]::FromSeconds(90))
try {
 foreach ($gatewayProcessId in $gatewayProcessIds) {
  $gatewayProcess=Get-Process -Id $gatewayProcessId -ErrorAction SilentlyContinue
  if ($gatewayProcess -and -not $gatewayProcess.WaitForExit(90000)) { throw 'Gateway process still running' }
 }
 foreach ($relativePath in @('ignition\script-python\home_scada','com.inductiveautomation.perspective\views\Home')) {
  $source=Join-Path (Join-Path $workspaceDirectory 'home-scada\project') $relativePath
  $destination=Join-Path (Join-Path $gatewayDirectory 'data\projects\home_scada') $relativePath
  Get-ChildItem -LiteralPath $source | ForEach-Object { Copy-Item -LiteralPath $_.FullName -Destination $destination -Recurse -Force }
 }
} finally { Start-Service Ignition }
Write-Output 'House navigation and popup update complete; Gateway starting'

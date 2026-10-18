$ErrorActionPreference='Stop'
$gatewayDirectory='C:\Program Files\Inductive Automation\Ignition'
$workspaceDirectory='C:\Users\Paul\OneDrive\Desktop\Ignition'
$backupPath=Join-Path $workspaceDirectory 'backups\before-phone-fix-20261017.gwbk'
if (-not (Test-Path -LiteralPath $backupPath)) { throw 'Supported backup missing' }
if ((Get-NetFirewallRule -Name HomeSCADA-Block-Direct-HTTP).Enabled -ne 'True') { throw 'Remote HTTP block must be active before trusting proxy headers' }
$gatewayService=Get-CimInstance Win32_Service -Filter "Name='Ignition'"
$gatewayProcessIds=@($gatewayService.ProcessId)+@(Get-CimInstance Win32_Process | Where-Object ParentProcessId -eq $gatewayService.ProcessId | Select-Object -ExpandProperty ProcessId)
Stop-Service Ignition
(Get-Service Ignition).WaitForStatus('Stopped',[TimeSpan]::FromSeconds(90))
foreach ($gatewayProcessId in $gatewayProcessIds) {
 $gatewayProcess=Get-Process -Id $gatewayProcessId -ErrorAction SilentlyContinue
 if ($gatewayProcess -and -not $gatewayProcess.WaitForExit(90000)) { throw 'Gateway process still running; configuration not changed' }
}
$xmlPath=Join-Path $gatewayDirectory 'data\gateway.xml'
Copy-Item -LiteralPath $xmlPath -Destination (Join-Path $workspaceDirectory 'backups\gateway-before-phone-fix-20261017.xml')
try {
 & (Join-Path $gatewayDirectory 'lib\runtime\jre-win\bin\java.exe') '-Dpython.console.encoding=UTF-8' -cp (Join-Path $gatewayDirectory 'lib\core\common\jython-ia-2.7.4.0.jar') org.python.util.jython -S -B (Join-Path $workspaceDirectory 'sharing\write-phone-properties.py') $xmlPath
 if ($LASTEXITCODE -ne 0) { throw 'Java settings update failed' }
 foreach ($relativePath in @('ignition\script-python\cube_meter','ignition\startup')) {
  $source=Join-Path (Join-Path $workspaceDirectory 'home-scada\project') $relativePath
  $destination=Join-Path (Join-Path $gatewayDirectory 'data\projects\home_scada') $relativePath
  if (-not (Test-Path -LiteralPath $destination)) { New-Item -ItemType Directory -Path $destination | Out-Null }
  Get-ChildItem -LiteralPath $source -File | ForEach-Object { Copy-Item -LiteralPath $_.FullName -Destination $destination -Force }
 }
} catch {
 Copy-Item -LiteralPath (Join-Path $workspaceDirectory 'backups\gateway-before-phone-fix-20261017.xml') -Destination $xmlPath -Force
 throw
} finally { Start-Service Ignition }
Write-Output 'Phone settings and read-only meter startup installed; verify live metadata after startup'

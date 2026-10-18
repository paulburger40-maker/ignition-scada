$ErrorActionPreference='Stop'
$gatewayDirectory='C:\Program Files\Inductive Automation\Ignition'
$workspaceDirectory='C:\Users\Paul\OneDrive\Desktop\Ignition'
$backupPath=Join-Path $workspaceDirectory 'backups\before-phone-gateway-retry-20261011.gwbk'
if (-not (Test-Path -LiteralPath $backupPath)) { throw 'Supported Gateway backup is required' }
$gatewayXmlPath=Join-Path $gatewayDirectory 'data\gateway.xml'
$changes=@{
 'gateway.publicAddress.autoDetect'='false'
 'gateway.publicAddress.address'='home-scada.tail78dd75.ts.net'
 'gateway.publicAddress.httpPort'='80'
 'gateway.publicAddress.httpsPort'='443'
 'gateway.useProxyForwardedHeader'='true'
}
$ruleName='HomeSCADA-Block-Direct-HTTP'
$existingRule=Get-NetFirewallRule -Name $ruleName -ErrorAction SilentlyContinue
@{ruleName=$ruleName;created=(-not [bool]$existingRule)} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $workspaceDirectory 'backups\phone-firewall-change-20261011.json') -Encoding UTF8
if (-not $existingRule) {
 New-NetFirewallRule -Name $ruleName -DisplayName 'Home SCADA - require secure proxy for remote HTTP' -Direction Inbound -Action Block -Protocol TCP -LocalPort 8088 -Profile Any | Out-Null
}
$gatewayService=Get-CimInstance Win32_Service -Filter "Name='Ignition'"
$gatewayProcessIds=@($gatewayService.ProcessId)+@(Get-CimInstance Win32_Process | Where-Object ParentProcessId -eq $gatewayService.ProcessId | Select-Object -ExpandProperty ProcessId)
Stop-Service -Name Ignition
(Get-Service Ignition).WaitForStatus('Stopped',[TimeSpan]::FromSeconds(90))
foreach ($gatewayProcessId in $gatewayProcessIds) {
 $gatewayProcess=Get-Process -Id $gatewayProcessId -ErrorAction SilentlyContinue
 if ($gatewayProcess -and -not $gatewayProcess.WaitForExit(90000)) { throw 'Gateway process did not exit; XML not changed' }
}
try {
 $gatewayDocument=New-Object System.Xml.XmlDocument
 $gatewayDocument.PreserveWhitespace=$true
 $gatewayDocument.Load($gatewayXmlPath)
 $before=@{}
 foreach ($key in $changes.Keys) {
  $entry=$gatewayDocument.SelectSingleNode("//entry[@key='$key']")
  if (-not $entry) { throw "Missing documented setting: $key" }
  $before[$key]=$entry.InnerText
 }
 $before | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $workspaceDirectory 'backups\phone-web-settings-before-retry-20261011.json') -Encoding UTF8
 foreach ($key in $changes.Keys) { $gatewayDocument.SelectSingleNode("//entry[@key='$key']").InnerText=$changes[$key] }
 $gatewayDocument.Save($gatewayXmlPath)
 $verifyDocument=New-Object System.Xml.XmlDocument
 $verifyDocument.Load($gatewayXmlPath)
 foreach ($key in $changes.Keys) { if ($verifyDocument.SelectSingleNode("//entry[@key='$key']").InnerText -ne $changes[$key]) { throw "Setting verification failed: $key" } }
 Write-Output 'Saved web settings verified after all Gateway processes exited'
 Copy-Item -LiteralPath (Join-Path $workspaceDirectory 'home-scada\project\ignition\script-python\cube_meter\code.py') -Destination (Join-Path $gatewayDirectory 'data\projects\home_scada\ignition\script-python\cube_meter\code.py') -Force
 Copy-Item -LiteralPath (Join-Path $workspaceDirectory 'home-scada\project\ignition\script-python\cube_meter\resource.json') -Destination (Join-Path $gatewayDirectory 'data\projects\home_scada\ignition\script-python\cube_meter\resource.json') -Force
} finally {
 Start-Service -Name Ignition
}
Write-Output 'Phone Gateway address and trusted proxy settings applied; service starting'

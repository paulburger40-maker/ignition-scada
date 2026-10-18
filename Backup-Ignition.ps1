# Run from an administrator PowerShell session. Creates a supported Gateway backup.
$ErrorActionPreference = 'Stop'
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Administrator access is required. Open PowerShell as administrator, then run this script again.'
}
$workspacePath = $PSScriptRoot
$installPath = 'C:\Program Files\Inductive Automation\Ignition'
$backupDirectory = Join-Path $workspacePath 'backups'
New-Item -ItemType Directory -Path $backupDirectory -Force | Out-Null
$backupPath = Join-Path $backupDirectory ('before-setup-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.gwbk')
Push-Location -LiteralPath $installPath
try {
    & (Join-Path $installPath 'gwcmd.bat') -b $backupPath -z 180
    if ($LASTEXITCODE -ne 0) { throw "Ignition backup command failed with exit code $LASTEXITCODE" }
} finally { Pop-Location }
if (-not (Test-Path -LiteralPath $backupPath)) { throw 'The backup command did not create a file.' }
$backupFile = Get-Item -LiteralPath $backupPath
if ($backupFile.Length -eq 0) { throw 'The backup file is empty.' }
$result = [ordered]@{
    file = $backupFile.Name
    bytes = $backupFile.Length
    sha256 = (Get-FileHash -LiteralPath $backupPath -Algorithm SHA256).Hash.ToLowerInvariant()
    createdUtc = [DateTime]::UtcNow.ToString('o')
    method = 'Official gwcmd -b'
    restoreTested = $false
}
$result | ConvertTo-Json | Set-Content -LiteralPath ($backupPath + '.verification.json') -Encoding utf8
Write-Output "Backup created: $backupPath"
Write-Output 'A restore test on an isolated development Gateway is still required.'

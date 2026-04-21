# One-shot backup verification:
#   1. List snapshots
#   2. `restic check` with 10% read-data-subset (downloads and verifies ~10% of stored blobs)
#   3. File-level restore round-trip: restore tasks/lessons.md to a temp dir, SHA256-diff against source
#
# Reuses the same <password-manager>-backed credential flow as backup-restic.ps1.

$SourcePath    = '<workspace>'
$TestFile      = 'tasks\lessons.md'
$RestoreTarget = Join-Path $env:TEMP 'claude-restore-verify'
$RepoPath      = 'claude'

$B2ItemName = '<object-storage-login>'
$PwItemName = 'Claude Backup - Restic Repo Password'

function Resolve-Binary {
    param([string]$Name, [string]$GlobPattern)
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $hit = Get-ChildItem -Path "$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -Filter $GlobPattern -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($hit) { return $hit.FullName }
    return $null
}
$ResticExe = Resolve-Binary -Name 'restic' -GlobPattern 'restic*.exe'
$BwExe     = Resolve-Binary -Name 'bw'     -GlobPattern 'bw.exe'
if (-not $ResticExe) { Write-Error "restic not found"; exit 1 }
if (-not $BwExe)     { Write-Error "bw not found"; exit 1 }

$status = (& $BwExe status | ConvertFrom-Json).status
if ($status -eq 'unauthenticated') { Write-Error "Run: bw login <your-email>@example.com"; exit 1 }
if ($status -eq 'locked') {
    Write-Host "Unlocking <password-manager> vault (enter master password)..."
    $env:BW_SESSION = & $BwExe unlock --raw
    if (-not $env:BW_SESSION) { Write-Error "Unlock failed"; exit 1 }
}
& $BwExe sync --quiet | Out-Null

$b2Item = (& $BwExe get item $B2ItemName) | ConvertFrom-Json
$keyId      = ($b2Item.fields | Where-Object { $_.name -eq 'keyID' }).value
$appKey     = ($b2Item.fields | Where-Object { $_.name -eq 'applicationKey' }).value
$bucketName = ($b2Item.fields | Where-Object { $_.name -eq 'bucketName' }).value
$resticPw   = & $BwExe get password $PwItemName

$env:B2_ACCOUNT_ID     = $keyId
$env:B2_ACCOUNT_KEY    = $appKey
$env:RESTIC_REPOSITORY = "b2:${bucketName}:/${RepoPath}"
$env:RESTIC_PASSWORD   = $resticPw

try {
    Write-Host ""
    Write-Host "=== Snapshots ==="
    & $ResticExe snapshots
    if ($LASTEXITCODE -ne 0) { throw "restic snapshots failed" }

    Write-Host ""
    Write-Host "=== Integrity check (10% data sample) ==="
    & $ResticExe check --read-data-subset '10%'
    if ($LASTEXITCODE -ne 0) { throw "restic check failed" }

    if (Test-Path $RestoreTarget) { Remove-Item -Recurse -Force $RestoreTarget }

    Write-Host ""
    Write-Host "=== Restore round-trip: $TestFile ==="
    & $ResticExe restore latest --target $RestoreTarget --include "**/$TestFile"
    if ($LASTEXITCODE -ne 0) { throw "restic restore failed" }

    $restored = Get-ChildItem -Path $RestoreTarget -Recurse -File -Filter (Split-Path $TestFile -Leaf) | Select-Object -First 1
    if (-not $restored) { throw "Restored file not found under $RestoreTarget" }

    $orig = Join-Path $SourcePath $TestFile
    $origHash = (Get-FileHash -Path $orig              -Algorithm SHA256).Hash
    $restHash = (Get-FileHash -Path $restored.FullName -Algorithm SHA256).Hash

    Write-Host "Source   : $orig"
    Write-Host "Restored : $($restored.FullName)"
    Write-Host "Source   SHA256: $origHash"
    Write-Host "Restored SHA256: $restHash"

    if ($origHash -ne $restHash) { throw "Hash mismatch. Backup is not restoring file-identical content." }

    Write-Host ""
    Write-Host "=== VERIFICATION PASSED ==="
    Write-Host "  Repo integrity: OK (10% data read + checksummed)"
    Write-Host "  Restore round-trip: byte-identical"
    Remove-Item -Recurse -Force $RestoreTarget
}
finally {
    Remove-Item Env:B2_ACCOUNT_ID, Env:B2_ACCOUNT_KEY, Env:RESTIC_PASSWORD, Env:RESTIC_REPOSITORY -ErrorAction SilentlyContinue
}

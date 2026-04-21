# Encrypted incremental backup of <workspace> to <object-storage> via restic.
# Credentials pulled from <password-manager> CLI at runtime — nothing sensitive in this file.
#
# Prereqs: restic + bw on PATH, `bw login` completed once.
# Run: double-click backup-restic.bat, or `.\backup-restic.ps1` from PowerShell.

# Don't use $ErrorActionPreference = 'Stop' — PS 5.1 promotes native stderr writes to
# NativeCommandError, which conflicts with restic (404 probe, progress output, etc.).
# Every native call below is followed by an explicit $LASTEXITCODE check.

# --- Config ---
$SourcePath  = '<workspace>'
$ExcludeFile = Join-Path $PSScriptRoot 'backup-excludes.txt'
$RepoPath    = 'claude'

$B2ItemName = '<object-storage-login>'
$PwItemName = 'Claude Backup - Restic Repo Password'

# --- Resolve binaries (PATH may not be updated after fresh winget install) ---
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
if (-not $ResticExe) { Write-Error "restic not found. Install: winget install restic.restic"; exit 1 }
if (-not $BwExe)     { Write-Error "bw not found. Install: winget install <password-manager>.CLI"; exit 1 }

# --- <password-manager> auth ---
$status = (& $BwExe status | ConvertFrom-Json).status
switch ($status) {
    'unauthenticated' {
        Write-Error "<password-manager> CLI not logged in. Run: bw login <your-email>@example.com"
        exit 1
    }
    'locked' {
        Write-Host "Unlocking <password-manager> vault (enter master password)..."
        $env:BW_SESSION = & $BwExe unlock --raw
        if (-not $env:BW_SESSION) {
            Write-Error "<password-manager> unlock failed."
            exit 1
        }
    }
}

& $BwExe sync --quiet | Out-Null

# --- Retrieve B2 credentials from custom fields on the <object-storage> login item ---
$b2Json = & $BwExe get item $B2ItemName 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "<password-manager> item '$B2ItemName' not found or ambiguous. Raw: $b2Json"
    exit 1
}
$b2Item = $b2Json | ConvertFrom-Json
$keyId      = ($b2Item.fields | Where-Object { $_.name -eq 'keyID' }).value
$appKey     = ($b2Item.fields | Where-Object { $_.name -eq 'applicationKey' }).value
$bucketName = ($b2Item.fields | Where-Object { $_.name -eq 'bucketName' }).value

if (-not $keyId)      { Write-Error "'$B2ItemName' is missing custom field 'keyID'."; exit 1 }
if (-not $appKey)     { Write-Error "'$B2ItemName' is missing custom field 'applicationKey'."; exit 1 }
if (-not $bucketName) { Write-Error "'$B2ItemName' is missing custom field 'bucketName'."; exit 1 }

# --- Retrieve restic repo password ---
$resticPw = & $BwExe get password $PwItemName 2>&1
if ($LASTEXITCODE -ne 0 -or -not $resticPw) {
    Write-Error "Could not retrieve password from <password-manager> item '$PwItemName'. Raw: $resticPw"
    exit 1
}

# --- Export env vars for restic ---
$env:B2_ACCOUNT_ID     = $keyId
$env:B2_ACCOUNT_KEY    = $appKey
$env:RESTIC_REPOSITORY = "b2:${bucketName}:/${RepoPath}"
$env:RESTIC_PASSWORD   = $resticPw

try {
    # --- Init repo on first run ---
    Write-Host "Checking restic repository at $($env:RESTIC_REPOSITORY)..."
    $probeExit = 0
    try {
        $null = & $ResticExe cat config 2>&1
        $probeExit = $LASTEXITCODE
    } catch {
        $probeExit = if ($LASTEXITCODE) { $LASTEXITCODE } else { 1 }
    }
    if ($probeExit -eq 10 -or $probeExit -eq 12) {
        # 10 = repo does not exist (restic 0.17+); 12 = no config file
        Write-Host "Repository does not exist yet. Initialising..."
        & $ResticExe init
        if ($LASTEXITCODE -ne 0) { throw "restic init failed" }
    } elseif ($probeExit -ne 0) {
        throw "restic cat config failed with exit code $probeExit (not a missing-repo signal)"
    }

    # --- Backup ---
    Write-Host ""
    Write-Host "=== Backup: $SourcePath ==="
    & $ResticExe backup $SourcePath --exclude-file=$ExcludeFile --tag scheduled
    if ($LASTEXITCODE -ne 0) { throw "restic backup failed" }

    # --- Retention (7 daily + 4 weekly + 6 monthly) ---
    Write-Host ""
    Write-Host "=== Retention policy ==="
    & $ResticExe forget --keep-daily 7 --keep-weekly 4 --keep-monthly 6 --prune
    if ($LASTEXITCODE -ne 0) { throw "restic forget failed" }

    # --- Stats ---
    Write-Host ""
    Write-Host "=== Repo stats ==="
    & $ResticExe stats --mode raw-data

    Write-Host ""
    Write-Host "Backup complete."
}
finally {
    Remove-Item Env:B2_ACCOUNT_ID, Env:B2_ACCOUNT_KEY, Env:RESTIC_PASSWORD, Env:RESTIC_REPOSITORY -ErrorAction SilentlyContinue
}

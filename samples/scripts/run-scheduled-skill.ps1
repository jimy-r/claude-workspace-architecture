#Requires -Version 5.1
<#
.SYNOPSIS
  Headless launcher for Claude Code scheduled-task SKILL.md files.

.DESCRIPTION
  Reads a SKILL.md from `~/.claude/scheduled-tasks/<Skill>/` and pipes it as
  the prompt to `claude --print`, with `<workspace>` on the tool-access list.
  Output is tee'd to `<workspace>\tasks\scheduled-logs\<Skill>_<date-time>.log`.

  Invoked by Windows Task Scheduler entries that own the cron cadence. This
  is the workaround for the built-in `scheduled-tasks` MCP being unconnected
  in this environment — registration there would be the canonical path, but
  until it's available, Task Scheduler + this wrapper is the durable route.

.PARAMETER Skill
  Name of the subfolder under `~/.claude/scheduled-tasks/` (e.g. `morning-brief`).

.PARAMETER DryRun
  Resolve + print paths and prompt size, do not invoke `claude`.

.EXAMPLE
  pwsh -NoProfile -ExecutionPolicy Bypass -File run-scheduled-skill.ps1 -Skill morning-brief
#>
param(
    [Parameter(Mandatory)][string]$Skill,
    [switch]$DryRun
)

# Native-command hygiene: do NOT set $ErrorActionPreference = 'Stop' globally
# (lesson 2026-04-19: PS 5.1 promotes native stderr to NativeCommandError).
$ErrorActionPreference = 'Continue'

$SkillFile = Join-Path $env:USERPROFILE ".claude\scheduled-tasks\$Skill\SKILL.md"
if (-not (Test-Path $SkillFile)) {
    Write-Error "Skill not found: $SkillFile"
    exit 1
}

$TodayTag = Get-Date -Format 'yyyy-MM-dd-HHmm'
$LogDir = '<workspace>\tasks\scheduled-logs'
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
$LogFile = Join-Path $LogDir "${Skill}_${TodayTag}.log"

if ($DryRun) {
    $prompt = Get-Content $SkillFile -Raw
    Write-Host "Skill:        $Skill"
    Write-Host "SKILL.md:     $SkillFile"
    Write-Host "Log file:     $LogFile"
    Write-Host "Prompt chars: $($prompt.Length)"
    Write-Host "Would invoke: claude --print --add-dir <workspace>"
    exit 0
}

Set-Location '<workspace>'

# Pipe SKILL.md content as stdin; tee all output (stdout + stderr merged) to log.
Get-Content $SkillFile -Raw | & claude --print --add-dir '<workspace>' *>&1 |
    Tee-Object -FilePath $LogFile

$code = $LASTEXITCODE
if ($null -eq $code) { $code = 0 }
Write-Host "claude exit code: $code"
exit $code

#!/usr/bin/env pwsh
<#
.SYNOPSIS
Count files by extension in a directory and its subdirectories. Outputs JSON.

.PARAMETER Path
The root directory to scan (default: current directory).

.EXAMPLE
.\count_files.ps1 -Path "C:\Documents"
.\count_files.ps1  # scan current directory
#>

param(
    [string]$Path = "."
)

if (-not (Test-Path $Path)) {
    Write-Error "Path not found: $Path"
    exit 1
}

$files = Get-ChildItem -Path $Path -File -Recurse -ErrorAction SilentlyContinue

$result = [ordered]@{}

$files |
    Group-Object -Property Extension |
    Sort-Object -Property Count -Descending |
    ForEach-Object {
        $ext = if ($_.Name) { $_.Name.ToLower() } else { "(no extension)" }
        $result[$ext] = $_.Count
    }

$result["total"] = $files.Count

$result | ConvertTo-Json

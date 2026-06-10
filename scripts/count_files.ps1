#!/usr/bin/env pwsh
<#
.SYNOPSIS
Count files in a directory and its subdirectories.

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

$totalFiles = (Get-ChildItem -Path $Path -File -Recurse -ErrorAction SilentlyContinue).Count
$totalDirs = (Get-ChildItem -Path $Path -Directory -Recurse -ErrorAction SilentlyContinue).Count

Write-Host "Directory: $(Resolve-Path $Path)"
Write-Host "Total files: $totalFiles"
Write-Host "Total directories: $totalDirs"

# Optional: show file count by extension
Write-Host "`nFiles by type:"
Get-ChildItem -Path $Path -File -Recurse -ErrorAction SilentlyContinue |
    Group-Object -Property Extension |
    Sort-Object -Property Count -Descending |
    ForEach-Object { Write-Host "  $($_.Name): $($_.Count)" }

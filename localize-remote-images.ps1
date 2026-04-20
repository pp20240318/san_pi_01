$ErrorActionPreference = "Stop"

$root = "F:\2026Code\san_pi_01"
$siteDirs = Get-ChildItem -Path $root -Directory | Where-Object { $_.Name -like "Zz_*" }

if (-not $siteDirs) {
    Write-Host "No site directories matched Zz_* under $root"
    exit 0
}

function Get-SafeFileName([string]$url) {
    try {
        $uri = [Uri]$url
        $name = [IO.Path]::GetFileName($uri.AbsolutePath)
        if ([string]::IsNullOrWhiteSpace($name)) {
            $name = "img_" + [guid]::NewGuid().ToString("N") + ".bin"
        }
    } catch {
        $name = "img_" + [guid]::NewGuid().ToString("N") + ".bin"
    }

    return ($name -replace '[\\/:*?"<>|]', '_')
}

function Get-RelativePath([string]$fromPath, [string]$toPath) {
    $fromAbs = [IO.Path]::GetFullPath($fromPath)
    $toAbs = [IO.Path]::GetFullPath($toPath)

    $fromUri = New-Object System.Uri(($fromAbs.TrimEnd('\') + '\'))
    $toUri = New-Object System.Uri($toAbs)
    $relUri = $fromUri.MakeRelativeUri($toUri)
    $rel = [Uri]::UnescapeDataString($relUri.ToString())
    return ($rel -replace '/', '\')
}

$urlRegex = 'https?://[^\s"''<>()]+?\.(?:png|jpe?g|gif|webp|svg|ico)(?:\?[^\s"''<>()]*)?'
$targetExtRegex = '^\.(html?|css|js|json|xml|txt)$'

$globalDownloaded = 0
$globalReplacedFiles = 0

foreach ($site in $siteDirs) {
    Write-Host ""
    Write-Host "=== Processing $($site.Name) ==="

    $imgDir = Join-Path $site.FullName "assets\images"
    New-Item -ItemType Directory -Force -Path $imgDir | Out-Null

    $files = Get-ChildItem -Path $site.FullName -Recurse -File | Where-Object { $_.Extension -match $targetExtRegex }
    if (-not $files) {
        Write-Host "No target files found."
        continue
    }

    $urlMap = @{}
    $siteDownloaded = 0
    $siteUpdated = 0

    foreach ($file in $files) {
        $content = Get-Content -LiteralPath $file.FullName -Raw
        $matches = [regex]::Matches($content, $urlRegex) | ForEach-Object { $_.Value } | Select-Object -Unique

        foreach ($url in $matches) {
            if ($urlMap.ContainsKey($url)) { continue }

            try {
                $name = Get-SafeFileName $url
                $target = Join-Path $imgDir $name

                if (Test-Path -LiteralPath $target) {
                    $existingHash = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash
                    $urlMap[$url] = $target
                    continue
                }

                Invoke-WebRequest -Uri $url -OutFile $target -UseBasicParsing -TimeoutSec 45
                if ((Get-Item -LiteralPath $target).Length -eq 0) {
                    Remove-Item -LiteralPath $target -ErrorAction SilentlyContinue
                    continue
                }

                $urlMap[$url] = $target
                $siteDownloaded++
                Write-Host "Downloaded: $url -> $name"
            } catch {
                Write-Warning "Failed to download: $url"
            }
        }
    }

    foreach ($file in $files) {
        $content = Get-Content -LiteralPath $file.FullName -Raw
        $newContent = $content

        foreach ($url in $urlMap.Keys) {
            $localAbs = $urlMap[$url]
            $fileDir = Split-Path -Parent $file.FullName
            $relativeLocal = Get-RelativePath $fileDir $localAbs
            $relativeWeb = $relativeLocal -replace '\\', '/'
            $newContent = $newContent.Replace($url, $relativeWeb)
        }

        if ($newContent -ne $content) {
            Set-Content -LiteralPath $file.FullName -Value $newContent -NoNewline
            $siteUpdated++
            Write-Host "Updated refs: $($file.FullName)"
        }
    }

    $globalDownloaded += $siteDownloaded
    $globalReplacedFiles += $siteUpdated
    Write-Host "Site done. Downloaded: $siteDownloaded, Updated files: $siteUpdated"
}

Write-Host ""
Write-Host "All done. Total downloaded images: $globalDownloaded"
Write-Host "All done. Total updated files: $globalReplacedFiles"

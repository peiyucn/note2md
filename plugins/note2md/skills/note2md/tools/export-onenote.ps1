<#
.SYNOPSIS
  从 OneNote 桌面版导出所有笔记本为 XML 文件
.DESCRIPTION
  使用 OneNote COM API 遍历所有笔记本→分区→页面，导出为 XML。
  自动跳过回收站（OneNote_RecycleBin）。
.PARAMETER OutputDir
  导出目标目录，默认为脚本所在目录下的 ./onenote_export
.EXAMPLE
  .\export-onenote.ps1
  .\export-onenote.ps1 -OutputDir "D:\my_notes"
#>

param(
    [string]$OutputDir = "$PSScriptRoot\onenote_export"
)

$ErrorActionPreference = "Continue"
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$onenote = New-Object -ComObject OneNote.Application
$baseDir = $OutputDir

$hierXml = ""
$onenote.GetHierarchy("", 4, [ref]$hierXml)

$xmlDoc = [xml]$hierXml
$ns = New-Object Xml.XmlNamespaceManager($xmlDoc.NameTable)
$ns.AddNamespace("one", "http://schemas.microsoft.com/office/onenote/2013/onenote")

$notebooks = $xmlDoc.SelectNodes("//one:Notebook", $ns)
$totalPages = 0
$totalSections = 0
$skipped = 0
$failed = 0

foreach ($notebook in $notebooks) {
    $nbName = $notebook.GetAttribute("name")
    Write-Host "=== Notebook: $nbName ===" -ForegroundColor Cyan
    
    $sections = $notebook.SelectNodes("one:Section", $ns)
    foreach ($section in $sections) {
        $secName = $section.GetAttribute("name")
        
        # 跳过回收站（OneNote 系统目录，非用户内容）
        if ($section.GetAttribute("isRecycleBin") -eq "true" -or
            $section.GetAttribute("isInRecycleBin") -eq "true" -or
            $section.GetAttribute("isDeletedPages") -eq "true") {
            Write-Host "  Skip: $secName (recycle bin)" -ForegroundColor Gray
            continue
        }
        
        $secNameSafe = $secName -replace '[\\/:*?"<>|]', '_'
        $secPath = Join-Path $baseDir $nbName | Join-Path -ChildPath $secNameSafe
        
        if (-not (Test-Path $secPath)) {
            New-Item -ItemType Directory -Path $secPath -Force | Out-Null
        }
        
        Write-Host "  Section: $secName" -ForegroundColor Yellow
        $totalSections++
        
        $pages = $section.SelectNodes("one:Page", $ns)
        $pageCount = 0
        foreach ($page in $pages) {
            $pageId = $page.GetAttribute("ID")
            $pageName = $page.GetAttribute("name")
            $pageNameSafe = $pageName -replace '[\\/:*?"<>|]', '_'
            $pageFile = Join-Path $secPath "$pageNameSafe.xml"
            
            if (Test-Path $pageFile) {
                Write-Host "    Skip: $pageName (exists)" -ForegroundColor Gray
                $skipped++
                continue
            }
            
            try {
                $pageXml = ""
                $onenote.GetPageContent($pageId, [ref]$pageXml, 0)
                $prettyXml = '<?xml version="1.0" encoding="UTF-8"?>' + "`r`n" + $pageXml
                [System.IO.File]::WriteAllText($pageFile, $prettyXml, $utf8NoBom)
                Write-Host "    OK: $pageName" -ForegroundColor Green
                $pageCount++
                $totalPages++
                Start-Sleep -Milliseconds 150
            }
            catch {
                Write-Host "    FAIL: $pageName -- $_" -ForegroundColor Red
                $failed++
            }
        }
        Write-Host "    ($pageCount pages exported)" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "========== DONE ==========" -ForegroundColor Cyan
Write-Host "Notebooks: $($notebooks.Count)"
Write-Host "Sections:  $totalSections"
Write-Host "Exported:  $totalPages pages"
Write-Host "Skipped:   $skipped"
Write-Host "Failed:    $failed"

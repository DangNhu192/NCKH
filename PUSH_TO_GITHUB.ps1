# PUSH_TO_GITHUB.ps1
# Script tự động cập nhật và đẩy mã nguồn WEB SUPER lên GitHub (DangNhu192/NCKH)

param(
    [string]$CommitMessage = "fix(vercel): Hoan thien cau hinh vercel.json chong tai file .py va nang cap kien truc Static SPA"
)

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Set-Location -Path $PSScriptRoot
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   🚀 WEB SUPER - DONG BO VA DAY MA NGUON LEN GITHUB     " -ForegroundColor Cyan
Write-Host "   Repository: https://github.com/DangNhu192/NCKH         " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Tự động phát hiện vị trí git.exe
$gitCmd = $null
$possibleGitPaths = @(
    "git.exe",
    "C:\Users\User\AppData\Local\github-copilot-git-2.53.0-4\cmd\git.exe",
    "C:\Program Files\Git\cmd\git.exe",
    "C:\Program Files (x86)\Git\cmd\git.exe",
    "$env:LOCALAPPDATA\Programs\Git\cmd\git.exe",
    "$env:ProgramFiles\Git\cmd\git.exe"
)

foreach ($path in $possibleGitPaths) {
    if ($path -eq "git.exe") {
        $found = Get-Command "git.exe" -ErrorAction SilentlyContinue
        if ($found) {
            $gitCmd = "git.exe"
            break
        }
    } elseif (Test-Path $path) {
        $gitCmd = $path
        break
    }
}

if (-not $gitCmd) {
    Write-Host "[X] Loi: Khong tim thay git.exe tren he thong!" -ForegroundColor Red
    Write-Host "Vui long cai dat Git hoac them Git vao bien moi truong PATH." -ForegroundColor Yellow
    Read-Host "Nhan Enter de thoat..."
    exit 1
}

Write-Host "[*] Su dung Git tai: $gitCmd" -ForegroundColor Gray

# 2. Don dep tep desktop.ini gay loi ref trong .git (do Google Drive sinh ra)
if (Test-Path ".git") {
    $desktopInis = Get-ChildItem -Path ".git" -Filter "desktop.ini" -Recurse -Force -ErrorAction SilentlyContinue
    if ($desktopInis) {
        Write-Host "[*] Dang loai bo $desktopInis.Count tep desktop.ini sinh ngau nhien trong .git..." -ForegroundColor DarkYellow
        $desktopInis | Remove-Item -Force -ErrorAction SilentlyContinue
    }
}

# 3. Kiem tra trang thai Git
Write-Host "[*] Dang kiem tra cac tep tin da chinh sua..." -ForegroundColor Yellow
& $gitCmd status -s

# 4. Dua toan bo thay doi vao Stage
Write-Host "`n[*] Dang them tep tin vao Git Stage (git add .)..." -ForegroundColor Yellow
& $gitCmd add .

# 5. Commit neu co thay doi
& $gitCmd diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "[*] Dang tao Commit: '$CommitMessage'..." -ForegroundColor Yellow
    & $gitCmd commit -m $CommitMessage
} else {
    Write-Host "[i] Khong co tep moi can commit. Tiep tuc dong bo voi remote..." -ForegroundColor Cyan
}

# 6. Day code len GitHub
Write-Host "`n[*] Dang day du lieu len GitHub (origin main)..." -ForegroundColor Cyan
& $gitCmd push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n==========================================================" -ForegroundColor Green
    Write-Host "   DA CAP NHAT VA DAY CODE LEN GITHUB THANH CONG!        " -ForegroundColor Green
    Write-Host "==========================================================" -ForegroundColor Green
} else {
    Write-Host "`n[!] Qua trinh push gap loi (Exit code: $LASTEXITCODE)." -ForegroundColor Red
    Write-Host "Vui long kiem tra ket noi mang hoac quyen truy cap GitHub." -ForegroundColor Yellow
}

Write-Host ""
if (-not $env:CI) {
    Write-Host "Nhan Enter de dong cua so nay..." -ForegroundColor Gray
    Read-Host
}

@echo off
setlocal EnableExtensions
chcp 65001 >nul

cd /d "%~dp0"

set "ISS_FILE=%~1"
if not defined ISS_FILE (
    for /f "delims=" %%i in ('dir /b /a-d "*.iss" 2^>nul') do (
        if not defined ISS_FILE set "ISS_FILE=%%i"
    )
)

if not defined ISS_FILE (
    echo [ERROR] No .iss file found in:
    echo "%cd%"
    echo.
    echo [TIP] Put this batch file next to the .iss file, or pass the .iss path as the first argument.
    pause
    exit /b 1
)

if not exist "%ISS_FILE%" (
    echo [ERROR] .iss file not found:
    echo "%ISS_FILE%"
    echo.
    echo [TIP] Put this batch file next to the .iss file, or pass the .iss path as the first argument.
    pause
    exit /b 1
)

set "APP_VERSION="
for /f "usebackq delims=" %%i in (`powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; [Console]::OutputEncoding=[System.Text.UTF8Encoding]::new(); $projectRoot = Get-Location; $candidate = Get-ChildItem -LiteralPath $projectRoot -Recurse -File -Filter *.json | Where-Object { $_.FullName -match '[\\/]config[\\/]app[\\/]' } | Sort-Object @{Expression={($_.FullName -split '[\\/]').Count}; Descending=$true}, FullName | Select-Object -First 1; if (-not $candidate) { throw 'No config/app version JSON file found'; }; $version = (Get-Content -Raw -Encoding UTF8 -LiteralPath $candidate.FullName | ConvertFrom-Json).version; if ([string]::IsNullOrWhiteSpace($version)) { throw ('version field is empty: ' + $candidate.FullName); }; [Console]::WriteLine(([string]$version).Trim())"`) do (
    set "APP_VERSION=%%i"
)

if not defined APP_VERSION (
    echo [ERROR] Failed to read AppVersion from config/app JSON.
    echo [TIP] Check that the version JSON exists and its version field is not empty.
    pause
    exit /b 1
)

set "ISCC_PATH="

if defined INNO_SETUP_COMPILER (
    if exist "%INNO_SETUP_COMPILER%" (
        set "ISCC_PATH=%INNO_SETUP_COMPILER%"
    )
)

if not defined ISCC_PATH (
    for /f "delims=" %%i in ('where ISCC.exe 2^>nul') do (
        set "ISCC_PATH=%%i"
        goto :compiler_found
    )
)

if not defined ISCC_PATH (
    if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
        set "ISCC_PATH=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
    )
)

if not defined ISCC_PATH (
    if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" (
        set "ISCC_PATH=%ProgramFiles%\Inno Setup 6\ISCC.exe"
    )
)

if not defined ISCC_PATH (
    if exist "%ProgramFiles(x86)%\Inno Setup 5\ISCC.exe" (
        set "ISCC_PATH=%ProgramFiles(x86)%\Inno Setup 5\ISCC.exe"
    )
)

if not defined ISCC_PATH (
    if exist "%ProgramFiles%\Inno Setup 5\ISCC.exe" (
        set "ISCC_PATH=%ProgramFiles%\Inno Setup 5\ISCC.exe"
    )
)

:compiler_found
if not defined ISCC_PATH (
    echo [ERROR] ISCC.exe was not found.
    echo.
    echo You can fix this by doing one of the following:
    echo 1. Install Inno Setup
    echo 2. Add the ISCC.exe directory to PATH
    echo 3. Set the INNO_SETUP_COMPILER environment variable manually
    echo.
    echo Example:
    echo set "INNO_SETUP_COMPILER=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    echo.
    pause
    exit /b 1
)

echo [INFO] Compiler:
echo "%ISCC_PATH%"
echo.
echo [INFO] Script:
echo "%ISS_FILE%"
echo.
echo [INFO] AppVersion:
echo "%APP_VERSION%"
echo.
echo [START] Running Inno Setup Compiler...
echo.

"%ISCC_PATH%" "/DAppVersion=%APP_VERSION%" "%ISS_FILE%"
set "EXIT_CODE=%ERRORLEVEL%"

echo.
if not "%EXIT_CODE%"=="0" (
    echo [FAIL] Installer build failed. Exit code: %EXIT_CODE%
    pause
    exit /b %EXIT_CODE%
)

echo [DONE] Installer build succeeded.
pause
exit /b 0


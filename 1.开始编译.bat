@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "PYTHON_EXE=python"
set "BUILD_SCRIPT="

for /f "delims=" %%I in ('dir /b /a-d "windows*.py" 2^>nul') do (
    set "BUILD_SCRIPT=%%~fI"
    goto :found_script
)

echo [FAIL] Cannot find build script matching:
echo "windows*.py"
echo.
echo [HINT] Keep this batch file next to the Windows build script.
pause
exit /b 1

:found_script
echo [INFO] Build script:
echo "%BUILD_SCRIPT%"
echo.
echo [START] Running build script...
echo.

"%PYTHON_EXE%" "%BUILD_SCRIPT%"
set "EXITCODE=%ERRORLEVEL%"

if "%EXITCODE%"=="0" (
    echo.
    echo [DONE] Build completed.
) else (
    echo.
    echo [FAIL] Build failed. Exit code: %EXITCODE%
)

pause
exit /b %EXITCODE%

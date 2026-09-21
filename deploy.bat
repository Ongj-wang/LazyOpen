@echo off
setlocal

set "PROJECT_DIR=%~dp0"
pushd "%PROJECT_DIR%"

echo [1/4] Building lazyopen.exe...
uv run pyinstaller --onefile --name lazyopen --clean main.py
if errorlevel 1 (
    echo Build failed.
    popd
    exit /b 1
)

echo [2/4] Copying lazyopen.exe...
copy /y "dist\lazyopen.exe" "%PROJECT_DIR%lazyopen.exe" >nul
if errorlevel 1 (
    echo Copy failed.
    popd
    exit /b 1
)

echo [3/4] Removing build directories...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo [4/4] Adding the project directory to the user PATH...
set "LAZYOPEN_PROJECT_DIR=%PROJECT_DIR%"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$projectPath = [IO.Path]::GetFullPath($env:LAZYOPEN_PROJECT_DIR); $userPath = [Environment]::GetEnvironmentVariable('Path', 'User'); $entries = @($userPath -split ';' | Where-Object { $_ }); if ($entries -notcontains $projectPath) { [Environment]::SetEnvironmentVariable('Path', (($entries + $projectPath) -join ';'), 'User') }"
if errorlevel 1 (
    echo Failed to update the user PATH.
    popd
    exit /b 1
)

popd
echo Deployment complete. Open a new terminal for the updated PATH to take effect.
exit /b 0
@echo off
setlocal

set "PROJECT_DIR=%~dp0"
set "WINDOWS_DIR=%PROJECT_DIR%windows"
set "LAZYOPEN_COMMAND=%WINDOWS_DIR%\lazyopen.bat"
set "LAZYOPEN_COMPLETION=%WINDOWS_DIR%\AutoRegistration\lazyopen-completion.ps1"
pushd "%PROJECT_DIR%"

echo [1/3] Adding Windows launcher directory to user PATH...
set "LAZYOPEN_PROJECT_DIR=%WINDOWS_DIR%"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$projectPath = [IO.Path]::GetFullPath($env:LAZYOPEN_PROJECT_DIR); $legacyPath = [IO.Path]::GetFullPath((Join-Path $projectPath '..')); $userPath = [Environment]::GetEnvironmentVariable('Path', 'User'); $entries = @($userPath -split ';' | Where-Object { $_ -and ([IO.Path]::GetFullPath($_) -ne $legacyPath) -and ([IO.Path]::GetFullPath($_) -ne $projectPath) }); [Environment]::SetEnvironmentVariable('Path', (($entries + $projectPath) -join ';'), 'User')"
if errorlevel 1 (
    echo Failed to update the user PATH.
    popd
    exit /b 1
)

echo [2/3] Registering PowerShell tab completion...
set "LAZYOPEN_PROFILE=%USERPROFILE%\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"
set "LAZYOPEN_PROFILE7=%USERPROFILE%\Documents\PowerShell\Microsoft.PowerShell_profile.ps1"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$completionPath = [IO.Path]::GetFullPath($env:LAZYOPEN_COMPLETION); $line = '. ' + [char]34 + $completionPath + [char]34; foreach ($profilePath in @($env:LAZYOPEN_PROFILE, $env:LAZYOPEN_PROFILE7) | Select-Object -Unique) { $profileDir = Split-Path -Parent $profilePath; if (!(Test-Path $profileDir)) { New-Item -ItemType Directory -Path $profileDir -Force | Out-Null }; if (!(Test-Path $profilePath)) { New-Item -ItemType File -Path $profilePath -Force | Out-Null }; if (!(Select-String -LiteralPath $profilePath -SimpleMatch -Quiet $completionPath -ErrorAction SilentlyContinue)) { Add-Content -LiteralPath $profilePath -Value $line } }"
if errorlevel 1 (
    echo Failed to register PowerShell tab completion.
    popd
    exit /b 1
)

echo [3/3] Deployment ready.
popd
echo Deployment complete. Open a new PowerShell window for PATH and tab completion changes to take effect.
exit /b 0
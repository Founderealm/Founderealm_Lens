@echo off
rem Runs the Founderealm Lens binary built for this machine, fetching it once if needed: the
rem launcher beside this file, for Windows, which runs no shell script. .mcp.json names
rem server/lens, and Windows finds that name as this file.
rem
rem A local build in this directory wins, for development. Otherwise the binary comes from
rem the release named in RELEASE, and is run only if its SHA-256 matches the one written
rem in SHA256SUMS beside this file: the expected hash comes from the plugin as installed,
rem not from the place the binary is downloaded from. Stdout belongs to MCP, so every
rem message here goes to stderr. Git keeps this file's line endings CRLF (.gitattributes),
rem the only ones cmd.exe reads reliably.
setlocal EnableExtensions DisableDelayedExpansion

set "here=%~dp0"
set "issues=open an issue at https://github.com/Founderealm/Founderealm_Lens/issues."

if exist "%here%founderealm-lens.exe" endlocal & "%here%founderealm-lens.exe" %* & exit /b

rem The processor's own name, even when a 32-bit cmd.exe runs this.
set "arch=%PROCESSOR_ARCHITECTURE%"
if defined PROCESSOR_ARCHITEW6432 set "arch=%PROCESSOR_ARCHITEW6432%"
set "msg=no prebuilt binary for %arch%; %issues%"
if /i "%arch%"=="AMD64" set "arch=x86_64"
if /i "%arch%"=="ARM64" set "arch=arm64"
if not "%arch%"=="x86_64" if not "%arch%"=="arm64" goto fail
set "name=founderealm-lens-windows-%arch%.exe"

set "msg=this copy of the plugin names no release and holds no local build in %here:~0,-1%; update or reinstall the plugin."
if not exist "%here%RELEASE" goto fail
if not exist "%here%SHA256SUMS" goto fail
set "release="
for /f "usebackq tokens=1" %%R in ("%here%RELEASE") do if not defined release set "release=%%R"
set "want="
for /f "usebackq tokens=1,2" %%A in ("%here%SHA256SUMS") do (
    if "%%B"=="%name%" set "want=%%A"
    if "%%B"=="*%name%" set "want=%%A"
)
set "msg=release %release% has no binary for windows-%arch%."
if not defined want goto fail

rem The plugin's own data directory when Claude Code names one, else the user's local cache.
set "data=%FOUNDEREALM_LENS_DATA%"
if not defined data goto cache
rem A literal ${ means Claude Code passed the placeholder through unexpanded.
if "%data:${=%"=="%data%" goto data_known
:cache
set "data=%LOCALAPPDATA%\founderealm-lens"
:data_known
set "bin=%data%\%release%\%name%"

set "got="
if exist "%bin%" call :sha "%bin%"
if /i "%got%"=="%want%" goto run

if not exist "%data%\%release%" mkdir "%data%\%release%"
set "base=%FOUNDEREALM_LENS_BASE_URL%"
if not defined base set "base=https://github.com/Founderealm/Founderealm_Lens/releases/download/%release%"
set "part=%bin%.part.%RANDOM%"
>&2 echo founderealm-lens: fetching %name% from release %release%
set "msg=could not download %base%/%name%"
curl.exe -fsSL --retry 2 -o "%part%" "%base%/%name%" || goto fail
call :sha "%part%"
set "msg=SHA-256 of %name% is %got%, expected %want%. It was deleted and nothing was run."
if /i not "%got%"=="%want%" goto fail
set "msg=could not put %name% in %data%\%release%"
move /y "%part%" "%bin%" >nul || goto fail

:run
endlocal & "%bin%" %*
exit /b

rem Stops with the message in msg, leaving no partial download behind. The message is printed
rem by delayed expansion, so a path in it holding & or ^ prints as it is.
:fail
if defined part if exist "%part%" del "%part%"
setlocal EnableDelayedExpansion
>&2 echo founderealm-lens: !msg!
exit /b 1

rem The file's SHA-256 into got: certutil prints it on its second line, its bytes parted by
rem spaces on older Windows.
:sha
set "got="
for /f "skip=1 delims=" %%H in ('certutil -hashfile "%~1" SHA256') do if not defined got set "got=%%H"
if defined got set "got=%got: =%"
exit /b 0

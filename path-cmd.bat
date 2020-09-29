:: Usage:
::   call path-cmd script

:: %COMSPEC% executes script ONLY from the %PATH%
:: In order to %COMSPEC% execute script from CWD use: "%COMSPEC%" /c ".\script.bat"

@echo off
set "full_path="
set "all_but_first="

SETLOCAL
for /F "usebackq delims=" %%a in (`^^^"%WINDIR%\System32\where.exe^^^" $PATH:%1`) do (
    ENDLOCAL
    set "full_path=%%a"
    GOTO :break1
)

:break1
for /F "tokens=1,*" %%a in ("%*") do set "all_but_first=%%b"

call "%COMSPEC%" /c "%full_path%" %all_but_first%

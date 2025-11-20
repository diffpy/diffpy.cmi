@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM ---- temp workspace ----
set "TMPROOT=%TEMP%\remote_tests_%RANDOM%%RANDOM%"
md "%TMPROOT%" || (echo Failed to create TMPROOT & exit /b 1)

REM ---- resolve args -> URL list file ----
if "%~2"=="" (
  if exist "%~1" (
    set "URLS_FILE=%~f1"
  ) else (
    set "URLS_FILE=%TMPROOT%\urls.txt"
    > "%URLS_FILE%" echo %~1
  )
) else (
  set "URLS_FILE=%TMPROOT%\urls.txt"
  (for %%U in (%*) do @echo %%~U) > "%URLS_FILE%"
)

pushd "%TMPROOT%" >nul || (echo Failed to enter TMPROOT & exit /b 1)

set /a i=0
set /a overall_ec=0

for /f "usebackq delims=" %%L in ("%URLS_FILE%") do call :process_one "%%L"

popd >nul

REM -------- CLEANUP: do not poison exit code --------
rmdir /s /q "%TMPROOT%" >nul 2>&1
ver >nul   REM reset errorlevel to 0

REM ---- FINAL EXIT ----
exit /b %overall_ec%


REM ===================================================
:process_one
setlocal EnableExtensions EnableDelayedExpansion

set "url=%~1"
if "%url%"=="" (endlocal & goto :eof)

:trim
if not "%url:~0,1%"==" " goto :trim_done
set "url=%url:~1%"
goto trim
:trim_done

if "%url:~0,1%"=="#" (endlocal & goto :eof)

endlocal & set /a i+=1 & set "URL=%url%"

echo(
echo ==> [%i%] %URL%

set "PKGDIR=%TMPROOT%\pkg_%i%"
md "%PKGDIR%" >nul 2>&1
pushd "%PKGDIR%" >nul || goto :after

curl -L --fail -o "archive.tar.gz" "%URL%"
if errorlevel 1 (
  echo curl failed
  set /a overall_ec=1
  popd >nul & goto :after
)

tar -xzf "archive.tar.gz" >nul 2>&1
if errorlevel 1 tar -xf "archive.tar.gz" >nul 2>&1
if errorlevel 1 (
  echo tar extract failed
  set /a overall_ec=1
  popd >nul & goto :after
)

set "FIRST="
for /f "delims=" %%F in ('tar -tzf "archive.tar.gz" 2^>nul') do set "FIRST=%%F" & goto got_first
for /f "delims=" %%F in ('tar -tf  "archive.tar.gz" 2^>nul') do set "FIRST=%%F" & goto got_first
:got_first

set "PROJROOT=%CD%"
if defined FIRST for /f "tokens=1 delims=/" %%T in ("%FIRST%") do if exist ".\%%T\" set "PROJROOT=%CD%\%%T"

if exist "%PROJROOT%\src\" rmdir /s /q "%PROJROOT%\src" >nul 2>&1 & ver >nul

pushd "%PROJROOT%" >nul
echo Running pytest in "%CD%"

set "OLD_PYTHONPATH=%PYTHONPATH%"

if exist "tests\" (
  if defined OLD_PYTHONPATH (
    set "PYTHONPATH=%CD%;tests;%OLD_PYTHONPATH%"
  ) else (
    set "PYTHONPATH=%CD%;tests"
  )
) else (
  if defined OLD_PYTHONPATH (
    set "PYTHONPATH=%CD%;%OLD_PYTHONPATH%"
  ) else (
    set "PYTHONPATH=%CD%"
  )
)

pytest
if errorlevel 1 set /a overall_ec=1

set "PYTHONPATH=%OLD_PYTHONPATH%"
popd >nul

popd >nul

:after
REM cleanup without poisoning errorlevel
rmdir /s /q "%PKGDIR%" >nul 2>&1
ver >nul

goto :eof

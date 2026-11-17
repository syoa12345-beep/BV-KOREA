@echo off
chcp 65001 >nul
setlocal

cd /d "%~dp0"

echo.
echo ==========================================
echo BV_Korea EXE BUILD
echo ==========================================
echo.

echo Checking Python...
python --version
if errorlevel 1 goto NO_PYTHON

echo.
echo Checking PyInstaller...
python -m PyInstaller --version
if errorlevel 1 goto INSTALL_PYINSTALLER

goto FIND_FILE

:INSTALL_PYINSTALLER
echo.
echo PyInstaller not found.
echo Installing PyInstaller...
echo.
python -m pip install pyinstaller
if errorlevel 1 goto BUILD_ERROR

:FIND_FILE
set "PYFILE="

for %%F in (*.pyw) do (
    if not defined PYFILE set "PYFILE=%%F"
)

if not defined PYFILE (
    for %%F in (*.py) do (
        if not defined PYFILE set "PYFILE=%%F"
    )
)

if not defined PYFILE goto NO_FILE

echo.
echo Source file:
echo %PYFILE%
echo.

echo Starting EXE build...
echo.

if exist "app_icon.ico" (
    echo Icon found: app_icon.ico
    python -m PyInstaller --onefile --windowed --icon="app_icon.ico" --name "GitHUB_최초셋팅_자동업데이트" "%PYFILE%"
) else (
    echo No app_icon.ico found. Building with default icon...
    python -m PyInstaller --onefile --windowed --name "GitHUB_최초셋팅_자동업데이트" "%PYFILE%"
)

if errorlevel 1 goto BUILD_ERROR

echo.
echo ==========================================
echo BUILD COMPLETE
echo ==========================================
echo.
echo EXE:
echo %CD%\dist\GitHUB_최초셋팅_자동업데이트.exe
echo.

if exist "dist\GitHUB_최초셋팅_자동업데이트.exe" goto SUCCESS

echo WARNING: EXE was not found.
goto FINISH

:NO_PYTHON
echo.
echo ERROR: Python was not found.
goto FINISH

:NO_FILE
echo.
echo ERROR: No PY or PYW file was found in this folder.
goto FINISH

:BUILD_ERROR
echo.
echo ERROR: Build failed.
echo Check the messages above.
goto FINISH

:SUCCESS
echo EXE file created successfully.

:FINISH
echo.
echo Press any key to close this window.
pause >nul
endlocal

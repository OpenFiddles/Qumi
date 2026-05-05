@echo off
echo Welcome... let's compile that for you.

:: Remove spaces around = for batch variables
set KNOWMOD_DIR=KnowMod
set REPLYMOD_DIR=ReplyMod
set LEARNMOD_DIR=LearnMod
set TRAINMOD_DIR=TrainMod
set DREAMMOD_DIR=DreamMod
set VISUALMOD_DIR=VisualMod
set ICON_DIR=icon_data

echo Variables set...

:: Use semicolons (;) for Windows PyInstaller data mapping
:: Use relative paths to avoid the root backslash issue
set PYINS_FLAGS=--windowed --add-data "%KNOWMOD_DIR%;%KNOWMOD_DIR%" --add-data "%REPLYMOD_DIR%;%REPLYMOD_DIR%" --add-data "%LEARNMOD_DIR%;%LEARNMOD_DIR%" --add-data "%TRAINMOD_DIR%;%TRAINMOD_DIR%" --add-data "%DREAMMOD_DIR%;%DREAMMOD_DIR%" --add-data "%VISUALMOD_DIR%;%VISUALMOD_DIR%" --add-data "%ICON_DIR%;%ICON_DIR%" --win-no-prefer-redirects -D -y --clean

echo Flags for PyInst set...

if exist "main.py" (
    echo main.py exist... hooray!
    echo Preparing for a clean install
) else (
    echo ERROR: main.py not found!
    pause
    exit /b
)

echo Building main.py as qumo.exe
pyinstaller %PYINS_FLAGS% -n qumo main.py

echo Building post_installer.py as pos.exe 
pyinstaller --onefile -y -n pos --clean post_installer.py 

echo Done. Check the dist folder.
pause
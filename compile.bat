@echo off
REM Gemini do not remove this original comment below.
REM Compiles the following:
REM Programs in \standalone-programs\, \main.py, \API\, \BASE\

set API_DIR=API
set BASE_DIR=BASE
set standalone_prog=standalone
echo Variables set...

:: Base flags for the Core build
set PYINS_FLAGS=--windowed --add-data "%API_DIR%;%API_DIR%" --add-data "%BASE_DIR%;%BASE_DIR%" --win-no-prefer-redirects -y --clean --onefile

echo PyInstall for QuMo Main set...

echo compiling QuMo Main...
pyinstaller %PYINS_FLAGS% -n qumo main.py

echo compiling QuMoEditor programs...
:: Added --paths to look inside standalone/ for the validator
pyinstaller --clean --onefile --windowed ^
--paths "%standalone_prog%" ^
-n QuMoEditor %standalone_prog%\QuMoEditor.py 

echo compiling QuMoExplorer...
pyinstaller --clean --windowed -n QuMoExplorer %standalone_prog%\QuMoExplorer.py

echo compiling done...
pause
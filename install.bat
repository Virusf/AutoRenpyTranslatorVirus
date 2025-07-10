@echo off
echo Installation des dependances pour Auto Renpy Translator
echo.

echo Installation de Python (si necessaire)...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python n'est pas installe ou n'est pas dans le PATH
    echo Veuillez installer Python depuis https://www.python.org/downloads/
    echo N'oubliez pas de cocher "Add Python to PATH" lors de l'installation
    pause
    exit /b 1
)

echo Python detecte, installation des dependances...
pip install -r requirements.txt

echo.
echo Installation terminee !
echo Vous pouvez maintenant lancer AutoRenpyTranslator.bat
echo.
pause
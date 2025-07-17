@echo off

echo Auto Renpy Translator
echo.

@REM  Google Translate
@REM python AutoRenpyTranslator.py

@REM Personnaliser le nombre de threads
python AutoRenpyTranslator.py --max-workers 3

@REM  service libretranslate Translate
@REM python AutoRenpyTranslator.py --service libretranslate


pause
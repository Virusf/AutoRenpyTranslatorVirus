@echo off

echo Auto Renpy Translator
echo.

@REM  Google Translate
@REM python AutoRenpyTranslator.py

@REM  service libretranslate Translate
@REM python AutoRenpyTranslator.py --service libretranslate


@REM Personnaliser le nombre de threads
python AutoRenpyTranslator.py --service libretranslate --max-workers 3


pause
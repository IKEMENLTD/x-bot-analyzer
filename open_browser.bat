@echo off
chcp 65001 > nul

REM 現在のディレクトリのindex.htmlを取得
set CURRENT_DIR=%~dp0
set HTML_FILE=%CURRENT_DIR%index.html

echo ブラウザでツールを開いています...
start "" "%HTML_FILE%"

timeout /t 2 > nul

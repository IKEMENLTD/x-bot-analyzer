@echo off
chcp 65001 > nul
echo ================================
echo X アカウント分析ツール - 起動中
echo ================================
echo.

REM .envファイルから環境変数を読み込み
if exist .env (
    for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
        if not "%%a"=="" if not "%%a:~0,1%"=="#" (
            set %%a=%%b
        )
    )
    echo Claude API Key: 設定済み
) else (
    echo 警告: .envファイルが見つかりません
    echo AI分析機能は利用できません
)

echo.
echo サーバーを起動しています...
echo サーバーURL: http://localhost:5000
echo.
echo フロントエンドを開くには:
echo - index.html をダブルクリック
echo - または、ブラウザにドラッグ&ドロップ
echo.
echo サーバーを停止するには Ctrl+C を押してください
echo.
echo ================================
echo.

python server.py

pause

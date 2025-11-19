@echo off
chcp 65001 > nul
echo ================================
echo X アカウント分析ツール - セットアップ
echo ================================
echo.

echo [1/3] Python依存パッケージをインストール中...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo エラー: パッケージのインストールに失敗しました
    echo Pythonがインストールされているか確認してください
    pause
    exit /b 1
)

echo.
echo [2/3] ChromeDriverのセットアップ中...
python -c "from selenium import webdriver; from selenium.webdriver.chrome.service import Service; from webdriver_manager.chrome import ChromeDriverManager; driver = webdriver.Chrome(service=Service(ChromeDriverManager().install())); driver.quit(); print('ChromeDriver: OK')"
if errorlevel 1 (
    echo.
    echo 警告: ChromeDriverのセットアップに失敗しました
    echo Google Chromeがインストールされているか確認してください
)

echo.
echo [3/3] 設定ファイルを確認中...
if not exist .env (
    echo .envファイルが見つかりません
    echo .env.exampleを参考に作成してください
    echo.
    echo Claude API Keyを設定する場合:
    echo 1. .env.exampleをコピーして.envにリネーム
    echo 2. CLAUDE_API_KEY=your_api_key_here を実際のAPIキーに変更
) else (
    echo .envファイル: OK
)

echo.
echo ================================
echo セットアップ完了！
echo ================================
echo.
echo 次のステップ:
echo 1. start.bat を実行してサーバーを起動
echo 2. ブラウザで index.html を開く
echo.
pause

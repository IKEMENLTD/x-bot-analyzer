# X アカウント分析ツール - 人間 or BOT 判定

XアカウントのURLを入力すると、そのアカウントが人間によって運用されているか、BOTによって運用されているかを自動判定する無料ツールです。

## 🚀 機能

- **自動スクレイピング**: XアカウントURLを入力するだけで、過去の投稿を自動収集
- **AI分析**: Claude AIを使った高精度な文章分析
- **多角的判定**: 以下の4つの観点で分析
  - 投稿パターン（時間の規則性）
  - 文章の自然さ
  - コミュニケーション性
  - 感情表現の豊かさ
- **視覚的な結果表示**: わかりやすいスコアと詳細分析結果

## 📋 必要なもの

### 1. Python 3.8以上

### 2. Google Chrome

スクレイピングにSeleniumを使用するため、Google Chromeがインストールされている必要があります。

### 3. Claude API Key（オプション）

AI分析機能を使用する場合は、AnthropicのClaude APIキーが必要です。

- APIキーの取得: https://console.anthropic.com/
- 無料枠あり（月間$5相当）

※ APIキーなしでもルールベース分析のみで動作します

## 🔧 セットアップ手順

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. ChromeDriverのインストール

以下のいずれかの方法でChromeDriverをインストールします：

#### 方法A: 自動インストール（推奨）

Pythonで以下を実行：

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.quit()
```

#### 方法B: 手動インストール

1. ChromeDriverをダウンロード: https://chromedriver.chromium.org/
2. Chromeのバージョンに合ったものを選択
3. パスを通すか、`scraper.py`でパスを指定

### 3. Claude API Keyの設定（オプション）

環境変数にAPIキーを設定：

**Windows (コマンドプロンプト):**
```cmd
set CLAUDE_API_KEY=your_api_key_here
```

**Windows (PowerShell):**
```powershell
$env:CLAUDE_API_KEY="your_api_key_here"
```

**Mac/Linux:**
```bash
export CLAUDE_API_KEY=your_api_key_here
```

または、`.env`ファイルを作成：
```
CLAUDE_API_KEY=your_api_key_here
```

## 🎮 使い方

### 1. バックエンドサーバーの起動

```bash
python server.py
```

サーバーが `http://localhost:5000` で起動します。

### 2. フロントエンドの表示

`index.html` をブラウザで開きます：

- ダブルクリックで開く
- または、ブラウザにドラッグ&ドロップ

### 3. アカウントの分析

1. XアカウントのURLを入力（例: `https://x.com/username`）
2. 「分析開始」ボタンをクリック
3. 結果が表示されるまで待機（30秒〜1分程度）

## 📊 判定方法

### ルールベース分析（基本機能）

1. **投稿パターン分析**
   - 投稿時間の規則性をチェック
   - 深夜・早朝の投稿頻度を確認
   - 変動係数(CV)で人間らしさを測定

2. **文章の自然さ**
   - 投稿の多様性を測定
   - URL/ハッシュタグの割合をチェック
   - テキスト長のばらつきを分析

3. **コミュニケーション性**
   - @メンションの頻度
   - 返信・質問形式の投稿
   - 対話的なやり取りの有無

4. **感情表現**
   - 絵文字・顔文字の使用
   - 感情語の豊かさ
   - 表現の多様性

### AI分析（Claude API使用時）

- 文章の自然さを深く理解
- 文脈の一貫性をチェック
- 人間らしい思考パターンを検出
- BOT特有の定型文を識別

最終スコアは、これらの分析結果を総合して0〜100%で表示されます。

## 🔍 スコアの見方

- **80%以上**: ほぼ確実に人間
- **60〜80%**: 人間の可能性が高い
- **40〜60%**: 判定が難しい
- **20〜40%**: BOTの可能性が高い
- **20%未満**: ほぼ確実にBOT

## ⚠️ 注意事項

### スクレイピングについて

- このツールはSeleniumを使ってX（Twitter）から公開情報を取得します
- 大量のリクエストを送るとアカウントがブロックされる可能性があります
- 個人利用・研究目的でのみ使用してください
- 商用利用は避けてください

### 判定精度について

- 判定結果は参考値であり、100%の精度を保証するものではありません
- 新しいアカウントや投稿数が少ない場合、精度が低下します
- BOTでも人間らしい投稿をするものは検出が困難です

### プライバシー

- このツールはローカルで動作し、分析データは外部に送信されません
- Claude APIを使用する場合のみ、投稿テキストがAnthropicに送信されます

## 🛠️ トラブルシューティング

### エラー: "ChromeDriver not found"

→ ChromeDriverが正しくインストールされているか確認してください

### エラー: "Failed to scrape account"

→ 以下を確認：
- アカウントが存在するか
- アカウントが公開設定か
- ネットワーク接続が安定しているか

### エラー: "AI分析は利用できません"

→ CLAUDE_API_KEY環境変数が設定されているか確認してください

### バックエンドに接続できない

→ `server.py`が起動しているか確認してください

## 📝 ライセンス

このツールは個人利用・研究目的で自由に使用できます。

## 🤝 貢献

改善提案やバグ報告は歓迎します！

## 📧 お問い合わせ

問題が発生した場合は、READMEのトラブルシューティングを参照してください。

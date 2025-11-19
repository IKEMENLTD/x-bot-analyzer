# 🚀 デプロイ手順（完全無料）

このツールを完全無料でインターネット上に公開する手順です。

## 📋 構成

- **フロントエンド**: Vercel（無料）
- **バックエンド**: Render（無料プラン）
- **合計費用**: 完全無料 🎉

## 🔧 事前準備

### 1. GitHubアカウントの作成

まだない場合は https://github.com で作成してください。

### 2. GitHubリポジトリの作成

1. GitHubにログイン
2. 「New repository」をクリック
3. リポジトリ名: `x-bot-analyzer`（任意）
4. Public を選択
5. 「Create repository」をクリック

### 3. コードをGitHubにプッシュ

このプロジェクトフォルダで以下を実行：

```bash
# Gitの初期化
git init

# ファイルを追加
git add .

# コミット
git commit -m "Initial commit"

# GitHubリポジトリと連携（URLは自分のリポジトリに変更）
git remote add origin https://github.com/YOUR_USERNAME/x-bot-analyzer.git

# プッシュ
git branch -M main
git push -u origin main
```

---

## 🎨 Part 1: バックエンドのデプロイ（Render）

### ステップ 1: Renderアカウント作成

1. https://render.com にアクセス
2. 「Get Started」をクリック
3. GitHubアカウントで Sign up

### ステップ 2: Web Serviceを作成

1. Renderダッシュボードで「New +」→「Web Service」をクリック
2. GitHubリポジトリを接続
3. 先ほど作成した `x-bot-analyzer` リポジトリを選択

### ステップ 3: 設定

以下のように設定：

- **Name**: `x-bot-analyzer-api`（任意）
- **Region**: Oregon（デフォルト）
- **Branch**: `main`
- **Root Directory**: （空白）
- **Runtime**: `Python 3`
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn server:app`
- **Instance Type**: `Free`

### ステップ 4: 環境変数を設定

「Environment」タブで以下を追加：

- **Key**: `CLAUDE_API_KEY`
- **Value**: あなたのClaude APIキー（https://console.anthropic.com/ から取得）

※ APIキーなしでもルールベース分析は動作します

### ステップ 5: デプロイ

「Create Web Service」をクリック

→ デプロイが開始されます（5〜10分程度かかります）

### ステップ 6: URLを確認

デプロイが完了すると、URLが表示されます：

例: `https://x-bot-analyzer-api.onrender.com`

**このURLをメモしておいてください！**

---

## 🖼️ Part 2: フロントエンドのデプロイ（Vercel）

### ステップ 1: script.jsのAPI URLを更新

`script.js` の1行目を編集：

```javascript
// 変更前
const API_URL = 'http://localhost:5000';

// 変更後（RenderのURLに置き換え）
const API_URL = 'https://x-bot-analyzer-api.onrender.com';
```

変更したら、GitHubにプッシュ：

```bash
git add script.js
git commit -m "Update API URL for production"
git push
```

### ステップ 2: Vercelアカウント作成

1. https://vercel.com にアクセス
2. 「Sign Up」をクリック
3. GitHubアカウントで Sign up

### ステップ 3: プロジェクトをデプロイ

1. Vercelダッシュボードで「Add New...」→「Project」をクリック
2. GitHubリポジトリを接続
3. `x-bot-analyzer` リポジトリを選択
4. 設定はデフォルトのまま「Deploy」をクリック

### ステップ 4: デプロイ完了

デプロイが完了すると、URLが表示されます：

例: `https://x-bot-analyzer.vercel.app`

**これがあなたのツールの公開URLです！** 🎉

---

## 🎯 完成！

これで、以下の2つのURLが利用可能になります：

- **フロントエンド**: `https://x-bot-analyzer.vercel.app`
- **バックエンドAPI**: `https://x-bot-analyzer-api.onrender.com`

誰でもフロントエンドのURLにアクセスして、ツールを使えます！

---

## ⚙️ 追加設定（オプション）

### カスタムドメインの設定

Vercelでは無料でカスタムドメインを設定できます：

1. Vercelのプロジェクト設定 →「Domains」
2. ドメインを入力して設定

### 環境変数の変更

RenderやVercelのダッシュボードから、いつでも環境変数を変更できます。

Claude APIキーを変更する場合：
1. Renderダッシュボード →「Environment」
2. `CLAUDE_API_KEY` を編集
3. 自動的に再デプロイされます

---

## 🔍 動作確認

1. フロントエンドURL（Vercel）にアクセス
2. XアカウントURLを入力（例: `https://x.com/elonmusk`）
3. 分析開始ボタンをクリック
4. 結果が表示されればOK！

### 初回アクセスが遅い場合

Renderの無料プランは、15分間アクセスがないとスリープします。
初回アクセス時は起動に30秒〜1分程度かかりますが、正常です。

アクティブに保つには：
- 定期的にアクセスする
- または、UptimeRobot等のサービスで5分ごとにpingする

---

## 📝 更新方法

コードを変更した場合：

```bash
git add .
git commit -m "Update: 変更内容"
git push
```

→ VercelとRenderが自動的に再デプロイします！

---

## ❌ トラブルシューティング

### Renderのビルドが失敗する

→ `build.sh` に実行権限があるか確認：

```bash
chmod +x build.sh
git add build.sh
git commit -m "Add execute permission to build.sh"
git push
```

### 「CORS error」が出る

→ `server.py` で `CORS(app)` が設定されているか確認

### ChromeDriverエラー

→ Renderのログを確認して、ChromeDriverが正しくインストールされているか確認

### API通信エラー

→ `script.js` のAPI URLが正しいか確認（Renderの実際のURLと一致しているか）

---

## 💰 費用について

### 完全無料プランの制限

**Render（無料プラン）:**
- 750時間/月（常時起動可能）
- 15分間アクセスがないとスリープ
- スペック: 512MB RAM、0.1 CPU

**Vercel（無料プラン）:**
- 帯域幅: 100GB/月
- ビルド時間: 100時間/月
- 十分な容量です

### 有料プランへのアップグレード（オプション）

より高速・安定したサービスが必要な場合：

- **Render Starter**: $7/月（スリープなし、より高速）
- **Vercel Pro**: $20/月（より多くの帯域幅）

---

## 🎉 おめでとうございます！

これで、完全無料でXアカウント分析ツールが公開されました！

URLをSNSで共有して、みんなに使ってもらいましょう！

---

## 📞 サポート

問題が発生した場合は、GitHubのIssuesで報告してください。

// 本番環境用の設定ファイルサンプル
// デプロイ後に script.js の API_URL を以下のように変更してください

// 例: RenderのURLが https://x-bot-analyzer-api.onrender.com の場合
const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000'
    : 'https://x-bot-analyzer-api.onrender.com';

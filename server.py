from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from scraper import TwitterScraper
from analyzer import BotAnalyzer

app = Flask(__name__)

# CORS設定：すべてのオリジンからのアクセスを許可
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type"],
        "max_age": 3600
    }
})

# AI API Keyの設定（Geminiを優先）
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY', '')

# どちらかのAPIキーを使用（Geminiを優先）
API_KEY = GEMINI_API_KEY or CLAUDE_API_KEY

scraper = TwitterScraper()
analyzer = BotAnalyzer(API_KEY)

@app.route('/')
def index():
    return jsonify({
        'status': 'running',
        'message': 'X Account Bot Analyzer API is running'
    })

@app.route('/analyze', methods=['POST'])
def analyze_account():
    """
    XアカウントURLを受け取り、BOT判定結果を返す
    """
    try:
        data = request.json
        account_url = data.get('url', '')

        if not account_url:
            return jsonify({'error': 'URLが指定されていません'}), 400

        # URLからユーザー名を抽出
        username = extract_username(account_url)
        if not username:
            return jsonify({'error': '有効なアカウントURLではありません'}), 400

        print(f'[INFO] Analyzing account: @{username}')

        # 1. アカウント情報と投稿を取得
        print('[INFO] Scraping tweets...')
        account_data = scraper.scrape_account(username)

        if not account_data or not account_data.get('tweets'):
            return jsonify({
                'error': '投稿データを取得できませんでした。アカウントが存在しないか、非公開の可能性があります。'
            }), 404

        print(f'[INFO] Found {len(account_data["tweets"])} tweets')

        # 2. AI分析実行
        print('[INFO] Analyzing with AI...')
        analysis_result = analyzer.analyze_tweets(
            account_data['tweets'],
            account_data.get('account_info', {})
        )

        # 3. 結果を返す
        response = {
            'account': account_data.get('account_info', {}),
            'tweets': account_data['tweets'][:10],  # 最初の10件のみ返す
            'analysis': analysis_result
        }

        print(f'[INFO] Analysis complete. Score: {analysis_result["overall_score"]}%')
        return jsonify(response)

    except Exception as e:
        print(f'[ERROR] {str(e)}')
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'分析中にエラーが発生しました: {str(e)}'
        }), 500

def extract_username(url):
    """
    URLからユーザー名を抽出
    """
    import re
    patterns = [
        r'https?://(www\.)?(twitter\.com|x\.com)/([a-zA-Z0-9_]+)',
        r'@?([a-zA-Z0-9_]+)$'
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(match.lastindex)

    return None

@app.route('/health', methods=['GET'])
def health_check():
    """
    ヘルスチェック用エンドポイント
    """
    return jsonify({
        'status': 'healthy',
        'scraper': scraper.is_ready(),
        'analyzer': analyzer.is_ready()
    })

if __name__ == '__main__':
    print('='*60)
    print('X Account Bot Analyzer API Server')
    print('='*60)

    if GEMINI_API_KEY:
        print('[INFO] Gemini API Key: OK (優先)')
    elif CLAUDE_API_KEY:
        print('[INFO] Claude API Key: OK')
    else:
        print('[WARNING] API Key が設定されていません')
        print('[WARNING] GEMINI_API_KEY (推奨・無料) または CLAUDE_API_KEY を設定してください')
        print('[WARNING] AI分析機能はルールベースのみで動作します')

    print('[INFO] Starting server on http://localhost:5000')
    print('='*60)

    app.run(debug=True, host='0.0.0.0', port=5000)

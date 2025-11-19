import os
from datetime import datetime
import statistics
import re

# AI APIクライアント
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class BotAnalyzer:
    def __init__(self, api_key=None, api_type='auto'):
        """
        APIキーとタイプを指定してアナライザーを初期化

        api_type: 'gemini', 'claude', 'auto'（自動検出）
        """
        self.api_key = api_key
        self.api_type = api_type
        self.client = None

        if not api_key:
            print('[ANALYZER] No API key provided. Rule-based analysis only.')
            return

        # API自動検出
        if api_type == 'auto':
            # Geminiを優先（無料なので）
            if GEMINI_AVAILABLE:
                self.api_type = 'gemini'
            elif ANTHROPIC_AVAILABLE:
                self.api_type = 'claude'
            else:
                print('[ANALYZER] No AI libraries available.')
                return

        # クライアント初期化
        if self.api_type == 'gemini' and GEMINI_AVAILABLE:
            try:
                genai.configure(api_key=api_key)
                self.client = genai.GenerativeModel('gemini-1.5-flash')
                print('[ANALYZER] Using Google Gemini API')
            except Exception as e:
                print(f'[ANALYZER] Gemini initialization error: {e}')

        elif self.api_type == 'claude' and ANTHROPIC_AVAILABLE:
            try:
                self.client = anthropic.Anthropic(api_key=api_key)
                print('[ANALYZER] Using Claude API')
            except Exception as e:
                print(f'[ANALYZER] Claude initialization error: {e}')

    def analyze_tweets(self, tweets, account_info=None):
        """
        投稿データを分析してBOTスコアを算出
        """
        if not tweets:
            return self._create_error_result('投稿データがありません')

        # 1. ルールベース分析
        pattern_score = self._analyze_posting_pattern(tweets)
        text_score = self._analyze_text_naturalness(tweets)
        comm_score = self._analyze_communication(tweets)
        emotion_score = self._analyze_emotion_expression(tweets)

        # 2. AI分析（APIが利用可能な場合）
        ai_summary = ''
        ai_score_adjustment = 0

        if self.client:
            ai_result = self._ai_deep_analysis(tweets, account_info)
            ai_summary = ai_result['summary']
            ai_score_adjustment = ai_result['score_adjustment']
        else:
            ai_summary = 'AI分析は利用できません。GEMINI_API_KEY または CLAUDE_API_KEY 環境変数を設定してください。'

        # 3. 総合スコア計算
        base_score = (
            pattern_score * 0.25 +
            text_score * 0.30 +
            comm_score * 0.25 +
            emotion_score * 0.20
        )

        # AI調整を加える
        overall_score = max(0, min(100, base_score + ai_score_adjustment))

        return {
            'overall_score': round(overall_score, 1),
            'detailed_scores': {
                'posting_pattern': round(pattern_score, 1),
                'text_naturalness': round(text_score, 1),
                'communication': round(comm_score, 1),
                'emotion_expression': round(emotion_score, 1)
            },
            'details': {
                'posting_pattern': self._get_pattern_description(pattern_score),
                'text_naturalness': self._get_text_description(text_score),
                'communication': self._get_comm_description(comm_score),
                'emotion_expression': self._get_emotion_description(emotion_score)
            },
            'ai_summary': ai_summary
        }

    def _analyze_posting_pattern(self, tweets):
        """
        投稿パターンを分析（時間間隔の規則性）
        """
        if len(tweets) < 2:
            return 50

        try:
            # 投稿時間間隔を計算
            intervals = []
            for i in range(len(tweets) - 1):
                time1 = datetime.fromisoformat(tweets[i]['date'].replace('Z', '+00:00'))
                time2 = datetime.fromisoformat(tweets[i+1]['date'].replace('Z', '+00:00'))
                interval = abs((time1 - time2).total_seconds() / 3600)  # 時間単位
                intervals.append(interval)

            # 標準偏差を計算（低いほどBOTっぽい）
            if len(intervals) > 1:
                std_dev = statistics.stdev(intervals)
                mean_interval = statistics.mean(intervals)

                # 変動係数（CV）を計算
                if mean_interval > 0:
                    cv = std_dev / mean_interval
                    # CVが高いほど人間らしい（0.5以上で高スコア）
                    score = min(100, cv * 150)
                else:
                    score = 50
            else:
                score = 50

            # 深夜・早朝投稿をチェック（人間は睡眠時間に投稿が少ない）
            night_posts = 0
            for tweet in tweets:
                time = datetime.fromisoformat(tweet['date'].replace('Z', '+00:00'))
                hour = time.hour
                if 2 <= hour <= 6:  # 深夜2時〜6時
                    night_posts += 1

            night_ratio = night_posts / len(tweets)
            if night_ratio > 0.3:  # 30%以上が深夜投稿ならBOTの可能性
                score -= 20

            return max(0, min(100, score))

        except Exception as e:
            print(f'[ANALYZER] Pattern analysis error: {e}')
            return 50

    def _analyze_text_naturalness(self, tweets):
        """
        文章の自然さを分析
        """
        try:
            texts = [t['text'] for t in tweets if t['text']]
            if not texts:
                return 50

            # 1. 文字列の類似度をチェック
            unique_ratio = len(set(texts)) / len(texts)
            similarity_score = unique_ratio * 100

            # 2. テキストの多様性をチェック
            avg_length = statistics.mean([len(t) for t in texts])
            length_std = statistics.stdev([len(t) for t in texts]) if len(texts) > 1 else 0

            # 長さのばらつきが大きいほど人間らしい
            diversity_score = min(100, (length_std / avg_length * 100) if avg_length > 0 else 0)

            # 3. URL/ハッシュタグの割合
            url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            hashtag_pattern = r'#\w+'

            url_count = sum([len(re.findall(url_pattern, t)) for t in texts])
            hashtag_count = sum([len(re.findall(hashtag_pattern, t)) for t in texts])

            # URL/ハッシュタグが多すぎるとBOTっぽい
            promo_ratio = (url_count + hashtag_count) / len(texts)
            promo_score = max(0, 100 - promo_ratio * 30)

            # 総合
            score = (similarity_score * 0.4 + diversity_score * 0.4 + promo_score * 0.2)
            return max(0, min(100, score))

        except Exception as e:
            print(f'[ANALYZER] Text analysis error: {e}')
            return 50

    def _analyze_communication(self, tweets):
        """
        コミュニケーション性を分析（返信・引用・リツイートなど）
        """
        try:
            texts = [t['text'] for t in tweets]

            # @メンションの数
            mention_count = sum([t.count('@') for t in texts])

            # 質問形式の投稿
            question_count = sum([1 for t in texts if '?' in t or '？' in t])

            # 返信っぽい投稿（文頭が@から始まる）
            reply_count = sum([1 for t in texts if t.strip().startswith('@')])

            # 会話性が高いほど人間らしい
            comm_ratio = (mention_count + question_count + reply_count) / len(tweets)
            score = min(100, comm_ratio * 100)

            # 独り言っぽい投稿も人間らしい
            soliloquy_patterns = ['今日', 'なう', '行って', '食べ', '見て', 'わかる', 'と思う']
            soliloquy_count = sum([1 for t in texts if any(p in t for p in soliloquy_patterns)])
            soliloquy_score = min(50, (soliloquy_count / len(tweets)) * 100)

            return max(0, min(100, score * 0.7 + soliloquy_score * 0.3))

        except Exception as e:
            print(f'[ANALYZER] Communication analysis error: {e}')
            return 50

    def _analyze_emotion_expression(self, tweets):
        """
        感情表現の多様性を分析
        """
        try:
            texts = [t['text'] for t in tweets]

            # 絵文字・顔文字
            emoji_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]'
            kaomoji_pattern = r'[（\(][^）\)]*[笑泣涙汗喜怒哀楽][^）\)]*[）\)]|[＾^][_＿][＾^]|[oO0][_＿][oO0]'

            emoji_count = sum([len(re.findall(emoji_pattern, t)) for t in texts])
            kaomoji_count = sum([len(re.findall(kaomoji_pattern, t)) for t in texts])

            # 感情語
            emotion_words = ['嬉しい', '悲しい', '楽しい', 'つらい', '面白い', 'すごい', 'やばい',
                           '最高', '最悪', '好き', '嫌い', 'ありがとう', 'ごめん', 'うれしい']
            emotion_count = sum([sum([1 for word in emotion_words if word in t]) for t in texts])

            # 感嘆詞
            exclamation_count = sum([t.count('!') + t.count('！') for t in texts])

            total_emotion = emoji_count + kaomoji_count + emotion_count + exclamation_count
            emotion_ratio = total_emotion / len(tweets)

            score = min(100, emotion_ratio * 30)

            # 感情表現の種類が多様かチェック
            has_emoji = emoji_count > 0
            has_kaomoji = kaomoji_count > 0
            has_emotion_words = emotion_count > 0
            diversity_bonus = (has_emoji + has_kaomoji + has_emotion_words) * 10

            return max(0, min(100, score + diversity_bonus))

        except Exception as e:
            print(f'[ANALYZER] Emotion analysis error: {e}')
            return 50

    def _ai_deep_analysis(self, tweets, account_info):
        """
        AI APIを使った高度な分析（Gemini または Claude）
        """
        if not self.client:
            return {'summary': 'AI分析は利用できません', 'score_adjustment': 0}

        try:
            # 投稿サンプルを準備（最新20件）
            sample_tweets = tweets[:20]
            tweet_texts = '\n'.join([f"- {t['text']}" for t in sample_tweets])

            prompt = f"""以下のX（Twitter）アカウントの投稿を分析し、このアカウントが人間によって運用されているか、BOTによって運用されているかを判定してください。

アカウント情報:
- 名前: {account_info.get('name', 'Unknown') if account_info else 'Unknown'}
- ユーザー名: @{account_info.get('username', 'unknown') if account_info else 'unknown'}

投稿サンプル（最新20件）:
{tweet_texts}

以下の観点で分析してください：
1. 文章の自然さ・人間らしさ
2. 話題の多様性・一貫性
3. 感情表現の豊かさ
4. コミュニケーションの質
5. BOT特有のパターンの有無

分析結果を以下の形式で出力してください：
- 総評（2-3文）
- スコア調整値（-20〜+20の範囲で、人間らしいほどプラス、BOTらしいほどマイナス）

出力形式：
総評: [ここに総評]
スコア調整: [数値のみ]"""

            # APIタイプに応じて呼び出し
            if self.api_type == 'gemini':
                response = self.client.generate_content(prompt)
                response_text = response.text

            elif self.api_type == 'claude':
                message = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )
                response_text = message.content[0].text

            else:
                return {'summary': 'サポートされていないAPI', 'score_adjustment': 0}

            # レスポンスをパース
            summary_match = re.search(r'総評[：:]\s*(.+?)(?=スコア調整|$)', response_text, re.DOTALL)
            score_match = re.search(r'スコア調整[：:]\s*([-+]?\d+)', response_text)

            summary = summary_match.group(1).strip() if summary_match else response_text
            score_adjustment = int(score_match.group(1)) if score_match else 0

            # スコア調整を-20〜+20に制限
            score_adjustment = max(-20, min(20, score_adjustment))

            return {
                'summary': summary,
                'score_adjustment': score_adjustment
            }

        except Exception as e:
            print(f'[ANALYZER] AI analysis error: {e}')
            import traceback
            traceback.print_exc()
            return {
                'summary': f'AI分析でエラーが発生しました: {str(e)}',
                'score_adjustment': 0
            }

    def _get_pattern_description(self, score):
        if score >= 70:
            return '投稿時間が不規則で、人間の生活パターンに合致しています。'
        elif score >= 40:
            return '投稿時間にやや規則性が見られますが、許容範囲内です。'
        else:
            return '投稿時間が非常に規則的で、BOTの可能性があります。'

    def _get_text_description(self, score):
        if score >= 70:
            return '文章が多様で自然です。人間らしい表現が見られます。'
        elif score >= 40:
            return '文章にやや類似性が見られますが、許容範囲内です。'
        else:
            return '文章が定型的で、BOTによる自動投稿の可能性があります。'

    def _get_comm_description(self, score):
        if score >= 70:
            return '活発なコミュニケーションが見られます。人間らしい対話が確認できます。'
        elif score >= 40:
            return 'コミュニケーションは適度に見られます。'
        else:
            return 'コミュニケーションが少なく、一方的な投稿が多いです。'

    def _get_emotion_description(self, score):
        if score >= 70:
            return '豊かな感情表現が見られます。人間らしい感情の起伏が確認できます。'
        elif score >= 40:
            return '感情表現は適度に見られます。'
        else:
            return '感情表現が乏しく、機械的な印象を受けます。'

    def _create_error_result(self, message):
        return {
            'overall_score': 0,
            'detailed_scores': {
                'posting_pattern': 0,
                'text_naturalness': 0,
                'communication': 0,
                'emotion_expression': 0
            },
            'details': {
                'posting_pattern': message,
                'text_naturalness': message,
                'communication': message,
                'emotion_expression': message
            },
            'ai_summary': message
        }

    def is_ready(self):
        """
        アナライザーが使用可能かチェック
        """
        return self.client is not None

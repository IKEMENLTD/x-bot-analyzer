from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import json
from datetime import datetime

class TwitterScraper:
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None

    def init_driver(self):
        """
        Chromeドライバーを初期化
        """
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument('--headless')

        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # ChromeDriverのパスを指定（必要に応じて）
        # service = Service('path/to/chromedriver')
        # self.driver = webdriver.Chrome(service=service, options=chrome_options)

        self.driver = webdriver.Chrome(options=chrome_options)

    def scrape_account(self, username, max_tweets=50):
        """
        指定されたユーザーの投稿を取得
        """
        if not self.driver:
            self.init_driver()

        try:
            # Xアカウントページにアクセス
            url = f'https://x.com/{username}'
            print(f'[SCRAPER] Accessing: {url}')
            self.driver.get(url)

            # ページ読み込み待機（延長）
            print('[SCRAPER] Waiting for page to load...')
            time.sleep(5)

            # ログイン画面が表示されているかチェック
            try:
                login_button = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'ログイン') or contains(text(), 'Log in')]")
                if login_button:
                    print('[SCRAPER WARNING] Login page detected. Twitter may require authentication.')
                    # それでも試してみる
            except:
                pass

            # ページソースのデバッグ出力
            print('[SCRAPER] Page title:', self.driver.title)

            # アカウント情報を取得
            account_info = self._extract_account_info()

            # 投稿を取得
            tweets = self._extract_tweets(max_tweets)

            return {
                'account_info': account_info,
                'tweets': tweets
            }

        except Exception as e:
            print(f'[SCRAPER ERROR] {str(e)}')
            import traceback
            traceback.print_exc()
            raise
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None

    def _extract_account_info(self):
        """
        アカウント情報を抽出
        """
        try:
            # プロフィール画像
            try:
                profile_img = self.driver.find_element(By.CSS_SELECTOR, 'img[alt*="profile"]').get_attribute('src')
            except:
                profile_img = None

            # 表示名
            try:
                name = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="UserName"] span').text
            except:
                name = 'Unknown'

            # ユーザー名
            try:
                username_elem = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="UserName"]')
                username = username_elem.text.split('\n')[1] if '\n' in username_elem.text else 'unknown'
                username = username.replace('@', '')
            except:
                username = 'unknown'

            return {
                'name': name,
                'username': username,
                'profile_image': profile_img
            }

        except Exception as e:
            print(f'[SCRAPER] Error extracting account info: {e}')
            return {}

    def _extract_tweets(self, max_tweets=50):
        """
        投稿を抽出
        """
        tweets = []
        last_height = 0
        scroll_attempts = 0
        max_scroll_attempts = 20

        print(f'[SCRAPER] Starting tweet extraction (max: {max_tweets})...')

        # 最初のツイートが読み込まれるまで待機
        try:
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'article')))
            print('[SCRAPER] First article element detected')
        except Exception as e:
            print(f'[SCRAPER WARNING] Timeout waiting for articles: {e}')

        while len(tweets) < max_tweets and scroll_attempts < max_scroll_attempts:
            try:
                # ツイート要素を取得（複数のセレクタを試す）
                tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')

                if not tweet_elements:
                    # 代替セレクタを試す
                    tweet_elements = self.driver.find_elements(By.TAG_NAME, 'article')
                    print(f'[SCRAPER] Using fallback selector, found {len(tweet_elements)} articles')
                else:
                    print(f'[SCRAPER] Found {len(tweet_elements)} tweet elements with data-testid')

                for idx, elem in enumerate(tweet_elements):
                    if len(tweets) >= max_tweets:
                        break

                    try:
                        # ツイートテキスト（複数のセレクタを試す）
                        text = None
                        try:
                            text_elem = elem.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]')
                            text = text_elem.text
                        except:
                            # 代替セレクタ
                            try:
                                text_elem = elem.find_element(By.CSS_SELECTOR, 'div[lang]')
                                text = text_elem.text
                            except:
                                pass

                        if not text:
                            continue

                        # 投稿日時
                        try:
                            time_elem = elem.find_element(By.TAG_NAME, 'time')
                            date = time_elem.get_attribute('datetime')
                        except:
                            date = datetime.now().isoformat()

                        # 重複チェック
                        if not any(t['text'] == text for t in tweets):
                            tweets.append({
                                'text': text,
                                'date': date
                            })
                            print(f'[SCRAPER] Tweet #{len(tweets)}: {text[:50]}...')

                    except Exception as e:
                        print(f'[SCRAPER] Error extracting tweet #{idx}: {e}')
                        continue

                # スクロール
                self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                time.sleep(3)  # スクロール待機を延長

                new_height = self.driver.execute_script('return document.body.scrollHeight')
                if new_height == last_height:
                    scroll_attempts += 1
                    print(f'[SCRAPER] No new content after scroll (attempt {scroll_attempts}/{max_scroll_attempts})')
                else:
                    scroll_attempts = 0
                last_height = new_height

                print(f'[SCRAPER] Progress: {len(tweets)}/{max_tweets} tweets collected')

            except Exception as e:
                print(f'[SCRAPER] Error during scrolling: {e}')
                import traceback
                traceback.print_exc()
                break

        print(f'[SCRAPER] Total tweets collected: {len(tweets)}')
        return tweets

    def is_ready(self):
        """
        スクレイパーが使用可能かチェック
        """
        try:
            # Chromeドライバーが利用可能かテスト
            test_driver = webdriver.Chrome(options=Options())
            test_driver.quit()
            return True
        except:
            return False

    def __del__(self):
        """
        デストラクタ：ドライバーをクリーンアップ
        """
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

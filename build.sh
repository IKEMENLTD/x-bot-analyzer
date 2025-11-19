#!/usr/bin/env bash
# Render.com用ビルドスクリプト

set -e

echo "========================================="
echo "Installing Python dependencies..."
echo "========================================="
pip install -r requirements.txt

echo ""
echo "========================================="
echo "Installing Chrome and ChromeDriver..."
echo "========================================="

# Google Chromeのインストール
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
apt-get update
apt-get install -y google-chrome-stable

# ChromeDriverのインストール
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+')
echo "Chrome version: $CHROME_VERSION"

CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION%%.*}")
echo "ChromeDriver version: $CHROMEDRIVER_VERSION"

wget -q "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
unzip chromedriver_linux64.zip
chmod +x chromedriver
mv chromedriver /usr/local/bin/chromedriver
rm chromedriver_linux64.zip

echo ""
echo "========================================="
echo "Build complete!"
echo "========================================="

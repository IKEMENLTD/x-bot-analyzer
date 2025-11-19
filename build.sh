#!/usr/bin/env bash
# Render.com用ビルドスクリプト（シンプル版）

set -e

echo "========================================="
echo "Installing Python dependencies..."
echo "========================================="
pip install -r requirements.txt

echo ""
echo "========================================="
echo "Build complete!"
echo "========================================="
echo ""
echo "Note: Selenium features may not work on Render free tier."
echo "AI analysis with Gemini API will work fine."

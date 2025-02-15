#!/bin/bash

# デバッグ用ログ出力
exec 2> /tmp/error_log.txt  # 標準エラーをログに記録

which python3
which pip3
python3 --version
pip3 --version

echo "🐍 Current directory: $(pwd)"
ls -l $(pwd)

echo "🐍 Running start.sh" > /tmp/debug_log.txt
pwd >> /tmp/debug_log.txt
ls -l /app/ >> /tmp/debug_log.txt
ls -l /opt/render/project/go/src/github.com/gengorous/mastodon-rss-bot/ >> /tmp/debug_log.txt
echo "PATH: $PATH" >> /tmp/debug_log.txt
which bash >> /tmp/debug_log.txt
ls -l $(which bash) >> /tmp/debug_log.txt

echo "🔧 GCS 認証情報をセットアップ中..."
python3 setup_gcs_credentials.py

# 仮想環境 (`venv`) の確認＆セットアップ
if [ ! -d "venv" ]; then
    echo "⚠ 仮想環境が見つかりません！作成します..."
    python3 -m venv venv
    source venv/bin/activate
    pip3 install -r requirements.txt
else
    echo "🐍 仮想環境をアクティブ化..."
    source venv/bin/activate
fi

echo "🚀 アプリケーションを起動中..."
python3 r-mstdn.py

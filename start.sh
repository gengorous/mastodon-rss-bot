#!/bin/bash

echo "🔧 GCS 認証情報をセットアップ中..."
python setup_gcs_credentials.py

# 仮想環境 (`venv`) があれば有効化、なければスキップ
if [ -d "venv" ]; then
    echo "🐍 仮想環境をアクティブ化..."
    source venv/bin/activate
else
    echo "⚠ 仮想環境は見つかりませんでした。システムの Python を使用します。"
fi

echo "🚀 アプリケーションを起動中..."
python r-mstdn.py

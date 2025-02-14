#!/bin/bash

echo "🔧 GCS 認証情報をセットアップ中..."
python setup_gcs_credentials.py

# 仮想環境 (`venv`) の確認＆セットアップ
if [ ! -d "venv" ]; then
    echo "⚠ 仮想環境が見つかりません！作成します..."
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "🐍 仮想環境をアクティブ化..."
    source venv/bin/activate
fi

echo "🚀 アプリケーションを起動中..."
python r-mstdn.py

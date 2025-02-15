#!/bin/bash

# デバッグ用ログ出力
exec 2> /tmp/error_log.txt  # 標準エラーをログに記録

echo "🐍 Current directory: $(pwd)" > /tmp/debug_log.txt
ls -l $(pwd) >> /tmp/debug_log.txt

echo "🐍 PATH: $PATH" >> /tmp/debug_log.txt
which python3 >> /tmp/debug_log.txt
python3 --version >> /tmp/debug_log.txt
pip3 --version >> /tmp/debug_log.txt

echo "🐍 環境変数" >> /tmp/debug_log.txt
env >> /tmp/debug_log.txt

echo "🔧 GCS 認証情報をセットアップ中..."
python3 setup_gcs_credentials.py

# 仮想環境 (`venv`) の確認＆セットアップ
if [ ! -d "/opt/render/project/src/venv" ]; then
    echo "⚠ 仮想環境が見つかりません！作成します..."
    python3 -m venv /opt/render/project/src/venv
    source /opt/render/project/src/venv/bin/activate
    pip3 install -r /opt/render/project/src/requirements.txt
else
    echo "🐍 仮想環境をアクティブ化..."
    source /opt/render/project/src/venv/bin/activate
fi

# Flask サーバーを `waitress` で起動（バックグラウンドで実行）
echo "🚀 Flask サーバーを起動中..."
python -m waitress --listen=0.0.0.0:8080 --threads=1 mastdon:app &

# `r-mstdn.py` を実行
echo "🚀 r-mstdn.py を起動中..."
python3 r-mstdn.py


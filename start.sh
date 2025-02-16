#!/bin/bash

# デバッグ用ログ出力
exec 2> /opt/render/project/src/error_log.txt  # エラーログも保存

echo "🐍 Current directory: $(pwd)" > /opt/render/project/src/debug_log.txt
ls -l $(pwd) >> /opt/render/project/src/debug_log.txt

echo "🐍 PATH: $PATH" >> /opt/render/project/src/debug_log.txt
which python3 >> /opt/render/project/src/debug_log.txt
python3 --version >> /opt/render/project/src/debug_log.txt
pip3 --version >> /opt/render/project/src/debug_log.txt

echo "🐍 環境変数" >> /opt/render/project/src/debug_log.txt
env >> /opt/render/project/src/debug_log.txt


echo "🔧 GCS 認証情報をセットアップ中..."
python3 setup_gcs_credentials.py

# 仮想環境 (`venv`) の確認＆セットアップ
if [ ! -d "/opt/render/project/src/venv" ]; then
    echo "⚠ 仮想環境が見つかりません！作成します..."
    python3 -m venv /opt/render/project/src/venv
    source /opt/render/project/go/src/github.com/gengorous/mastodon-rss-bot/venv/bin/activate
    pip3 install -r /opt/render/project/src/requirements.txt
else
    echo "🐍 仮想環境をアクティブ化..."
    source /opt/render/project/go/src/github.com/gengorous/mastodon-rss-bot/venv/bin/activate
fi

echo "🐍 Python 実行ファイル: $(which python3)"
python3 --version
pip list | grep google

# Flask サーバーをバックグラウンドで起動
echo "🚀 Flask サーバーを起動中..."
python -m waitress --listen=0.0.0.0:8080 --threads=1 mastdon:app &

# `r-mstdn.py` を非同期で実行（バックグラウンド実行に変更）
echo "🚀 r-mstdn.py を起動中..."
python3 r-mstdn.py &

# 全てのバックグラウンドジョブを待機
wait
echo "🛑 全プロセスが終了しました。"

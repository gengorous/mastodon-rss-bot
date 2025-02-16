#!/bin/bash

# ログファイルの設定
DEBUG_LOG="/opt/render/project/go/src/debug_log.txt"
ERROR_LOG="/opt/render/project/go/src/error_log.txt"

# エラーログも保存
exec 2>> $ERROR_LOG  

echo "🐍 Current directory: $(pwd)" > $DEBUG_LOG
ls -l $(pwd) >> $DEBUG_LOG

echo "🐍 PATH: $PATH" >> $DEBUG_LOG
which python3 >> $DEBUG_LOG
python3 --version >> $DEBUG_LOG
pip3 --version >> $DEBUG_LOG

echo "🐍 環境変数" >> $DEBUG_LOG
env >> $DEBUG_LOG

echo "🔧 GCS 認証情報をセットアップ中..."
python3 setup_gcs_credentials.py

# 仮想環境 (`venv`) の確認＆セットアップ
if [ ! -d "/opt/render/project/go/src/venv" ]; then
    echo "⚠ 仮想環境が見つかりません！作成します..."
    python3 -m venv /opt/render/project/go/src/venv
    source /opt/render/project/go/src/github.com/gengorous/mastodon-rss-bot/venv/bin/activate
    pip3 install -r /opt/render/project/go/src/requirements.txt
else
    echo "🐍 仮想環境をアクティブ化..."
    source /opt/render/project/go/src/github.com/gengorous/mastodon-rss-bot/venv/bin/activate
fi

echo "🐍 Python 実行ファイル: $(which python3)" | tee -a $DEBUG_LOG
python3 --version | tee -a $DEBUG_LOG
pip list | grep google | tee -a $DEBUG_LOG

# Flask サーバーをバックグラウンドで起動しログを記録
echo "🚀 Flask サーバーを起動中..." | tee -a $DEBUG_LOG
python -m waitress --listen=0.0.0.0:8080 --threads=1 mastdon:app >> $DEBUG_LOG 2>> $ERROR_LOG &

# `r-mstdn.py` をバックグラウンドで実行しログを記録
echo "🚀 r-mstdn.py を起動中..." | tee -a $DEBUG_LOG
python3 r-mstdn.py >> $DEBUG_LOG 2>> $ERROR_LOG &

# 全てのバックグラウンドジョブを待機
wait
echo "🛑 全プロセスが終了しました。" | tee -a $DEBUG_LOG


#!/bin/bash

echo "🔧 GCS 認証情報をセットアップ中..."
python setup_gcs_credentials.py

echo "🚀 アプリケーションを起動中..."
python r-mstdn.py

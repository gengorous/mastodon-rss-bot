# ベースイメージ
FROM python:3.11

# 環境変数設定（UTF-8対応）
ENV PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8

# 作業ディレクトリを作成
WORKDIR /app

# 必要ファイルをコピー
COPY requirements.txt ./  
COPY mastdon.py ./  
COPY mastdon.json ./  
COPY key.json /app/key.json


# 依存ライブラリをインストール
RUN pip install --no-cache-dir -r requirements.txt

# Gunicorn で Flask アプリを起動
CMD ["python", "-m", "waitress", "--listen=0.0.0.0:8080", "--threads=1", "mastdon:app"]



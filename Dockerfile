# ベースイメージ
FROM python:3.11

# 作業ディレクトリを設定
WORKDIR /app

# 必要なファイルをコンテナ内にコピー

COPY . /app/
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh
RUN ls -l /app/

# start.sh に実行権限を付与
RUN python -m venv /app/venv && \
    /app/venv/bin/pip install -r /app/requirements.txt

# コンテナ起動時に start.sh を実行
CMD ["/bin/sh"]


# 必要ファイルをコピー
COPY requirements.txt /app/requirements.txt 
COPY r-mstdn.py /app/  
COPY mastdon.json ./  
COPY key.json /app/key.json

# 依存ライブラリをインストール
RUN pip install --no-cache-dir -r requirements.txt

# Gunicorn で Flask アプリを起動
CMD ["python", "-m", "waitress", "--listen=0.0.0.0:8080", "--threads=1", "mastdon:app"]



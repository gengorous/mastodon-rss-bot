# ベースイメージ
FROM python:3.11

# 作業ディレクトリを正しいパスに設定
WORKDIR /opt/render/project/go/src/github.com/gengorous/mastodon-rss-bot

# 依存ファイルを先にコピーしてキャッシュを活用
COPY requirements.txt /opt/render/project/src/requirements.txt

# 仮想環境を作成し、必要なライブラリをインストール
RUN python -m venv /opt/render/project/src/venv && \
    /opt/render/project/src/venv/bin/pip install --no-cache-dir -r /opt/render/project/src/requirements.txt
    
# 必要なファイルをコンテナ内にコピー
COPY . /opt/render/project/src/

# start.sh に実行権限を付与
RUN python -m venv /app/venv && \
    /app/venv/bin/pip install -r /app/requirements.txt

# start.sh に実行権限を付与
RUN chmod +x /opt/render/project/src/start.sh

# 必要ファイルをコピー
COPY requirements.txt /opt/render/project/src/requirements.txt
COPY r-mstdn.py /app/  
COPY mastdon.json ./  
COPY service-account.json /etc/secrets/service-account.json
ENV GOOGLE_APPLICATION_CREDENTIALS="/etc/secrets/service-account.json"


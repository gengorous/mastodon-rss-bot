# ベースイメージ
FROM python:3.11

# 作業ディレクトリを設定
WORKDIR /opt/render/project/go/src/github.com/gengorous/mastodon-rss-bot

# `requirements.txt` を先にコピーしてキャッシュを活用
COPY requirements.txt /opt/render/project/go/src/requirements.txt

# 仮想環境を作成 & 必要なライブラリをインストール
RUN python -m venv venv && \
    venv/bin/pip install --upgrade pip && \
    venv/bin/pip install --no-cache-dir -r requirements.txt

# `venv` をデフォルトの `python3` & `pip3` に設定
ENV PATH="/opt/render/project/go/src/venv/bin:$PATH"

# すべてのファイルをコンテナにコピー
COPY . . 


# `start.sh` に実行権限を付与
RUN chmod +x start.sh

# GCS の認証情報をセット
COPY service-account.json /etc/secrets/service-account.json
ENV GOOGLE_APPLICATION_CREDENTIALS="/etc/secrets/service-account.json"

# コンテナ起動時のコマンド
CMD ["/bin/bash", "/opt/render/project/go/src/github.com/gengorous/mastodon-rss-bot/start.sh"]


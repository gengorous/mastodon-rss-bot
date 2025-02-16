import json
import feedparser
import requests
import os
import logging
from bs4 import BeautifulSoup 
from google.cloud import storage
from google.oauth2 import service_account
import base64

# ログの設定
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# GCS 認証情報のロード
GCS_CREDENTIALS = os.getenv("GCS_CREDENTIALS")

if not GCS_CREDENTIALS:
    logging.error("❌ GCS_CREDENTIALS が設定されていません")
    credentials = None
else:
    try:
        decoded_credentials = base64.b64decode(GCS_CREDENTIALS).decode("utf-8")
        credentials_info = json.loads(decoded_credentials)
        credentials = service_account.Credentials.from_service_account_info(credentials_info)
        logging.info("✅ GCS 認証情報を正常にロードしました")
    except json.JSONDecodeError:
        logging.error("❌ GCS_CREDENTIALS のデコードに失敗しました（JSON 形式が壊れている可能性）")
        credentials = None
    except base64.binascii.Error:
        logging.error("❌ GCS_CREDENTIALS の Base64 デコードに失敗しました（データが壊れている可能性）")
        credentials = None
    except Exception as e:
        logging.error(f"❌ GCS 認証情報の読み込みエラー: {str(e)}")
        credentials = None

# GCS クライアントの作成
if credentials:
    try:
        client = storage.Client(credentials=credentials)
        logging.info("✅ GCS クライアントを正常に初期化しました")
    except Exception as e:
        logging.error(f"❌ GCS クライアントの初期化に失敗しました: {str(e)}")
        client = None
else:
    logging.error("❌ GCS クライアントの初期化に失敗しました（認証情報がありません）")
    client = None


# 環境変数から設定を取得
MASTODON_API_BASE = os.getenv("MASTODON_API_BASE", "https://mstdn.jp")  # マストドンのインスタンスURL
print(f"🔍 現在の MASTODON_API_BASE: {MASTODON_API_BASE}")

# 設定ファイルを読み込む
with open("mastdon.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# 記事の投稿管理

logging.basicConfig(level=logging.DEBUG)


from google.cloud import storage

# GCS の設定
BUCKET_NAME = "mastdon-project"
FILE_NAME = "posted_articles.json"

# 🛠 GCS に投稿済み記事を保存・取得する関数
from google.cloud import exceptions  # 追加

def load_posted_articles():
    """Cloud Storage から投稿済み記事リストを読み込む"""
    try:
        if not BUCKET_NAME:
            raise ValueError("❌ `BUCKET_NAME` が設定されていません！")

        print(f"🔍 GCS から `{FILE_NAME}` を読み込みます...")

        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(FILE_NAME)

        if blob.exists():  # ファイルが存在する場合のみ処理
            data = blob.download_as_text()
            print(f"✅ GCS から取得した `posted_articles.json`: {data}")  # 🔍 デバッグ用
            return json.loads(data)
        else:
            print(f"⚠ GCS にファイルが存在しません: {FILE_NAME}")
            return []  # 空のリストを返す
    except Exception as e:
        print(f"❌ GCS 読み込みエラー: {str(e)}")  # 🔍 デバッグ用
        return []  # エラー時も空リストを返す



def save_posted_articles(posted_articles):
    """Cloud Storage に投稿済み記事リストを保存"""
    try:
        print(f"📝 GCS に保存: {posted_articles}")  # ← 追加
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(FILE_NAME)
        blob.upload_from_string(json.dumps(posted_articles, ensure_ascii=False), content_type="application/json")
        logging.info("✅ 投稿履歴を GCS に保存しました")
    except Exception as e:
        logging.error(f"❌ GCS 書き込みエラー: {str(e)}")



from urllib.parse import urlparse, urlunparse

def normalize_url(url):
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))  # クエリやフラグメントを削除

def check_and_update_posted_articles(article_url):
    posted_articles = load_posted_articles()

    # URLを正規化
    normalized_url = normalize_url(article_url)
    print(f"🔍 正規化されたURL: {normalized_url}")

    if normalized_url in posted_articles:
        print(f"🟡 既に投稿済み: {normalized_url} → スキップ")
        return False  # 既に投稿済み

    # 新しい記事を記録
    print(f"📝 新しい記事を追加: {normalized_url}")  # ← 追加
    posted_articles.append(normalized_url)
    save_posted_articles(posted_articles)
    return True  # 投稿OK

def extract_image_url(entry):
    """記事の説明やサマリーから画像URLを抽出"""
    content = getattr(entry, "description", None) or getattr(entry, "summary", None)
    
    if content:
        soup = BeautifulSoup(content, "html.parser")
        img_tag = soup.find("img")
        
        if img_tag and "src" in img_tag.attrs:
            return img_tag["src"]

    return None  # 画像が見つからない場合
    
from PIL import Image
import io

def resize_image(image_data, max_width=1280, max_height=1280):
    """画像を指定した最大幅・高さにリサイズ"""
    with Image.open(io.BytesIO(image_data)) as img:
        img.thumbnail((max_width, max_height))
        output = io.BytesIO()
        img.save(output, format="JPEG")
        return output.getvalue()


def fetch_latest_entry(feed_url):
    """RSSフィードから最新のエントリを取得"""
    feed = feedparser.parse(feed_url)
    if feed.entries:
        entry = feed.entries[0]  # 最新の投稿
        image_url = None

        # 画像URLを探す（RSSの仕様によって色々試す）
        if "media_content" in entry and len(entry.media_content) > 0:
            image_url = entry.media_content[0]['url']
        elif "enclosures" in entry and len(entry.enclosures) > 0:
            image_url = entry.enclosures[0]['href']
        else:
            image_url = extract_image_url(entry)  # ここで `extract_image_url()` を使う

        # 取得した画像URLをログに出す
        if image_url:
            print(f"🖼 画像URL: {image_url}")
        else:
            print("⚠ 画像URLが見つかりませんでした")

        return entry, image_url
    return None, None


def upload_media(image_url, token):
    """マストドンに画像をアップロードしてメディアIDを取得"""
    if not image_url:
        print("⚠ 画像URLが見つからないためスキップ")
        return None  # 画像なしで投稿

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Referer": "https://mstdn.jp/"
        }
        response = requests.get(image_url, headers=headers)  

        print(f"🔍 HTTPレスポンスコード: {response.status_code}")  
        print(f"🔍 レスポンスヘッダー: {response.headers}")  
        print(f"🔍 画像データサイズ: {len(response.content)} バイト")  

        if response.status_code != 200:
            print(f"⚠ 画像取得エラー: HTTP {response.status_code}")
            return None
        
        img_data = response.content

        # 画像データの先頭数バイトを表示して、本当にJPEGか確認
        print(f"🔍 画像データ（先頭20バイト）: {img_data[:20]}")

        if not img_data or len(img_data) == 0:
            print("❌ 画像データが空！")
            return None

        files = {'file': ('image.jpg', img_data, 'image/jpeg')}
        headers = {"Authorization": f"Bearer {token}"}

        response = requests.post(f"{MASTODON_API_BASE}/api/v2/media", headers=headers, files=files)

        print(f"🔍 マストドンアップロードレスポンスコード: {response.status_code}")  
        print(f"🔍 マストドンレスポンス内容: {response.text}")  
        print(f"🔍 Mastodon 投稿データ: {response.json()}")  # 正しくレスポンスの JSON を表示

        if response.status_code == 200:
            media_id = response.json().get("id")
            print("✅ 画像アップロード成功:", media_id)
            return media_id
        else:
            print("❌ 画像アップロード失敗:", response.status_code, response.text)
            print("📝 エラーレスポンス内容:", response.text)
            return None
    except Exception as e:
        print("❌ 画像取得エラー:", e)
        return None




def post_to_mastodon(status, mastodon_url, token, media_id=None):
    """マストドンに投稿（BOTのルールに従い「未収載」で投稿）"""
    headers = {
    "Authorization": f"Bearer {token}",
    "User-Agent": "curl/8.10.1",  # `curl` の User-Agent をそのまま使う！
    "Accept": "application/json",  # JSON レスポンスを要求
    "Content-Type": "multipart/form-data",  # `curl` で使われた `Content-Type` に合わせる
}

    data = {
        "status": status,
        "visibility": "unlisted"  # ✅ 未収載にすることでフォロワーには見える
    }
    if media_id:
        data["media_ids[]"] = [media_id]  # 画像を添付

    # 🔍 ここでURLを確認！
    print(f"🔍 送信する Mastodon API URL: {mastodon_url}")

    response = requests.post(
        mastodon_url,
        headers=headers,
        data=data,
        allow_redirects=False,  # リダイレクトを防ぐ
        verify=True 
    )

    print(f"🔍 マストドン投稿レスポンスコード: {response.status_code}")
    print(f"🔍 レスポンスヘッダー: {response.headers}")
    print(f"🔍 マストドン投稿レスポンス内容: {response.text}")

    if response.status_code == 200:
        print("✅ 投稿成功:", status)
    else:
        print("❌ 投稿失敗:", response.status_code)
        print("📝 マストドンのエラーメッセージ:", response.text)



# `image_url` は `fetch_latest_entry()` で取得される
def main():
    for site in config["sites"]:
        print(f"処理中: {site['name']}")

        entry, image_url = fetch_latest_entry(site["rss_url"])  # ここで `image_url` を取得

        if entry:
            print(f"🔍 記事URL: {entry.link}")

            # 投稿済みチェック
            is_new = check_and_update_posted_articles(entry.link)
            print(f"🔄 投稿済みチェック結果: {is_new}")  # 🔍 デバッグ用

            if not is_new:
                print(f"⏩ 既に投稿済みの記事をスキップ: {entry.link}")
                continue  # 投稿済みならスキップ

            # 画像がある場合のみ取得＆リサイズ処理を実行
            resized_image_data = None
            if image_url:
                response = requests.get(image_url)
                if response.status_code == 200:
                    resized_image_data = resize_image(response.content)

            # 新しい記事の投稿
            status = f"{site['title']}\n{entry.title}\n{entry.link}"
            media_id = None
            if resized_image_data:
                media_id = upload_media(image_url, site["mastodon_token"])  # 画像アップロード
            post_to_mastodon(status, site["mastodon_url"], site["mastodon_token"], media_id)




if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Unhandled error: {e}")
    finally:
        exit(0)  # 必ず正常終了コードを返す

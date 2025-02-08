import json
import feedparser
import requests
import os
from bs4 import BeautifulSoup  # BeautifulSoupのインポートを追加

# 設定ファイルを読み込む
with open("mastdon.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# 環境変数から設定を取得
MASTODON_API_BASE = os.getenv("MASTODON_API_BASE", "https://mstdn.jp")  # マストドンのインスタンスURL
print(f"🔍 現在の MASTODON_API_BASE: {MASTODON_API_BASE}")

# 記事の投稿管理
def load_posted_articles():
    """投稿済み記事のリストをファイルから読み込む"""
    try:
        with open("posted_articles.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []  # ファイルがない場合は空リストを返す

def save_posted_articles(posted_articles):
    """投稿済み記事のリストをファイルに保存する"""
    with open("posted_articles.json", "w", encoding="utf-8") as f:
        json.dump(posted_articles, f, ensure_ascii=False, indent=2)

def check_and_update_posted_articles(article_url):
    """記事の URL が投稿済みか確認し、新規なら記録"""
    posted_articles = load_posted_articles()
    
    if article_url in posted_articles:
        print(f"🟡 既に投稿済みの記事: {article_url} → スキップ")
        return False  # 既に投稿済み

    posted_articles.append(article_url)
    save_posted_articles(posted_articles)
    return True  # 投稿 OK

def extract_image_url(entry):
    """記事の説明やサマリーから画像URLを抽出"""
    content = getattr(entry, "description", None) or getattr(entry, "summary", None)
    
    if content:
        soup = BeautifulSoup(content, "html.parser")
        img_tag = soup.find("img")
        
        if img_tag and "src" in img_tag.attrs:
            return img_tag["src"]

    return None  # 画像が見つからない場合

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
        verify=False 
    )

    print(f"🔍 マストドン投稿レスポンスコード: {response.status_code}")
    print(f"🔍 レスポンスヘッダー: {response.headers}")
    print(f"🔍 マストドン投稿レスポンス内容: {response.text}")

    if response.status_code == 200:
        print("✅ 投稿成功:", status)
    else:
        print("❌ 投稿失敗:", response.status_code)
        print("📝 マストドンのエラーメッセージ:", response.text)



def main():
    for site in config["sites"]:
        print(f"処理中: {site['name']}")
        entry, image_url = fetch_latest_entry(site["rss_url"])
        if entry:
            # 投稿済みチェック
            if not check_and_update_posted_articles(entry.link):
                continue  # 投稿済みならスキップ

            # 新しい記事の投稿
            status = f"{site['title']}\n{entry.title}\n{entry.link}"
            media_id = None
            if image_url:
                media_id = upload_media(image_url, site["mastodon_token"])  # 画像アップロード
            post_to_mastodon(status, site["mastodon_url"], site["mastodon_token"], media_id)


if __name__ == "__main__":
    main()

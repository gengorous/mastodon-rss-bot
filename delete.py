import time
from mastodon import Mastodon

# ここに自分のアクセストークンとインスタンスURLを入れる
ACCESS_TOKEN = "Nv-kRLghxYheOzFlDxamE9TPW0_EclFdqIxh1JtUke0"
INSTANCE_URL = "https://mstdn.jp"  # 自分のインスタンスのURL

# APIに接続
mastodon = Mastodon(access_token=ACCESS_TOKEN, api_base_url=INSTANCE_URL)

# 自分の投稿を取得して削除（5秒間隔）
def delete_all_toots():
    toots = mastodon.account_statuses(mastodon.me()['id'], limit=40)  # 40件ずつ取得
    while toots:
        for toot in toots:
            print(f"Deleting: {toot['id']}")
            mastodon.status_delete(toot['id'])
            time.sleep(5)  # 5秒待つ
        toots = mastodon.account_statuses(mastodon.me()['id'], limit=40)  # 次の40件を取得

delete_all_toots()
print("全部消したわよ。これでスッキリね！")

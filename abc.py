import os

GCS_CREDENTIALS = os.getenv("GCS_CREDENTIALS")

if not GCS_CREDENTIALS:
    print("❌ GCS_CREDENTIALS が設定されていません！")
else:
    print("✅ GCS_CREDENTIALS 読み込み成功！文字数:", len(GCS_CREDENTIALS))

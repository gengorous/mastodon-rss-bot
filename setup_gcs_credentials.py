import os
import base64
import json

# 環境変数から認証情報を取得
gcs_credentials = os.getenv("GCS_CREDENTIALS")
file_path = "/opt/render/project/src/service-account.json"

if not gcs_credentials:
    print("❌ GCS_CREDENTIALS が設定されていません")
    exit(1)

try:
    # デコードして JSON を取得
    decoded_credentials = base64.b64decode(gcs_credentials).decode("utf-8")
    credentials_info = json.loads(decoded_credentials)

    # JSON をファイルに保存
    with open(file_path, "w") as f:
        json.dump(credentials_info, f)
    
    print(f"✅ service-account.json を作成しました: {file_path}")

except Exception as e:
    print(f"❌ service-account.json の作成に失敗しました: {e}")
    exit(1)

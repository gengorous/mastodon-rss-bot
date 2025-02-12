from google.auth import default
from google.cloud import storage

creds, project = default()
print(f"認証成功！プロジェクト: {project}")
client = storage.Client(credentials=creds)
buckets = list(client.list_buckets())
print(f"バケット一覧: {buckets}")

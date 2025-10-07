# utils/gcs.py
import os
import uuid
from google.cloud import storage
from fastapi import UploadFile

GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
GCS_BUCKET_URL = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/"

_client = None
_bucket = None

def _get_bucket():
    global _client, _bucket
    # ✅ 필요할 때만 import & 생성 (시작 단계 크래시 방지)
    if _client is None:
        from google.cloud import storage
        _client = storage.Client()
    if _bucket is None:
        if not GCS_BUCKET_NAME:
            raise RuntimeError("GCS_BUCKET_NAME is not set")
        _bucket = _client.bucket(GCS_BUCKET_NAME)
    return _bucket


def upload_to_gcs(file: UploadFile, folder: str) -> str:
    """
    folder: "review/{사용자 아이디}/{공연장 id}"
    """
    bucket = _get_bucket()
    ext = file.filename.split(".")[-1]
    fname = f"{folder}/{uuid.uuid4().hex}.{ext}"
    blob = bucket.blob(fname)

    blob.upload_from_file(file.file, content_type=file.content_type)

    return f"{GCS_BUCKET_URL}{fname}"


def delete_from_gcs(file_url: str):
    """
    file_url: 업로드된 전체 URL
    """
    if not file_url.startswith(GCS_BUCKET_URL):
        return
    bucket = _get_bucket()
    file_path = file_url.replace(GCS_BUCKET_URL, "")
    blob = bucket.blob(file_path)

    if blob.exists():
        blob.delete()
        print(f"Deleted {file_path} from GCS.")
    else:
        print(f"{file_path} not found in GCS.")

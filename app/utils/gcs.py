# utils/gcs.py
import os
import uuid
from google.cloud import storage
from fastapi import UploadFile

GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
GCS_BUCKET_URL = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/"

client = storage.Client()
bucket = client.bucket(GCS_BUCKET_NAME)


def upload_to_gcs(file: UploadFile, folder: str) -> str:
    """
    folder: folder: "review/{사용자 아이디}/{공연장 id}"
    """
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
    
    file_path = file_url.replace(GCS_BUCKET_URL, "")
    blob = bucket.blob(file_path)

    if blob.exists():
        blob.delete()
        print(f"Deleted {file_path} from GCS.")
    else:
        print(f"{file_path} not found in GCS.")
"""File storage service: resumes / offer attachments.

Design doc §14 calls for MinIO object storage. We expose a small backend-
agnostic interface and select the backend via `settings.STORAGE_BACKEND`:

- "local" (default): files on disk under `uploads/`, served via a download
  endpoint. Nothing depends on external infrastructure, so the default setup
  keeps working without MinIO running.
- "minio": objects in a MinIO bucket, downloaded via fresh presigned URLs
  (so stored URLs never expire). If MinIO is unreachable at startup we log a
  warning and transparently fall back to local storage.

Stored `resume_url` values are storage keys (e.g. `resumes/<uuid>.pdf`), not
direct URLs, so the download endpoint can generate a fresh presigned URL on
each access regardless of backend.
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from app.core.config import settings

UPLOAD_DIR = Path("uploads")


def _minio_client() -> Any:
    from minio import Minio  # local import: keeps tests/imports light

    return Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE,
    )


# Resolved once on first use: True only when the user asked for MinIO AND the
# server is actually reachable. Cached so we don't pay a network check per call.
_resolved: bool | None = None


def _use_minio() -> bool:
    global _resolved
    if _resolved is not None:
        return _resolved
    if settings.STORAGE_BACKEND != "minio":
        _resolved = False
        return False
    try:
        client = _minio_client()
        if not client.bucket_exists(settings.MINIO_BUCKET):
            client.make_bucket(settings.MINIO_BUCKET)
        _resolved = True
    except Exception as exc:  # noqa: BLE001 - any connection issue -> fallback
        import structlog

        structlog.get_logger().warning(
            "minio_unreachable_fallback_to_local", error=str(exc)
        )
        _resolved = False
    return _resolved


def save_upload(data: bytes, content_type: str, ext: str) -> str:
    """Persist an uploaded file and return its storage key."""
    key = f"resumes/{uuid.uuid4().hex}.{ext or 'bin'}"
    if _use_minio():
        from io import BytesIO

        client = _minio_client()
        client.put_object(
            settings.MINIO_BUCKET,
            key,
            BytesIO(data),
            length=len(data),
            content_type=content_type or "application/octet-stream",
        )
    else:
        path = UPLOAD_DIR / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return key


def serve_file(key: str) -> str:
    """Resolve a storage key to a directly-openable URL.

    Local backend: a path under the public `/uploads` static mount.
    MinIO backend: a fresh presigned GET URL (1h), so stored keys never go
    stale regardless of when the resume was uploaded.
    """
    if _use_minio():
        from datetime import timedelta

        client = _minio_client()
        return client.presigned_get_object(
            settings.MINIO_BUCKET, key, expires=timedelta(hours=1)
        )
    return f"/uploads/{key}"

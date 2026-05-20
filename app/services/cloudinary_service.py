"""Cloudinary upload wrapper.

Cloudinary is configured via the CLOUDINARY_URL env var:
  cloudinary://<api_key>:<api_secret>@<cloud_name>
"""
import base64
import os
import uuid
from typing import Optional

import cloudinary
import cloudinary.uploader
from fastapi import UploadFile


_configured = False


def _ensure_configured() -> None:
    global _configured
    if _configured:
        return
    url = os.getenv("CLOUDINARY_URL")
    if not url:
        raise RuntimeError(
            "CLOUDINARY_URL is not set. Add it to your .env / Render env vars."
        )
    # cloudinary.config() picks up CLOUDINARY_URL automatically when present.
    cloudinary.config(secure=True)
    _configured = True


def upload_file(upload_file: UploadFile, folder: str) -> dict:
    """Upload a FastAPI UploadFile to Cloudinary, return {url, public_id}."""
    _ensure_configured()
    upload_file.file.seek(0)
    public_id = f"{folder}/{uuid.uuid4().hex}"
    result = cloudinary.uploader.upload(
        upload_file.file,
        public_id=public_id,
        resource_type="image",
        overwrite=False,
    )
    return {"url": result["secure_url"], "public_id": result["public_id"]}


def upload_data_url(data_url: str, folder: str) -> dict:
    """Upload a base64 data-URL (e.g. signature PNG from canvas) to Cloudinary."""
    _ensure_configured()
    if not data_url.startswith("data:"):
        raise ValueError("Expected a data URL")
    public_id = f"{folder}/{uuid.uuid4().hex}"
    result = cloudinary.uploader.upload(
        data_url,
        public_id=public_id,
        resource_type="image",
        overwrite=False,
    )
    return {"url": result["secure_url"], "public_id": result["public_id"]}


def delete_by_public_id(public_id: str) -> None:
    _ensure_configured()
    try:
        cloudinary.uploader.destroy(public_id, resource_type="image")
    except Exception:
        # Deletion failures shouldn't block business operations.
        pass

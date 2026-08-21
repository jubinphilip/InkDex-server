import os
import uuid

import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()

CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

if not all([CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET]):
    raise RuntimeError("Cloudinary credentials are not set")

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True,
)


def upload_file(file_obj, filename: str) -> dict:

    extension = os.path.splitext(filename)[1]

    result = cloudinary.uploader.upload(
        file_obj,
        resource_type="raw",
        folder="documents",
        public_id=f"{uuid.uuid4()}{extension}",
    )

    return {
        "public_id": result["public_id"],
        "url": result["secure_url"],
    }


def delete_file(public_id: str) -> None:
    cloudinary.uploader.destroy(public_id, resource_type="raw")

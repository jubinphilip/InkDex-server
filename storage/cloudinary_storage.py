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

    # Note: Cloudinary treats PDFs as "image" type assets rather than "raw".
    # Using "image" allows direct viewing/embedding in browser frames on the frontend.
    # We do not include the extension in public_id for image types, as Cloudinary appends it automatically.
    result = cloudinary.uploader.upload(
        file_obj,
        resource_type="image",
        folder="documents",
        public_id=str(uuid.uuid4()),
    )

    return {
        "public_id": result["public_id"],
        "url": result["secure_url"],
    }



def delete_file(public_id: str) -> None:
    # Match resource_type="image" used during upload
    cloudinary.uploader.destroy(public_id, resource_type="image")



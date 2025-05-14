import os
import uuid

from fastapi import UploadFile, File, Depends, APIRouter, HTTPException, Request

from app.utils.auth import get_current_user
from app.db.db import db

router = APIRouter(prefix="/images", tags=["images"])

UPLOAD_DIR = "app/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/")
async def list_user_images(request: Request, username: str = Depends(get_current_user)):
    user = await db.fetchrow("SELECT id FROM users WHERE username = $1", username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_id = user["id"]

    rows = await db.fetch("SELECT filename FROM images WHERE user_id = $1", user_id)
    filenames = [r["filename"] for r in rows]

    base_url = str(request.base_url).rstrip("/")
    urls = [f"{base_url}/static/uploads/{name}" for name in filenames]

    return {"images": urls}


@router.post("/")
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    username: str = Depends(get_current_user),
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    user_query = "SELECT id FROM users WHERE username = $1"
    user = await db.fetchrow(user_query, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_id = user["id"]

    ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    insert_query = "INSERT INTO images (user_id, filename) VALUES ($1, $2)"
    await db.execute(insert_query, user_id, unique_name)

    base_url = str(request.base_url).rstrip("/")
    return {
        "msg": "Image uploaded",
        "filename": unique_name,
        "url": f"{base_url}/static/uploads/{unique_name}",
    }

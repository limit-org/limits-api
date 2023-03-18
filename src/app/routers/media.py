from fastapi import APIRouter, Form, UploadFile, HTTPException, File
from pydantic import BaseModel

from .functions.media.upload import uploadMedia
from .functions.media.serve import servemedia

router = APIRouter()


class Media(BaseModel):
    username:   str
    sessionkey: str


@router.post("/media/upload", tags=["media"], status_code=201)
async def upload_media(file: UploadFile = File(), username: str = Form(), sessionkey: str = Form()):
    # all allowed media types. (media is considered audio, video and images)
    allowed_audio_types = ["audio/aac", "audio/mpeg", "audio/ogg", "audio/opus", "audio/wav", "audio/webm"]
    allowed_video_types = ["video/webm", "video/mp4", "video/quicktime", "video/ogg"]
    # video/ogg is a .ogg file
    allowed_image_types = ["image/jpeg", "image/png", "image/webp"]
    allowed_types = allowed_audio_types + allowed_video_types + allowed_image_types

    if file.content_type in allowed_types:
        return await uploadMedia(file, username, sessionkey)
    else:
        return HTTPException(
            status_code=415,  # Unsupported Media Type
            detail={
                "error_code": "1",
                "error": "Invalid media format.",
                "UIMessage": "That media format isn't allowed.",
            }
        )


@router.get("/media/get/{contentid}", tags=["media"], status_code=200)
async def serve_media(contentid: int):
    return await servemedia(contentid)

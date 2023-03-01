from fastapi import APIRouter, Form, UploadFile, HTTPException, File
from pydantic import BaseModel
import time

from functions.media.upload import uploadMedia
from functions.media.servemedia import servemedia

router = APIRouter()


class Media(BaseModel):
    username:   str
    sessionkey: str


@router.post("/media/upload", tags=["media"])
async def upload_media(file: UploadFile = File(), username: str = Form(), sessionkey: str = Form()):
    time_task_started = time.time()

    # all allowed media types. (media is considered audio, video and images)
    allowed_audio_types = ["audio/aac", "audio/mpeg", "audio/ogg", "audio/opus", "audio/wav", "audio/webm"]
    allowed_video_types = ["video/webm", "video/mp4", "video/quicktime", "video/ogg"]
    # video/ogg is audio, but sometimes it's not????
    allowed_image_types = ["image/jpeg", "image/png", "image/webp"]
    allowed_types = allowed_audio_types + allowed_video_types + allowed_image_types

    if file.content_type in allowed_types:
        return await uploadMedia(file, username, sessionkey)
    else:
        time_task_took = time.time() - time_task_started
        return HTTPException(
            status_code=500,  # conflict http code
            detail={
                "error_code": "1",
                "error": "Invalid media format.",
                "UIMessage": "That media format isn't allowed.",
                "time_took": time_task_took
            }
        )


@router.get("/media/get/{contentid}", tags=["media"])
async def serve_media(contentid: int):
    return await servemedia(contentid)
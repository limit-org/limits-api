import time

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel

from functions.profilepic.serve import servepfp
from functions.profilepic.set import setpfp

router = APIRouter()


class profilepic(BaseModel):
    username: str
    sessionkey: str


@router.get('/profilepic/get/{username}', tags=["profilepic"])
async def serveprofilepic(size: int, username: str):
    return await servepfp(username, size)


@router.post('/profilepic/set/', tags=["profilepic"])
async def setprofilepic(file: UploadFile = File(), username: str = Form(), sessionkey: str = Form()):
    time_task_started = time.time()

    # check if it's an image file
    allowed_image_types = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type in allowed_image_types:
        return await setpfp(file, username, sessionkey)

    else:
        time_task_took = time.time() - time_task_started
        return HTTPException(
            status_code=500,
            detail={
                "error_code": "1",
                "error": "Invalid media format.",
                "UIMessage": "That media format isn't supported for profile pictures.",
                "time_took": time_task_took
            }
        )

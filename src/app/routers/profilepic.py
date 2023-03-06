import time

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel

from functions.profilepic.serve import servepfp
from functions.profilepic.set import setpfp
from functions.profilepic.set import removepfp

router = APIRouter()


class profilepic(BaseModel):
    username: str
    sessionkey: str


@router.get('/profilepic/get/{username}', tags=["profilepic"], status_code=200)
async def serveprofilepic(size: int, username):
    return await servepfp(str(username), size)


@router.post('/profilepic/set/', tags=["profilepic"], status_code=201)
async def setprofilepic(file: UploadFile = File(), username: str = Form(), sessionkey: str = Form()):
    time_task_started = time.time()

    # check if it's an allowed image type
    allowed_image_types = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type in allowed_image_types:
        return await setpfp(file, username, sessionkey)

    else:
        time_task_took = time.time() - time_task_started
        return HTTPException(
            status_code=415,  # Unsupported Media Type
            detail={
                "error_code": "1",
                "error": "Invalid media format.",
                "UIMessage": "That media format isn't supported for profile pictures.",
                "time_took": time_task_took
            }
        )


@router.delete('/profilepic/remove/', tags=["profilepic"], status_code=200)
async def removeprofilepic(username: str = Form(), sessionkey: str = Form()):
    return await removepfp(username, sessionkey)

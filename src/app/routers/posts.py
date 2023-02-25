import time

from fastapi import APIRouter
from fastapi import Form
from pydantic import BaseModel

from functions.posting.create import makepost


class Post(BaseModel):
    username:      str
    sessionkey:    str
    postcontent:   str
    attachedmedia: str
    posttopic:     str


router = APIRouter()


@router.post('/posts/create', tags=["posts"])
async def createpost(username: str = Form(), sessionkey: str = Form(),
                     postcontent: str = Form(), attachedmedia: str = Form(), posttopic: str = Form()):
    time_task_started = time.time()
    post_topics = ["meta", "general", "hacking", "privacy"]  # ADD MORE

    if posttopic not in post_topics:
        time_task_took = time.time() - time_task_started
        return {
            "detail": {
                "APImessage": "failure",
                "error": "Invalid post topic.",
                "UIMessage": "Invalid post topic.",
                "username": username,
                "attempt_time": int(str(time.time()).split(".")[0]),
            },
            "time_took": time_task_took,
            "error_code": 0
        }
    if posttopic == "meta":
        if username != "announcements":
            time_task_took = time.time() - time_task_started
            return {
                "detail": {
                    "APImessage": "failure",
                    "error": "Invalid post topic.",
                    "UIMessage": "You're not allowed to post in this topic.",
                    "username": username,
                    "attempt_time": int(str(time.time()).split(".")[0]),
                },
                "time_took": time_task_took,
                "error_code": 0
            }
    else:
        return await makepost(postcontent, attachedmedia, posttopic, username, sessionkey)
